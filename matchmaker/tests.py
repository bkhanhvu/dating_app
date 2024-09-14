from django.test import TestCase
from django.urls import reverse
from .models import Profile, Match

class ProfileModelTest(TestCase):
    def setUp(self):
        # Create profiles for testing
        self.profile1 = Profile.objects.create(
            name="John Doe",
            age=30,
            gender="M",
            relationship_status="S",
            looking_for="LT",
            settle_timeline=24,
            occupation="Software Engineer",
            interests="Reading, Hiking, Movies"
        )

        self.profile2 = Profile.objects.create(
            name="Jane Smith",
            age=28,
            gender="F",
            relationship_status="S",
            looking_for="LT",
            settle_timeline=12,
            occupation="Designer",
            interests="Art, Traveling, Cooking"
        )

    def test_profile_creation(self):
        # Test that the profile is created correctly
        self.assertEqual(self.profile1.name, "John Doe")
        self.assertEqual(self.profile2.occupation, "Designer")
        self.assertEqual(Profile.objects.count(), 2)

    def test_profile_string_representation(self):
        # Test the string representation of a profile
        self.assertEqual(str(self.profile1), "John Doe (30)")
    
    def test_match_creation(self):
        # Create a match between the two profiles
        match = Match.objects.create(
            profile1=self.profile1,
            profile2=self.profile2,
            compatibility_score=85.5,
            reason="Both enjoy outdoor activities and have similar values."
        )
        self.assertEqual(Match.objects.count(), 1)
        self.assertEqual(match.compatibility_score, 85.5)

class MatchModelTest(TestCase):
    def setUp(self):
        self.profile1 = Profile.objects.create(
            name="John Doe",
            age=30,
            gender="M",
            relationship_status="S",
            looking_for="LT",
            settle_timeline=24,
            occupation="Software Engineer",
            interests="Reading, Hiking"
        )
        self.profile2 = Profile.objects.create(
            name="Jane Smith",
            age=28,
            gender="F",
            relationship_status="S",
            looking_for="LT",
            settle_timeline=12,
            occupation="Designer",
            interests="Art, Traveling"
        )
        self.match = Match.objects.create(
            profile1=self.profile1,
            profile2=self.profile2,
            compatibility_score=80.0,
            reason="Both enjoy traveling and have similar long-term goals."
        )

    def test_match_creation(self):
        # Test if the match is correctly created
        self.assertEqual(self.match.profile1.name, "John Doe")
        self.assertEqual(self.match.profile2.name, "Jane Smith")
        self.assertEqual(self.match.compatibility_score, 80.0)

    def test_match_string_representation(self):
        # Test string representation of match
        self.assertEqual(str(self.match), "Match between John Doe and Jane Smith")

class ProfileViewTest(TestCase):
    def setUp(self):
        # Create a profile for testing
        self.profile = Profile.objects.create(
            name="John Doe",
            age=30,
            gender="M",
            relationship_status="S",
            looking_for="LT",
            settle_timeline=24,
            occupation="Software Engineer",
            interests="Reading, Hiking"
        )

    def test_profile_create_view(self):
        # Test the profile creation view
        response = self.client.get(reverse('profile_create'))
        self.assertEqual(response.status_code, 200)  # Check if the page loads
        self.assertTemplateUsed(response, '/Users/khanhvu/Documents/fullstack/dating_app/matchmaker/templates/profile_form.html')  # Check if the correct template is used
    
    def test_matches_list_view(self):
        # Test the matches list view
        response = self.client.get(reverse('matches_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, '/Users/khanhvu/Documents/fullstack/dating_app/matchmaker/templates/matches_list.html')
        self.assertContains(response, "John Doe")  # Check if the response contains profile data

class MatchViewTest(TestCase):
    def setUp(self):
        self.profile1 = Profile.objects.create(
            name="John Doe",
            age=30,
            gender="M",
            relationship_status="S",
            looking_for="LT",
            settle_timeline=24,
            occupation="Software Engineer",
            interests="Reading, Hiking"
        )
        self.profile2 = Profile.objects.create(
            name="Jane Smith",
            age=28,
            gender="F",
            relationship_status="S",
            looking_for="LT",
            settle_timeline=12,
            occupation="Designer",
            interests="Art, Traveling"
        )
    
    def test_generate_matches(self):
        # Create match using the view and verify match creation
        response = self.client.get(reverse('matches_list'))
        # print response.content  # Uncomment to print response content for debugging
        print(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
        self.assertContains(response, "Jane Smith")

def test_profile_post(self):
    form_data = {
        'name': 'Alice Doe',
        'age': 29,
        'gender': 'F',
        'relationship_status': 'S',
        'looking_for': 'LT',
        'settle_timeline': 18,
        'occupation': 'Architect',
        'interests': 'Reading, Traveling'
    }
    response = self.client.post(reverse('profile_create'), data=form_data)
    self.assertEqual(response.status_code, 302)  # Should redirect after form submission
    self.assertEqual(Profile.objects.count(), 1)

from .utils import generate_matches

class MatchGenerationTest(TestCase):
    def setUp(self):
        self.profile1 = Profile.objects.create(
            name="John Doe",
            age=30,
            gender="M",
            relationship_status="S",
            looking_for="LT",
            settle_timeline=24,
            occupation="Software Engineer",
            interests="Reading, Hiking"
        )
        self.profile2 = Profile.objects.create(
            name="Jane Smith",
            age=28,
            gender="F",
            relationship_status="S",
            looking_for="LT",
            settle_timeline=12,
            occupation="Designer",
            interests="Art, Traveling"
        )
    
    def test_generate_matches(self):
        # Test the match generation utility
        num_matches = generate_matches()
        self.assertEqual(num_matches, 1)
        self.assertEqual(Match.objects.count(), 1)

