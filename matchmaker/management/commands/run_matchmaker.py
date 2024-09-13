from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from matchmaker.models import Profile, Match
from matchmaker.utils import generate_matches, calculate_compatibility, generate_match_reason

class Command(BaseCommand):
    help = 'Runs the matchmaking algorithm for all profiles or a specific profile'

    def add_arguments(self, parser):
        # Add an optional 'name' argument to allow matching for a specific profile
        parser.add_argument('--name', type=str, help='Name of the profile to generate matches for (optional)')

    def handle(self, *args, **options):
        # Extract the 'name' argument from the command options
        name = options.get('name')

        if name:
            # If a name is provided, generate matches for that specific profile
            try:
                # Attempt to retrieve the profile with the given name (case-insensitive)
                profile = Profile.objects.get(name__iexact=name)
                
                # Generate matches for the found profile
                matches = self.generate_matches_for_profile(profile)
                
                # Display success message with the number of matches found
                self.stdout.write(self.style.SUCCESS(f'Generated {len(matches)} matches for {profile.name}'))
                
                # Display detailed information about each match
                self.display_matches(matches)
            except ObjectDoesNotExist:
                # If no profile is found with the given name, display an error message
                self.stdout.write(self.style.ERROR(f'No profile found with name: {name}'))
        else:
            # If no name is provided, generate matches for all profiles
            num_matches = generate_matches()
            self.stdout.write(self.style.SUCCESS(f'Successfully generated {num_matches} matches for all profiles'))

    def generate_matches_for_profile(self, profile):
        matches = []
        # Get all profiles except the one we're matching for
        all_profiles = Profile.objects.exclude(id=profile.id)

        for other_profile in all_profiles:
            # Calculate compatibility score between the two profiles
            compatibility_score = calculate_compatibility(profile, other_profile)
            
            # If the compatibility score is above the threshold (70 in this case)
            if compatibility_score >= 70:  # This threshold can be adjusted
                # Generate a reason for the match
                reason = generate_match_reason(profile, other_profile, compatibility_score)
                
                # Create and save a new Match object
                match = Match.objects.create(
                    profile1=profile,
                    profile2=other_profile,
                    compatibility_score=compatibility_score,
                    reason=reason
                )
                
                # Add the new match to our list of matches
                matches.append(match)

        return matches

    def display_matches(self, matches):
        # Iterate through all matches and display their details
        for match in matches:
            self.stdout.write(f"\nMatch with {match.profile2.name}:")
            self.stdout.write(f"Compatibility Score: {match.compatibility_score}")
            self.stdout.write(f"Reason: {match.reason}")
            self.stdout.write("-" * 50)  # Print a separator line for readability

# Usage examples:
# For all profiles: python manage.py run_matchmaker
# For a specific profile: python manage.py run_matchmaker --name "John Doe"