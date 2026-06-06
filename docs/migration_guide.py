"""
Data-migration recipe for moving an existing AD (``models.DateField``)
column to BS (``NepaliDateField``).

This file is a *template*, not a runnable migration: it shows the
correct shape, the safe defaults, and the gotchas to look out for.
Drop it into your app's ``migrations/`` directory, fill in the
``APP_LABEL`` / ``MODEL_NAME`` / field names, then ``makemigrations``
will pick up the ``Migration`` class at the bottom.

What v0.2.2 changed for migrations
----------------------------------
- ``NepaliDateField`` / ``NepaliDateTimeField`` store ``VARCHAR``
  values formatted with ``nepkit_settings.BS_DATE_FORMAT`` /
  ``BS_DATETIME_FORMAT`` (default ``"%Y-%m-%d"`` /
  ``"%Y-%m-%d %H:%M:%S"``).  A migration that writes a different
  format will sort and ``startswith``-filter incorrectly, so the
  recipe below honours the live setting.
- ``BaseNepaliBSField.to_python`` / ``get_prep_value`` raise
  ``ValidationError`` on bad input, so the conversion must produce
  valid ``nepalidate`` / ``nepalidatetime`` objects before they
  reach the model.
- The framework-agnostic ``django_nepkit.api`` helpers are the
  recommended way to do read-side conversion; ``nepalidate.from_date``
  is still available for one-off scripts but is no longer the only
  path.
"""

from __future__ import annotations

import datetime
import logging

from django.db import migrations
from django.utils import timezone
from django.utils.functional import LazyObject
from nepali.datetime import nepalidate, nepalidatetime

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Settings (filled in at runtime, not at import time)
# ---------------------------------------------------------------------------


class _NepkitSettingsProxy(LazyObject):
    """Defer the ``django_nepkit.conf`` import until first access.

    Importing ``django_nepkit.conf`` at module level pulls in Django
    settings machinery, which is fine inside a real migration but
    trips up linters and unit tests that collect this file in
    isolation.
    """

    def _setup(self):
        from django_nepkit.conf import nepkit_settings

        self._wrapped = nepkit_settings


nepkit_settings = _NepkitSettingsProxy()


# ---------------------------------------------------------------------------
# Configuration — EDIT THESE FOR YOUR MODEL
# ---------------------------------------------------------------------------

APP_LABEL = "YourApp"  # e.g. "accounts"
MODEL_NAME = "YourModel"  # e.g. "Profile"
SOURCE_FIELD = "birth_date_ad"  # the existing ``DateField`` / ``DateTimeField``
TARGET_FIELD = "birth_date"  # the new ``NepaliDateField`` / ``NepaliDateTimeField``

# Pagination for large tables; the admin may be running this against
# millions of rows.  ``iterator(chunk_size=...)`` keeps memory flat.
CHUNK_SIZE = 500

