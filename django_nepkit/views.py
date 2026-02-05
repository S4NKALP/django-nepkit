from django.http import JsonResponse, HttpResponse

from django_nepkit.utils import (
    get_districts_by_province,
    get_municipalities_by_district,
)

from django_nepkit.conf import nepkit_settings


def _render_options(data, placeholder):
    """Internal helper to render list of options as HTML."""
    options = [f'<option value="">{placeholder}</option>']
    for item in data:
        options.append(f'<option value="{item["id"]}">{item["text"]}</option>')
    return HttpResponse("\n".join(options), content_type="text/html")


def _get_primary_param(request, param_name, exclude_params=None):
    """
    Extract a parameter from request.GET with fallback logic.

    Args:
        request: Django request object
        param_name: Primary parameter name to look for
        exclude_params: List of parameter names to exclude from fallback

    Returns:
        Parameter value or None
    """
    from django_nepkit.constants import INTERNAL_PARAMS

    if exclude_params is None:
        exclude_params = INTERNAL_PARAMS

    # Try primary parameter first
    value = request.GET.get(param_name)

    # Fallback: take the first non-internal parameter
    if not value:
        for key, val in request.GET.items():
            if key not in exclude_params and val:
                value = val
                break

    return value


def _parse_language_params(request):
    """
    Parse language parameters from request.

    Args:
        request: Django request object

    Returns:
        Tuple of (ne, en) boolean values
    """
    default_lang = nepkit_settings.DEFAULT_LANGUAGE
    ne_param = request.GET.get("ne")
    ne = ne_param.lower() == "true" if ne_param else default_lang == "ne"

    en_param = request.GET.get("en")
    en = en_param.lower() == "true" if en_param else not ne

    return ne, en


def _should_return_html(request):
    """
    Check if response should be HTML format.

    Args:
        request: Django request object

    Returns:
        Boolean indicating if HTML format is requested
    """
    return (
        request.GET.get("html", "false").lower() == "true"
        or request.headers.get("HX-Request") == "true"
    )


def _location_list_view(request, param_name, data_func, placeholders):
    """
    Generic view handler for location hierarchy endpoints.

    Args:
        request: Django request object
        param_name: Name of the primary parameter to extract
        data_func: Function to call to get location data
        placeholders: Tuple of (nepali_placeholder, english_placeholder)

    Returns:
        JsonResponse or HttpResponse with location data
    """
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
    """Return list of districts for a given province."""
    from django_nepkit.constants import PLACEHOLDERS

    return _location_list_view(
        request,
        param_name="province",
        data_func=get_districts_by_province,
        placeholders=(PLACEHOLDERS["district"]["ne"], PLACEHOLDERS["district"]["en"]),
    )


def municipality_list_view(request):
    """Return list of municipalities for a given district."""
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
