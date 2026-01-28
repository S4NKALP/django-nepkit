from nepali.locations import districts, provices


def get_districts_by_province(provice_name):
    selected_province = next((p for p in provices if p.name == provice_name), None)
    if not selected_province:
        return []
    return [{"id": d.name, "text": d.name} for d in selected_province.districts]


def get_municipalities_by_district(district_name):
    selected_district = next((d for d in districts if d.name == district_name), None)
    if not selected_district:
        return []
    return [{"id": m.name, "text": m.name} for m in selected_district.municipalities]
