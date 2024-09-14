import requests
import random
from django.conf import settings
from django.db.models import Q
from .models import Profile, Match
import json

# Set up OpenAI API key and endpoint
OPENAI_API_KEY = settings.OPENAI_API_KEY
OPENAI_URL = 'https://api.openai.com/v1/chat/completions'

# Predefined options for generating random profiles
PROFILE_OPTIONS = {
    'relationship_status': ['Single', 'In a relationship', 'Divorced', 'Widowed', 'Married'],
    'looking_for': ['Friendship', 'Casual dating', 'Long-term relationship', 'Short-term relationship', 'Marriage'],}

def call_openai_api(prompt, max_tokens=150):
    """
    Call the OpenAI API using the requests library to generate a response using the gpt-4o-mini model.
    
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
        'model': 'gpt-4o-mini',  # Updated model to gpt-4o-mini
        'messages': [
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 1,
        'max_tokens': max_tokens
    }
    
    try:
        response = requests.post(OPENAI_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except requests.exceptions.RequestException as e:
        print(f"Error calling OpenAI API: {e}")
        return None

def generate_random_profile(gender):
    """
    Generate a random dating profile using OpenAI's GPT-4 via API call.
    
    Returns:
    dict: A dictionary containing profile attributes, or None if an error occurs.
    """
    prompt = f"""Generate a random dating profile with the following attributes: randomize and be creative with different races. 
    We already have these names: {set(Profile.objects.values_list('name', flat=True))} DO NOT REPEAT
    1. Full name based on gender of {gender}
    2. Age (between 18 and 65)
    3. Occupation
    4. 3-5 interests or hobbies (comma-separated)
    5. Timeline to settle down (in months, between 0 and 60)

    Format the response as a Python dictionary with keys: name, age, occupation, interests, settle_timeline."""
    profile_text = call_openai_api(prompt, max_tokens=150)
    if not profile_text:
        return None

    try:
        # find everything between the curly braces
        profile_text = profile_text[profile_text.find("{"):profile_text.rfind("}")+1]
        print(profile_text)
        # Parse the generated profile text as a Python dictionary
        profile_dict = json.loads(profile_text)
        print(profile_dict)
    except Exception as e:
        print(f"Error parsing generated profile: {e}")
        return None

    # Add randomly selected options for predefined fields
    profile_dict['gender'] = gender
    profile_dict['relationship_status'] = random.choice(PROFILE_OPTIONS['relationship_status'])
    profile_dict['looking_for'] = random.choice(PROFILE_OPTIONS['looking_for'])

    # Ensure correct data types and formats
    profile_dict['age'] = int(profile_dict['age'])
    profile_dict['settle_timeline'] = int(profile_dict['settle_timeline'])
    profile_dict['gender'] = profile_dict['gender'][0].upper()
    profile_dict['relationship_status'] = profile_dict['relationship_status'][0].upper()
    profile_dict['looking_for'] = profile_dict['looking_for'][:2].upper()

    return profile_dict


def get_ai_compatibility_and_final_analysis(profile1: Profile, profile2: Profile, manual_score):
    """
    Make a single API call to get both AI-generated compatibility scores and a final analysis explanation.
    
    Args:
    profile1 (Profile): The first profile to compare.
    profile2 (Profile): The second profile to compare.
    manual_score (int): The manually calculated score for age, timeline, and looking_for.
    
    Returns:
    dict: A dictionary containing AI-generated scores, total score, and a final explanation.
    """
    prompt = f"""Follow the instruction but only produce the final JSON output.
    Calculate the AI-based scores matching both profiles (50 points) based on the following rubric and provide a final compatibility explanation:
    - Occupation (out of 15)
    - Interests (out of 15)
    - Names (out of 5)
    - Personality (out of 15)
    The remaining score (already calculated: {manual_score}/50) is based on their relationship goals, timeline to settle down, and age difference.

    Profile 1: {profile1.name}, {profile1.age}, {profile1.occupation}, interested in {profile1.interests}, 
    looking for {profile1.get_looking_for_display()}, timeline to settle: {profile1.settle_timeline} months.

    Profile 2: {profile2.name}, {profile2.age}, {profile2.occupation}, interested in {profile2.interests}, 
    looking for {profile2.get_looking_for_display()}, timeline to settle: {profile2.settle_timeline} months.

    Provide the following output for compatibility score as a formated JSON:
        'Occupation (out of 15)': ,
        'Interests (out of 15)': ,
        'Names (out of 5)': ,
        'Personality (out of 15)': ,
        'Compatibility Explanation: 
    """

    response = call_openai_api(prompt, max_tokens=400)

    if not response:
        return None

    try:      
        # remove initial json
        response = response[response.find("{"):response.rfind("}")+1]
        response_dict = json.loads(response)
        
        # Extract fields from the response_dict
        scores = {
            'occupation': response_dict.get('Occupation (out of 15)', 0),
            'interests': response_dict.get('Interests (out of 15)', 0),
            'names': response_dict.get('Names (out of 5)', 0),
            'personality': response_dict.get('Personality (out of 15)', 0),
            'manual_score': manual_score,
            'final_explanation': response_dict.get('Compatibility Explanation', '')
        }
        
        scores['total_score'] = scores['manual_score'] + scores['occupation'] + scores['interests'] + scores['names'] + scores['personality']
        
        return scores

    except Exception as e:
        print(f"Error parsing AI response: {e}")
        return None


def calculate_manual_score(profile1: Profile, profile2: Profile):
    """
    Manually calculate the compatibility score based on age difference, timeline difference, and relationship goals.
    
    Args:
    profile1 (Profile): The first profile to compare.
    profile2 (Profile): The second profile to compare.
    
    Returns:
    int: The manually calculated score out of 50.
    """
    score = 0

    # Looking For (15 points)
    if profile1.looking_for == profile2.looking_for:
        score += 15
    elif (profile1.looking_for in ['LO', 'SH'] and profile2.looking_for in ['LO', 'SH']) or \
        (profile1.looking_for in ['FR', 'CA'] and profile2.looking_for in ['FR', 'CA']):
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

    return score  # Out of 50


def calculate_compatibility(profile1: Profile, profile2: Profile):
    """
    Calculate the total compatibility score between two profiles, including both manual and AI-generated scores.
    
    Args:
    profile1 (Profile): The first profile to compare.
    profile2 (Profile): The second profile to compare.
    
    Returns:
    dict: Contains the final total score and explanation.
    """
    # Manually calculate the score (out of 50)
    manual_score = calculate_manual_score(profile1, profile2)

    # Get AI-generated scores and the final explanation
    ai_data = get_ai_compatibility_and_final_analysis(profile1, profile2, manual_score)
    
    if ai_data:
        final_score = ai_data['total_score']
        final_explanation = ai_data['final_explanation']
        return {
            'total_score': final_score,
            'explanation': final_explanation
        }
    return None


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
                compatibility_result = calculate_compatibility(profile1, profile2)
                if compatibility_result:
                    total_score = compatibility_result['total_score']
                    reason = compatibility_result['explanation']

                    if total_score >= settings.MATCH_THRESHOLD:
                        new_matches.append(
                            Match(
                                profile1=profile1,
                                profile2=profile2,
                                compatibility_score=total_score,
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
