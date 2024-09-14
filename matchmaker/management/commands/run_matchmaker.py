from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from matchmaker.models import Profile, Match
from matchmaker.utils import generate_matches, calculate_compatibility
import random

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

    def generate_matches_for_profile(self, profile: Profile):
        matches = []
        # Get all profiles except the one we're matching for
        all_profiles = Profile.objects.exclude(id=profile.id)
        
        # Get all profiles with the same looking_for and opposite gender
        opposite_gender = 'F' if profile.gender == 'M' else 'M'
        matching_profiles = Profile.objects.filter(looking_for=profile.looking_for, gender=opposite_gender)

        print(f"Number of matching profiles for {profile.name}: {len(matching_profiles)}")
        
        # # if more than 5 profiles, get random 5 profiles
        # if len(matching_profiles) > 5:
        #     matching_profiles = random.sample(list(matching_profiles), min(5, len(matching_profiles)))
        
        profile_count = 0
        for other_profile in matching_profiles:
            profile_count += 1
            # Calculate compatibility score between the two profiles
            compatibility_result = calculate_compatibility(profile, other_profile)
            
            # print Profile 2 Name,Total Score, Explanations
            # print profile 2 name,
            print("-" * 50)
            print(f"Match {profile_count}: {other_profile.name}\n\nTotal Score: {compatibility_result['total_score']}\n\nExplanation: {compatibility_result['explanation']}")
            print("-" * 50)

            if compatibility_result is None:
                continue
            total_score = compatibility_result['total_score']
            reason = compatibility_result['explanation']
            
            # If the compatibility score is above the threshold (70 in this case)
            if total_score >= 70:  # Adjust the threshold as needed
                # Create and save a new Match object
                match = Match.objects.create(
                    profile1=profile,
                    profile2=other_profile,
                    compatibility_score=total_score,
                    reason=reason
                )
                    
                # Add the new match to our list of matches
                matches.append(match)
                
                # Display match information to the user
                print("\nCongratulations!")
                print(f"You've been matched with {other_profile.name}!")
                print(f"Compatibility Score: {total_score}")
                print(f"Reason for match: {reason}")
                print(f"Profile 2: Age: {other_profile.age}, Gender: {other_profile.gender}, Occupation: {other_profile.occupation}")
                print("-" * 50)

                # Ask user if they want to continue (safe proof)
                while True:
                    user_input = input("Do you want to continue finding matches? (yes/no): ").strip().lower()
                    if user_input in ['yes', 'no']:
                        break  # Break the loop if input is valid
                    print("Invalid input! Please type 'yes' or 'no'.")

                if user_input == 'no':
                    print("Ending matchmaking process.")
                    return matches  # Stop the matching process if user says no


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
