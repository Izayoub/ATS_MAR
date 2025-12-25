# management/commands/migrate_skills_to_separate_fields.py
from django.core.management.base import BaseCommand
from recruitment.models import Candidate


class Command(BaseCommand):
    help = 'Migrate skills from skills_extracted to separate technical_skills and soft_skills fields'

    def handle(self, *args, **options):
        candidates = Candidate.objects.all()
        migrated_count = 0

        self.stdout.write("Starting skills migration...")

        for candidate in candidates:
            self.stdout.write(f"Processing candidate {candidate.id}: {candidate.full_name}")

            updated = False

            # Migrer depuis skills_extracted si nécessaire
            if candidate.skills_extracted and isinstance(candidate.skills_extracted, dict):

                # Migrer technical_skills
                if not candidate.technical_skills and 'technical_skills' in candidate.skills_extracted:
                    technical = candidate.skills_extracted['technical_skills']
                    if isinstance(technical, list):
                        candidate.technical_skills = technical
                        updated = True
                        self.stdout.write(f"  → Migrated {len(technical)} technical skills")

                # Migrer soft_skills
                if not candidate.soft_skills and 'soft_skills' in candidate.skills_extracted:
                    soft = candidate.skills_extracted['soft_skills']
                    if isinstance(soft, list):
                        candidate.soft_skills = soft
                        updated = True
                        self.stdout.write(f"  → Migrated {len(soft)} soft skills")

            # Si skills_extracted est une liste (ancien format)
            elif candidate.skills_extracted and isinstance(candidate.skills_extracted, list):
                if not candidate.technical_skills:
                    candidate.technical_skills = candidate.skills_extracted
                    updated = True
                    self.stdout.write(f"  → Migrated {len(candidate.skills_extracted)} skills as technical")

            # Initialiser les champs vides si nécessaire
            if not candidate.technical_skills:
                candidate.technical_skills = []
                updated = True

            if not candidate.soft_skills:
                candidate.soft_skills = []
                updated = True

            if updated:
                candidate.save()
                migrated_count += 1
                self.stdout.write(f"✓ Updated candidate {candidate.id}")
            else:
                self.stdout.write(f"- No changes needed for candidate {candidate.id}")

        self.stdout.write(
            self.style.SUCCESS(f'Successfully migrated {migrated_count} candidates')
        )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually doing it',
        )