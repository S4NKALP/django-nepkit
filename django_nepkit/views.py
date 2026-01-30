from django.http import JsonResponse

from django_nepkit.utils import (
    get_districts_by_province,
    get_municipalities_by_district,
)


def district_list_view(request):
    province = request.GET.get("province")
    if not province:
        return JsonResponse([], safe=False)

    # Check for ne/en parameters from request or widget data attributes
    ne = request.GET.get("ne", "false").lower() == "true"
    en = request.GET.get("en", "true").lower() == "true"

    data = get_districts_by_province(province, ne=ne, en=en)
    return JsonResponse(data, safe=False)


def municipality_list_view(request):
    district = request.GET.get("district")
    if not district:
        return JsonResponse([], safe=False)

    # Check for ne/en parameters from request or widget data attributes
    ne = request.GET.get("ne", "false").lower() == "true"
    en = request.GET.get("en", "true").lower() == "true"

    data = get_municipalities_by_district(district, ne=ne, en=en)
    return JsonResponse(data, safe=False)
