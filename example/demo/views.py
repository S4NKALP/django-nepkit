"""
Plain Django views for the demo.

The form-based views (``person_list`` / ``person_create`` / ``transaction_create``
/ ``address_normalize_demo``) use Django's built-in machinery. The JSON
endpoints under ``/api/`` use the framework-agnostic helpers in
``django_nepkit.api`` so this demo doesn't need DRF or django-filter.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from django import forms
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET

from django_nepkit import api as nepkit_api
from django_nepkit.conf import nepkit_settings
from django_nepkit.utils import normalize_address

from .models import AuditedPerson, Citizen, Person, Transaction


_TRUE_VALUES = {"true", "1", "yes", "on"}


# --------------------------------------------------------------------------- #
# Form-based views
# --------------------------------------------------------------------------- #


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = [
            "name",
            "birth_date",
            "birth_date_ne",
            "phone_number",
            "province",
            "province_ne",
            "district",
            "district_ne",
            "municipality",
            "municipality_ne",
        ]


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["title", "amount"]


def person_list(request: HttpRequest):
    persons = Person.objects.all()
    transactions = Transaction.objects.all()
    return render(
        request,
        "demo/person_list.html",
        {"persons": persons, "transactions": transactions},
    )


def person_create(request: HttpRequest):
    if request.method == "POST":
        form = PersonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("demo:person-list")
    else:
        form = PersonForm()
    return render(request, "demo/person_form.html", {"form": form})


def transaction_create(request: HttpRequest):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("demo:person-list")
    else:
        form = TransactionForm()
    return render(
        request, "demo/person_form.html", {"form": form, "title": "Add Transaction"}
    )


def address_normalize_demo(request: HttpRequest):
    address = request.GET.get("address", "")
    result = None
    if address:
        result = normalize_address(address)

    if request.headers.get("HX-Request") == "true":
        return render(
            request, "demo/address_normalize_partial.html", {"result": result}
        )

    return render(
        request,
        "demo/address_normalize.html",
        {"address": address, "result": result},
    )


# --------------------------------------------------------------------------- #
# Plain-Django JSON API (no DRF, no django-filter)
# --------------------------------------------------------------------------- #


def _bad_request(message: str, **extra) -> JsonResponse:
    payload = {"error": message}
    payload.update(extra)
    return JsonResponse(payload, status=400)


def _ne_flag(request: HttpRequest) -> bool:
    """Resolve the ``?ne=true`` flag for JSON endpoints.

    Falls back to the ``Accept-Language`` header before defaulting to the
    project setting so that consumers that send ``ne`` only on some
    requests still get a sensible answer.
    """
    raw = request.GET.get("ne")
    if raw is not None:
        return raw.lower() in _TRUE_VALUES
    accept = (request.headers.get("Accept-Language") or "").lower()
    if "ne" in accept:
        return True
    return nepkit_settings.DEFAULT_LANGUAGE == "ne"


def _strict_flag(request: HttpRequest) -> bool:
    """Resolve the ``?strict=1`` flag for JSON endpoints.

    When True, the demo's ``serialize_*`` calls raise on unparseable
    values instead of falling back to ``str(value)`` — useful for
    smoke-testing the strict paths the API exposes.
    """
    raw = request.GET.get("strict")
    if raw is None:
        return False
    return raw.lower() in _TRUE_VALUES


def _paginate(request: HttpRequest, queryset, per_page: int = 25):
    try:
        page_num = max(1, int(request.GET.get("page", 1)))
    except (TypeError, ValueError):
        page_num = 1
    paginator = Paginator(queryset, per_page)
    page = paginator.get_page(page_num)
    return page.object_list, {
        "page": page.number,
        "pages": paginator.num_pages,
        "per_page": per_page,
        "total": paginator.count,
    }


def _search(queryset, search_fields: list[str], term: str | None):
    if not term:
        return queryset
    q = Q()
    for field in search_fields:
        q |= Q(**{f"{field}__icontains": term})
    return queryset.filter(q)


def _apply_ordering(queryset, ordering_fields: list[str], order_param: str | None):
    """Apply ``?order=`` whitelist.

    Returns ``(queryset, error)``: the queryset is unchanged on error, and
    ``error`` is an :class:`HttpResponseBadRequest` if the value is
    malformed.
    """
    if not order_param:
        return queryset, None
    field = order_param.lstrip("-")
    if field not in ordering_fields:
        return (
            queryset,
            _bad_request(
                _("Invalid order field: %(field)s"),
                field=field,
                allowed=sorted(ordering_fields),
            ),
        )
    return queryset.order_by(order_param), None


def _year_month_filter(queryset, field_name: str, year: str | None, month: str | None):
    """Year/month substring filter, mirroring the default ``BS_DATE_FORMAT``."""
    fmt = nepkit_settings.BS_DATE_FORMAT
    if year:
        try:
            year_int = int(year)
        except (TypeError, ValueError):
            return queryset, _bad_request(_("Invalid year: %(value)s"), value=year)
        if fmt.startswith("%Y"):
            sep = fmt[2] if len(fmt) > 2 and not fmt[2].startswith("%") else "-"
            queryset = queryset.filter(
                **{f"{field_name}__startswith": f"{year_int}{sep}"}
            )
    if month:
        try:
            month_int = int(month)
        except (TypeError, ValueError):
            return queryset, _bad_request(_("Invalid month: %(value)s"), value=month)
        if not 1 <= month_int <= 12:
            return queryset, _bad_request(
                _("Month out of range: %(value)s"), value=month
            )
        month_str = f"{month_int:02d}"
        if fmt == "%Y-%m-%d":
            queryset = queryset.filter(**{f"{field_name}__contains": f"-{month_str}-"})
        else:
            sep = fmt[2] if len(fmt) > 2 and not fmt[2].startswith("%") else "-"
            queryset = queryset.filter(
                **{f"{field_name}__contains": f"{sep}{month_str}{sep}"}
            )
    return queryset, None


def _range_filter(queryset, field_name: str, raw: str | None, field_type: str = "auto"):
    """Filter by ``"min,max"`` / ``"min,"`` / ``",max"`` / ``"value"``.

    ``field_type`` is one of ``"auto"``, ``"decimal"``, ``"date"`` or
    ``"integer"`` and is used to validate user input before it reaches
    the ORM (so a stray string doesn't 500 the request).
    """
    if not raw:
        return queryset, None

    parts = [p.strip() for p in raw.split(",")]
    if len(parts) > 2:
        return queryset, _bad_request(
            _("Range must be one or two comma-separated values: %(value)s"),
            value=raw,
        )

    def _validate(value: str):
        if not value:
            return None
        if field_type == "decimal":
            try:
                return Decimal(value)
            except (InvalidOperation, ValueError):
                raise ValueError(value)
        if field_type == "integer":
            try:
                return int(value)
            except (TypeError, ValueError):
                raise ValueError(value)
        if field_type == "date":
            # Will be re-validated by the ORM; let it pass.
            return value
        # Auto: try decimal first, fall back to string.
        try:
            return Decimal(value)
        except (InvalidOperation, ValueError):
            return value

    try:
        if len(parts) == 1:
            v = _validate(parts[0])
            if v is None:
                return queryset, None
            return queryset.filter(**{field_name: v}), None
        lo, hi = parts
        lo_v = _validate(lo) if lo else None
        hi_v = _validate(hi) if hi else None
        if lo_v is not None and hi_v is not None:
            return queryset.filter(**{f"{field_name}__range": (lo_v, hi_v)}), None
        if lo_v is not None:
            return queryset.filter(**{f"{field_name}__gte": lo_v}), None
        if hi_v is not None:
            return queryset.filter(**{f"{field_name}__lte": hi_v}), None
        return queryset, None
    except ValueError as exc:
        return queryset, _bad_request(
            _("Invalid range value: %(value)s") % {"value": str(exc)}
        )


# ---- Person -----------------------------------------------------------------


@require_GET
def person_api(request: HttpRequest):
    qs = Person.objects.all()
    qs = _search(qs, ["name", "birth_date", "phone_number"], request.GET.get("q"))
    qs, err = _apply_ordering(
        qs, ["name", "birth_date", "created_at"], request.GET.get("order")
    )
    if err is not None:
        return err

    birth_date = request.GET.get("birth_date")
    if birth_date:
        qs = qs.filter(birth_date=birth_date)
    qs, err = _year_month_filter(
        qs, "birth_date", request.GET.get("year"), request.GET.get("month")
    )
    if err is not None:
        return err
    if request.GET.get("province"):
        qs = qs.filter(province=request.GET["province"])
    if request.GET.get("district"):
        qs = qs.filter(district=request.GET["district"])

    items, meta = _paginate(request, qs)
    ne = _ne_flag(request)
    strict = _strict_flag(request)
    payload = [_person_to_payload(p, ne=ne, strict=strict) for p in items]
    return JsonResponse({"results": payload, "meta": meta})


def _person_to_payload(
    person: Person, *, ne: bool, strict: bool = False
) -> dict[str, Any]:
    return nepkit_api.build_localized_payload(
        {
            "id": person.id,
            "name": person.name,
            "birth_date": nepkit_api.serialize_nepali_date(
                person.birth_date, ne=ne, strict=strict
            ),
            "phone_number": person.phone_number,
            "province": person.province,
            "district": person.district,
            "municipality": person.municipality,
            "created_at": nepkit_api.serialize_nepali_datetime(
                person.created_at, ne=ne, strict=strict
            ),
        },
        ne=ne,
    )


# ---- Citizen ----------------------------------------------------------------


@require_GET
def citizen_api(request: HttpRequest):
    qs = Citizen.objects.all()
    qs, err = _apply_ordering(
        qs, ["name", "province", "district"], request.GET.get("order")
    )
    if err is not None:
        return err
    items, meta = _paginate(request, qs)
    ne = _ne_flag(request)
    return JsonResponse(
        {
            "results": [
                nepkit_api.build_localized_payload(
                    {
                        "id": c.id,
                        "name": c.name,
                        "province": c.province,
                        "district": c.district,
                        "municipality": c.municipality,
                    },
                    ne=ne,
                )
                for c in items
            ],
            "meta": meta,
        }
    )


# ---- Audited person ---------------------------------------------------------


@require_GET
def audited_api(request: HttpRequest):
    qs = AuditedPerson.objects.all()
    qs = _search(qs, ["name", "birth_date"], request.GET.get("q"))
    qs, err = _apply_ordering(qs, ["name", "created_at"], request.GET.get("order"))
    if err is not None:
        return err
    items, meta = _paginate(request, qs)
    ne = _ne_flag(request)
    strict = _strict_flag(request)
    return JsonResponse(
        {
            "results": [
                nepkit_api.build_localized_payload(
                    {
                        "id": a.id,
                        "name": a.name,
                        "birth_date": nepkit_api.serialize_nepali_date(
                            a.birth_date, ne=ne, strict=strict
                        ),
                        "created_at": nepkit_api.serialize_nepali_datetime(
                            a.created_at, ne=ne, strict=strict
                        ),
                    },
                    ne=ne,
                )
                for a in items
            ],
            "meta": meta,
        }
    )


# ---- Transaction ------------------------------------------------------------


@require_GET
def transaction_api(request: HttpRequest):
    qs = Transaction.objects.all()
    qs = _search(qs, ["title", "amount", "date"], request.GET.get("q"))
    qs, err = _range_filter(
        qs, "amount", request.GET.get("amount_range"), field_type="decimal"
    )
    if err is not None:
        return err
    qs, err = _range_filter(
        qs, "date", request.GET.get("date_range"), field_type="date"
    )
    if err is not None:
        return err
    if request.GET.get("title"):
        qs = qs.filter(title=request.GET["title"])
    items, meta = _paginate(request, qs)
    ne = _ne_flag(request)
    strict = _strict_flag(request)
    return JsonResponse(
        {
            "results": [
                nepkit_api.build_localized_payload(
                    {
                        "id": t.id,
                        "title": t.title,
                        "amount": str(t.amount),
                        "amount_formatted": nepkit_api.serialize_nepali_currency(
                            t.amount, ne=ne
                        ),
                        "date": nepkit_api.serialize_nepali_date(
                            t.date, ne=ne, strict=strict
                        ),
                    },
                    ne=ne,
                )
                for t in items
            ],
            "meta": meta,
        }
    )
