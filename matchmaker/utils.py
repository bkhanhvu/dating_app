import requests
import random
from django.conf import settings
from django.db.models import Q
from .models import Profile, Match

# Predefined options for certain profile attributes
PROFILE_OPTIONS = {
    'gender': ['Male', 'Female', 'Other'],
    'relationship_status': ['Single', 'Divorced', 'Widowed'],
    'looking_for': ['Long-term', 'Short-term', 'Friendship', 'Casual'],
}

# Set up OpenAI API key and endpoint
OPENAI_API_KEY = 'your_openai_api_key'
OPENAI_URL = 'https://api.openai.com/v1/completions'

def call_openai_api(prompt, max_tokens=150):
    """
    Call the OpenAI API using the requests library.
    
    Args:
    prompt (str): The text prompt for the OpenAI API.
    max_tokens (int): The maximum number of tokens in the response.
    
    Returns:
    str: The generated text from the OpenAI API, or None if an error occurs.
    """
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        'model': 'text-davinci-002',
        'prompt': prompt,
        'max_tokens': max_tokens
    }
    
    try:
        response = requests.post(OPENAI_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['text'].strip()
    except requests.exceptions.RequestException as e:
        print(f"Error calling OpenAI API: {e}")
        return None

def generate_random_profile():
    """
    Generate a random dating profile using OpenAI's GPT-3 via API call.
    
    Returns:
    dict: A dictionary containing profile attributes, or None if an error occurs.
    """
    prompt = """Generate a random dating profile with the following attributes:
    1. Full name
    2. Age (between 18 and 65)
    3. Occupation
    4. 3-5 interests or hobbies (comma-separated)
    5. Timeline to settle down (in months, between 0 and 60)

    Format the response as a Python dictionary with keys: name, age, occupation, interests, settle_timeline."""

    profile_text = call_openai_api(prompt, max_tokens=150)
    if not profile_text:
        return None

    try:
        profile_dict = eval(profile_text)
    except Exception as e:
        print(f"Error parsing generated profile: {e}")
        return None

    # Add randomly selected options for predefined fields
    profile_dict['gender'] = random.choice(PROFILE_OPTIONS['gender'])
    profile_dict['relationship_status'] = random.choice(PROFILE_OPTIONS['relationship_status'])
    profile_dict['looking_for'] = random.choice(PROFILE_OPTIONS['looking_for'])

    # Ensure correct data types and formats
    profile_dict['age'] = int(profile_dict['age'])
    profile_dict['settle_timeline'] = int(profile_dict['settle_timeline'])
    profile_dict['gender'] = profile_dict['gender'][0].upper()
    profile_dict['relationship_status'] = profile_dict['relationship_status'][0].upper()
    profile_dict['looking_for'] = profile_dict['looking_for'][:2].upper()

    return profile_dict

def calculate_compatibility(profile1: Profile, profile2: Profile):
    """
    Calculate the compatibility score between two profiles.
    
    Args:
    profile1 (Profile): The first profile to compare.
    profile2 (Profile): The second profile to compare.
    
    Returns:
    int: A compatibility score between 0 and 100.
    """
    score = 0
    
    # Basic Criteria (50 points total)
    
    # Looking For (15 points)
    if profile1.looking_for == profile2.looking_for:
        score += 15
    elif (profile1.looking_for in ['LT', 'ST'] and profile2.looking_for in ['LT', 'ST']) or \
         (profile1.looking_for in ['F', 'C'] and profile2.looking_for in ['F', 'C']):
        score += 7  # Partial match

    # Settle Timeline (10 points)
    timeline_diff = abs(profile1.settle_timeline - profile2.settle_timeline)
    if timeline_diff == 0:
        score += 10
    elif timeline_diff <= 6:
        score += 8
    elif timeline_diff <= 12:
        score += 5
    elif timeline_diff <= 24:
        score += 2

    # Age Difference (10 points)
    age_diff = abs(profile1.age - profile2.age)
    if age_diff <= 2:
        score += 10
    elif age_diff <= 5:
        score += 8
    elif age_diff <= 10:
        score += 5
    elif age_diff <= 15:
        score += 2

    # Relationship Status (5 points)
    if profile1.relationship_status == profile2.relationship_status:
        score += 5

    # AI-based Criteria (50 points total)
    ai_score = get_ai_compatibility_score(profile1, profile2)
    score += ai_score

    return min(score, 100)  # Ensure the score doesn't exceed 100

def get_ai_compatibility_score(profile1: Profile, profile2: Profile):
    """
    Get an AI-generated compatibility score for two profiles via API call.
    
    Args:
    profile1 (Profile): The first profile to compare.
    profile2 (Profile): The second profile to compare.
    
    Returns:
    int: An AI-generated compatibility score between 0 and 50.
    """
    prompt = f"""Analyze the compatibility of these two dating profiles and provide scores for different aspects. 
    The total score should add up to 50 points.

    Profile 1: {profile1.name}, {profile1.age}, {profile1.occupation}, interested in {profile1.interests}, 
    looking for {profile1.get_looking_for_display()}, timeline to settle: {profile1.settle_timeline} months

    Profile 2: {profile2.name}, {profile2.age}, {profile2.occupation}, interested in {profile2.interests}, 
    looking for {profile2.get_looking_for_display()}, timeline to settle: {profile2.settle_timeline} months

    Provide your response in the following format:
    Occupation: [score]
    Interests: [score]
    Names: [score]
    Personality: [score]
    Total: [sum of all scores]
    Explanation: [Brief explanation of your scoring]
    """
    
    analysis = call_openai_api(prompt, max_tokens=200)
    if not analysis:
        return 0
    
    try:
        lines = analysis.split('\n')
        for line in lines:
            if line.startswith('Total:'):
                return int(line.split(':')[1].strip())
    except Exception as e:
        print(f"Error parsing AI compatibility score: {e}")
    
    return 0

def generate_match_reason(profile1: Profile, profile2: Profile, compatibility_score):
    """
    Generate a personalized reason for why two profiles were matched via OpenAI API call.
    
    Args:
    profile1 (Profile): The first profile in the match.
    profile2 (Profile): The second profile in the match.
    compatibility_score (int): The calculated compatibility score.
    
    Returns:
    str: A brief explanation of why the profiles were matched.
    """
    prompt = f"""Generate a brief, friendly explanation for why {profile1.name} and {profile2.name} were matched.
    Their compatibility score is {compatibility_score}/100.
    
    Profile 1: {profile1.name}, {profile1.age}, {profile1.occupation}, interested in {profile1.interests}, 
    looking for {profile1.get_looking_for_display()}, timeline to settle: {profile1.settle_timeline} months

    Profile 2: {profile2.name}, {profile2.age}, {profile2.occupation}, interested in {profile2.interests}, 
    looking for {profile2.get_looking_for_display()}, timeline to settle: {profile2.settle_timeline} months

    Highlight key points of compatibility in a positive, encouraging tone. Keep it under 100 words.
    """

    reason = call_openai_api(prompt, max_tokens=100)
    if reason:
        return reason
    return "These profiles seem compatible based on their interests and preferences."

def generate_matches():
    """
    Generate matches between profiles based on compatibility.
    
    Returns:
    int: The number of new matches created.
    """
    profiles = Profile.objects.all()
    new_matches = []
    processed_pairs = set()

    for i, profile1 in enumerate(profiles):
        for profile2 in profiles[i+1:]:
            # Create a unique identifier for this pair
            pair_id = tuple(sorted([profile1.id, profile2.id]))
            if pair_id in processed_pairs:
                continue
            processed_pairs.add(pair_id)

            # Check if the pair is compatible based on their preferences
            if is_compatible_pair(profile1, profile2):
                compatibility_score = calculate_compatibility(profile1, profile2)
                if compatibility_score >= settings.MATCH_THRESHOLD:
                    reason = generate_match_reason(profile1, profile2, compatibility_score)
                    new_matches.append(
                        Match(
                            profile1=profile1,
                            profile2=profile2,
                            compatibility_score=compatibility_score,
                            reason=reason
                        )
                    )

    # Bulk create all new matches
    Match.objects.bulk_create(new_matches)
    return len(new_matches)

def is_compatible_pair(profile1: Profile, profile2: Profile):
    """
    Check if two profiles are compatible based on basic criteria.
    
    Args:
    profile1 (Profile): The first profile to compare.
    profile2 (Profile): The second profile to compare.
    
    Returns:
    bool: True if the profiles are compatible, False otherwise.
    """
    # This is a simplified check and should be expanded based on your app's gender and preference options
    if profile1.gender != profile2.gender and profile1.looking_for == profile2.looking_for:
        return True
    return False
