from django.core.management.base import BaseCommand
from matchmaker.models import Profile
from matchmaker.utils import generate_random_profile
import random

GENDER_CHOICES = ['Male', 'Female']

class Command(BaseCommand):
    help = 'Populates the database with randomly generated profiles'

    def handle(self, *args, **kwargs):
        male_count = 0
        female_count = 0
        total_count = 2

        while male_count + female_count < total_count:
            gender = random.choice(GENDER_CHOICES)
            
            # logic to make sure we get even Male and Female
            if gender == 'Male' and (male_count /  total_count > 0.5):
                gender = 'Female'
            elif gender == 'Female' and (female_count /  total_count > 0.5):
                gender = 'Male'
            
            profile_data = generate_random_profile(gender)
            if profile_data:
                if profile_data['gender'] == 'M' and male_count < 200:
                    Profile.objects.create(**profile_data)
                    male_count += 1
                
                elif profile_data['gender'] == 'F' and female_count < 200:
                    Profile.objects.create(**profile_data)
                    female_count += 1

                if (male_count + female_count) % 10 == 0:
                    self.stdout.write(f"Created {male_count + female_count} profiles...")

        self.stdout.write(self.style.SUCCESS(f'Successfully created {male_count} male and {female_count} female profiles'))

# Usage: python manage.py populate_profiles