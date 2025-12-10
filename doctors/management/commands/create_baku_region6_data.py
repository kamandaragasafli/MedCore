"""
Management command to create:
- Region: "Baku Region 6"
- One hospital in that region
- 30 doctors assigned to that region and hospital

By default this runs for ALL tenant company databases (multi-tenant setup),
similar to `populate_test_doctors` and `populate_all_tenants_regions`.
"""

from django.core.management.base import BaseCommand

from subscription.models import Company
from subscription.db_router import set_tenant_db, clear_tenant_db

from regions.models import Region, City, Clinic
from doctors.models import Doctor


class Command(BaseCommand):
    help = 'Create "Baku Region 6", a hospital in that region, and 30 doctors assigned to it (for all tenant databases).'

    REGION_NAME = "Baku Region 6"
    REGION_CODE = "BAK6"
    CITY_NAME = "Baku Region 6 City"
    CLINIC_NAME = "Baku Region 6 Hospital"

    def handle(self, *args, **options):
        import sys

        # Ensure UTF-8 output for Windows terminals
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            # Not critical; continue with default encoding
            pass

        companies = Company.objects.all()

        if not companies.exists():
            self.stdout.write(self.style.ERROR("No companies found!"))
            return

        self.stdout.write(self.style.SUCCESS(f"Found {companies.count()} companies\n"))

        total_doctors_created = 0

        for company in companies:
            if not company.db_name:
                self.stdout.write(
                    self.style.WARNING(f"Skipping {company.name} (no database configured)")
                )
                continue

            self.stdout.write(
                self.style.WARNING(
                    f"\n=== Creating Baku Region 6 data for {company.name} ({company.db_name}) ==="
                )
            )

            # Switch to tenant database
            set_tenant_db(company.db_name)

            try:
                created_count = self._create_region_hospital_and_doctors()
                total_doctors_created += created_count
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  [OK] Created {created_count} doctors for {company.name}"
                    )
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Error: {str(e)}"))
                import traceback

                traceback.print_exc()
            finally:
                clear_tenant_db()

        self.stdout.write(
            self.style.SUCCESS(
                f"\n[SUCCESS] Finished creating Baku Region 6 data. Total doctors created: {total_doctors_created}"
            )
        )

    def _create_region_hospital_and_doctors(self) -> int:
        """
        Create the region, city, hospital clinic, and up to 30 doctors.
        Returns the number of doctors created in this tenant DB.

        Idempotent behavior:
        - If region/city/clinic already exist, they are reused.
        - If there are already >= 30 doctors in this region, no new doctors are added.
        """

        # 1) Create/get Region
        region, region_created = Region.objects.get_or_create(
            code=self.REGION_CODE,
            defaults={"name": self.REGION_NAME},
        )

        if region_created:
            self.stdout.write(
                self.style.SUCCESS(f'  [+] Created region: "{region.name}" ({region.code})')
            )
        else:
            self.stdout.write(
                f'  [=] Region already exists: "{region.name}" ({region.code})'
            )

        # 2) Create/get City for that region
        city, city_created = City.objects.get_or_create(
            name=self.CITY_NAME,
            region=region,
        )

        if city_created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'  [+] Created city: "{city.name}" for region "{region.name}"'
                )
            )
        else:
            self.stdout.write(
                f'  [=] City already exists: "{city.name}" for region "{region.name}"'
            )

        # 3) Create/get Hospital clinic in that region/city
        clinic_defaults = {
            "region": region,
            "city": city,
            "address": "Baku Region 6 Main Street",
            "phone": "+994 12 600 0006",
            "type": "hospital",
        }

        clinic, clinic_created = Clinic.objects.get_or_create(
            name=self.CLINIC_NAME,
            defaults=clinic_defaults,
        )

        # If clinic already exists but is missing some fields (older data),
        # make sure critical relations are aligned with this region/city.
        if not clinic_created:
            updated = False
            if clinic.region != region:
                clinic.region = region
                updated = True
            if clinic.city != city:
                clinic.city = city
                updated = True
            if clinic.type != "hospital":
                clinic.type = "hospital"
                updated = True
            if updated:
                clinic.save()

        if clinic_created:
            self.stdout.write(
                self.style.SUCCESS(f'  [+] Created hospital: "{clinic.name}"')
            )
        else:
            self.stdout.write(f'  [=] Hospital already exists: "{clinic.name}"')

        # 4) Create up to 30 doctors assigned to this region & hospital
        existing_in_region = Doctor.objects.filter(region=region).count()
        remaining = max(0, 30 - existing_in_region)

        if remaining == 0:
            self.stdout.write(
                self.style.WARNING(
                    f"  [=] Region already has {existing_in_region} doctors. No new doctors created."
                )
            )
            return 0

        self.stdout.write(
            self.style.WARNING(
                f"  Creating {remaining} doctors for region '{region.name}' (currently {existing_in_region}/30)..."
            )
        )

        doctors_created = 0

        for i in range(remaining):
            sequence_number = existing_in_region + i + 1
            name = f"Baku Region 6 Doctor {sequence_number}"

            # Simple deterministic phone pattern
            phone = f"+994 50 600 {sequence_number:04d}"

            Doctor.objects.create(
                ad=name,
                telefon=phone,
                region=region,
                city=city,
                clinic=clinic,
            )

            doctors_created += 1

        return doctors_created


