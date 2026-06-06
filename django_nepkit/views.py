import logging

from django.http import HttpResponse, JsonResponse
from django.utils.html import format_html

from django_nepkit.conf import nepkit_settings
from django_nepkit.utils import (
    get_districts_by_province,
    get_municipalities_by_district,
)

logger = logging.getLogger(__name__)

# Accepted values for ``?ne=`` / ``?en=`` query params. Anything else is
# either treated as "not provided" (default) or, with ``strict=True``,
# rejected.
_TRUE_VALUES = {"true", "1", "yes", "on"}
_FALSE_VALUES = {"false", "0", "no", "off"}


def _coerce_bool(raw):
    """Validate a boolean query string value.

    Returns:
        ``True``/``False`` if the value is recognised, ``None`` otherwise.
    """
    if raw is None:
        return None
    lowered = raw.lower()
    if lowered in _TRUE_VALUES:
        return True
    if lowered in _FALSE_VALUES:
        return False
    return None


def _render_options(data, placeholder):
    """Render a list of location options as HTML.

    Each ``<option>`` is built with an explicit ``format_html`` call so
    that the attribute (``value="..."``) and the text node are
    individually escaped — a user-supplied data row that contains a
    ``"><script>`` payload can never smuggle markup into the rendered
    page, regardless of which slot it ends up in.  ``format_html_join``
    is intentionally avoided: the per-option ``format_html`` makes the
    escaping contract obvious at the call site and avoids the
    placeholder/value/template-coupling that ``format_html_join``
    forces when the template changes.
    """
    parts: list[str] = [format_html('<option value="">{0}</option>', placeholder or "")]
    for item in data or []:
        opt_id = (item.get("id") if isinstance(item, dict) else "") or ""
        opt_text = (item.get("text") if isinstance(item, dict) else "") or ""
        parts.append(format_html('<option value="{0}">{1}</option>', opt_id, opt_text))
    return HttpResponse("\n".join(parts), content_type="text/html")


def _get_primary_param(request, param_name, exclude_params=None):
    """
    Extract a parameter from ``request.GET``.

    The primary parameter is read first.  If it is not present, the helper
    falls back to the **single** remaining non-internal parameter — this
    is a soft contract that makes the chained-select endpoints
    friendlier to hand-written URLs (``?Bagmati``), but it is **not**
    used when the query string has multiple non-internal keys (which
    would make the result ambiguous).
    """
    from django_nepkit.constants import INTERNAL_PARAMS

    if exclude_params is None:
        exclude_params = INTERNAL_PARAMS

    value = request.GET.get(param_name)
    if value:
        return value

    non_internal = [
        (k, v)
        for k, v in request.GET.items()
        if k not in exclude_params and v and k != param_name
    ]
    if len(non_internal) == 1:
        return non_internal[0][1]
    return None


def _parse_language_params(request, strict=False):
    """
    Parse the ``?ne=`` / ``?en=`` query parameters.

    Args:
        request: Django request.
        strict: When ``True``, raise ``ValueError`` if the value is
            present but unrecognised (anything outside
            ``true|false|1|0|yes|no|on|off``).  When ``False`` (the
            default), unrecognised values fall back to the project
            default so existing integrations aren't broken.

    Returns:
        Tuple of ``(ne, en)`` booleans.
    """
    default_lang = nepkit_settings.DEFAULT_LANGUAGE

    ne_raw = request.GET.get("ne")
    en_raw = request.GET.get("en")

    ne_value = _coerce_bool(ne_raw)
    en_value = _coerce_bool(en_raw)

    if strict and ne_raw is not None and ne_value is None:
        raise ValueError(f"Invalid value for ?ne=: {ne_raw!r}")
    if strict and en_raw is not None and en_value is None:
        raise ValueError(f"Invalid value for ?en=: {en_raw!r}")

    if ne_value is None:
        ne_value = default_lang == "ne"
    if en_value is None:
        en_value = not ne_value

    return ne_value, en_value


def _should_return_html(request):
    """Decide whether to return HTML (for HTMX / direct include) or JSON."""
    if request.headers.get("HX-Request") == "true":
        return True
    return request.GET.get("html", "false").lower() == "true"


def _location_list_view(request, param_name, data_func, placeholders):
    """Generic handler for the province→district→municipality chain."""
    param_value = _get_primary_param(request, param_name)
    if not param_value:
        return JsonResponse([], safe=False)

    ne, en = _parse_language_params(request)
    as_html = _should_return_html(request)

    data = data_func(param_value, ne=ne, en=en)

    if as_html:
        placeholder = placeholders[0] if ne else placeholders[1]
        return _render_options(data, placeholder)
    return JsonResponse(data, safe=False)


def district_list_view(request):
    """Return districts for a given province."""
    from django_nepkit.constants import PLACEHOLDERS

    return _location_list_view(
        request,
        param_name="province",
        data_func=get_districts_by_province,
        placeholders=(PLACEHOLDERS["district"]["ne"], PLACEHOLDERS["district"]["en"]),
    )


def municipality_list_view(request):
    """Return municipalities for a given district."""
    from django_nepkit.constants import PLACEHOLDERS

    return _location_list_view(
        request,
        param_name="district",
        data_func=get_municipalities_by_district,
        placeholders=(
            PLACEHOLDERS["municipality"]["ne"],
            PLACEHOLDERS["municipality"]["en"],
        ),
    )