# Conversion errors that we *expect* (e.g. Naive/aware mismatches, an
# out-of-range date).  Anything outside this list surfaces to the
# operator so we don't silently skip real bugs.
_CONVERSION_ERRORS = (
    ValueError,
    TypeError,
    OverflowError,
    OSError,  # e.g. value out of range for ``datetime``
    AttributeError,  # a ``None``/missing sub-attribute
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ad_to_bs_date(value):
    """Convert a Python ``date`` to a ``nepalidate`` honouring the project
    ``TIME_ZONE`` setting (the model's ``_convert_from_python`` does
    the same on save).
    """
    if isinstance(value, datetime.datetime):
        if timezone.is_aware(value):
            value = timezone.localtime(value)
        value = value.date()
    return nepalidate.from_date(value)


def _ad_to_bs_datetime(value):
    """Convert a Python ``datetime`` to a ``nepalidatetime``."""
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    elif value is not None:
        # Migrations run with ``USE_TZ=True`` by default; an unaware
        # value in such a project is almost always a bug, so flag it
        # explicitly rather than guessing.
        logger.warning(
            "convert_ad_to_bs: %s.%s has a naive datetime on a "
            "USE_TZ=True project — treating as UTC.",
            MODEL_NAME,
            SOURCE_FIELD,
        )
        value = timezone.make_aware(value, datetime.timezone.utc)
    return nepalidatetime.from_datetime(value)


# ---------------------------------------------------------------------------
# Migration data callbacks
# ---------------------------------------------------------------------------


def convert_ad_to_bs(apps, schema_editor):
    """Bulk-convert every row's ``SOURCE_FIELD`` into a BS string on
    ``TARGET_FIELD``.

    Skips rows whose ``SOURCE_FIELD`` is empty.  Logs (does not
    silently swallow) unexpected exceptions per row so a single bad
    record can't take the whole migration down.
    """
    MyModel = apps.get_model(APP_LABEL, MODEL_NAME)
    fmt = nepkit_settings.BS_DATE_FORMAT  # honour the project setting

    qs = MyModel.objects.all().iterator(chunk_size=CHUNK_SIZE)
    converted = skipped = failed = 0

    for obj in qs:
        ad_value = getattr(obj, SOURCE_FIELD, None)
        if ad_value in (None, ""):
            skipped += 1
            continue

        try:
            bs_date = _ad_to_bs_date(ad_value)
            setattr(obj, TARGET_FIELD, bs_date.strftime(fmt))
            obj.save(update_fields=[TARGET_FIELD])
            converted += 1
        except _CONVERSION_ERRORS as exc:
            failed += 1
            logger.error(
                "convert_ad_to_bs: %s pk=%s value=%r: %s",
                MODEL_NAME,
                obj.pk,
                ad_value,
                exc,
            )

    logger.info(
        "convert_ad_to_bs done: converted=%d skipped=%d failed=%d",
        converted,
        skipped,
        failed,
    )


def reverse_bs_to_ad(apps, schema_editor):
    """Reverse the migration by converting BS strings back to AD ``date``
    objects via ``nepalidatetime.to_datetime`` / ``nepalidate.to_date``.
    """
    MyModel = apps.get_model(APP_LABEL, MODEL_NAME)

    converted = skipped = failed = 0
    for obj in MyModel.objects.all().iterator(chunk_size=CHUNK_SIZE):
        bs_value = getattr(obj, TARGET_FIELD, None)
        if bs_value in (None, ""):
            skipped += 1
            continue
        try:
            parsed = nepalidatetime.strptime(bs_value, nepkit_settings.BS_DATE_FORMAT)
            # ``nepalidate`` and ``nepalidatetime`` both expose ``to_date`` /
            # ``to_datetime`` for round-tripping.  Pick the one your
            # ``SOURCE_FIELD`` was.
            if hasattr(parsed, "to_date"):
                ad_value = parsed.to_date()
            else:
                ad_value = parsed
            setattr(obj, SOURCE_FIELD, ad_value)
            obj.save(update_fields=[SOURCE_FIELD])
            converted += 1
        except _CONVERSION_ERRORS as exc:
            failed += 1
            logger.error(
                "reverse_bs_to_ad: %s pk=%s value=%r: %s",
                MODEL_NAME,
                obj.pk,
                bs_value,
                exc,
            )

    logger.info(
        "reverse_bs_to_ad done: converted=%d skipped=%d failed=%d",
        converted,
        skipped,
        failed,
    )


# ---------------------------------------------------------------------------
# The migration class — ``makemigrations`` will reformat this on first run.
# ---------------------------------------------------------------------------


class Migration(migrations.Migration):
    """Convert ``YourModel.birth_date_ad`` → ``YourModel.birth_date``.

    Steps when you wire this up for real:

    1. Add ``birth_date = NepaliDateField(null=True, blank=True)`` to
       the model and run ``makemigrations`` — that produces the
       ``AddField`` operation below.
    2. Drop *this* file into ``YourApp/migrations/`` (renamed to
       ``<seq>_convert_dates.py``) and ``makemigrations`` again so
       Django sees the new ``Migration`` class.
    3. Once the migration has run on production, remove the
       ``birth_date_ad`` field with a follow-up migration.
    """

    dependencies = [
        ("YourApp", "previous_migration_name"),
    ]

    operations = [
        # 1. Add the new BS field as nullable so the RunPython below
        #    can back-fill it without violating NOT NULL constraints.
        #
        # migrations.AddField(
        #     model_name="yourmodel",
        #     name="birth_date",
        #     field=django_nepkit.models.NepaliDateField(
        #         null=True, blank=True,
        #     ),
        # ),
        # 2. Back-fill from the AD source column.
        migrations.RunPython(convert_ad_to_bs, reverse_code=reverse_bs_to_ad),
        # 3. Drop the old AD field (separate migration, after this one
        #    has run on production and you've verified the data).
    ]
