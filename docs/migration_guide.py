from django.db import migrations
from nepali.datetime import nepalidate


def convert_ad_to_bs(apps, schema_editor):
    """Logic to convert English (AD) dates to Nepali (BS)."""
    # Set your app and model name here
    MyModel = apps.get_model("YourApp", "YourModel")

    # Loop through all records and update them
    for obj in MyModel.objects.all():
        # Name of your old and new fields
        if obj.birth_date_ad:
            try:
                # Turn English date into Nepali date
                bs_date = nepalidate.from_date(obj.birth_date_ad)
                # Format the date correctly for the database
                obj.birth_date = bs_date.strftime("%Y-%m-%d")
                obj.save(update_fields=["birth_date"])
            except Exception as e:
                print(f"Error converting object {obj.pk}: {e}")


def reverse_bs_to_ad(apps, schema_editor):
    """Optional: Logic to convert back to English dates."""
    # Note: BS to AD conversion is also supported by the 'nepali' library.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("YourApp", "previous_migration_name"),
    ]

    operations = [
        # 1. Add the new field
        # migrations.AddField(
        #     model_name='yourmodel',
        #     name='birth_date',
        #     field=django_nepkit.models.NepaliDateField(null=True, blank=True),
        # ),
        # 2. Run the conversion
        migrations.RunPython(convert_ad_to_bs, reverse_code=reverse_bs_to_ad),
        # 3. Clean up the old field
    ]
