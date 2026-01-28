from django.http import JsonResponse

from django_nepkit.utils import (
    get_districts_by_province,
    get_municipalities_by_district,
)


def district_list_view(request):
    province = request.GET.get("province")
    if not province:
        return JsonResponse([], safe=False)
    data = get_districts_by_province(province)
    return JsonResponse(data, safe=False)


def municipality_list_view(request):
    district = request.GET.get("district")
    if not district:
        return JsonResponse([], safe=False)
    data = get_municipalities_by_district(district)
    return JsonResponse(data, safe=False)
