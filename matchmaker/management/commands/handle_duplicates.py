from django.core.management.base import BaseCommand
from matchmaker.models import Profile
from faker import Faker
import random
from collections import defaultdict

class Command(BaseCommand):
    help = 'Iterate through profiles and optionally randomize settle_timeline or handle duplicate names'

    def add_arguments(self, parser):
        # Add a flag to the command to enable randomizing the settle_timeline
        parser.add_argument(
            '--randomize-timeline',
            action='store_true',  # This flag does not take any value
            help='Randomize the settle_timeline field for all profiles and ignore duplicate name handling'
        )

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Fetch all profiles from the database
        profiles = Profile.objects.all()

        # If randomize-timeline flag is passed, skip name handling and randomize settle_timeline
        if kwargs['randomize_timeline']:
            # Randomize the settle_timeline for all profiles
            for profile in profiles:
                old_timeline = profile.settle_timeline
                profile.settle_timeline = random.randint(0, 60)
                profile.save()

                # Print the change for logging/debugging purposes
                self.stdout.write(self.style.SUCCESS(f'Updated {profile.id} - old timeline: {old_timeline}, new timeline: {profile.settle_timeline}'))

            self.stdout.write(self.style.SUCCESS('Timelines randomized successfully'))
            return  # Exit after handling the timeline randomization

        # If the flag is not passed, handle duplicate names
        name_count = defaultdict(int)

        # First pass: Count the occurrences of each name
        for profile in profiles:
            name_count[profile.name] += 1

        # Second pass: Check for duplicates and change the name if needed
        for profile in profiles:
            if name_count[profile.name] > 1:
                # Generate a unique name using Faker until we get a non-duplicate name
                new_name = fake.name()
                while Profile.objects.filter(name=new_name).exists():
                    new_name = fake.name()

                # Update the profile with the new name
                old_name = profile.name
                profile.name = new_name
                profile.save()

                # Print the change for logging/debugging purposes
                self.stdout.write(self.style.SUCCESS(f'Updated {profile.id} - old name: {old_name}, new name: {new_name}'))

        self.stdout.write(self.style.SUCCESS('Duplicate names handled successfully'))

# python manage.py handle_duplicates --randomize-timeline