from django.shortcuts import render, redirect
from .forms import ProfileForm
from .models import Profile, Match
from .utils import generate_matches

# View to create a new profile
def profile_create(request):
    # Check if the request method is POST (i.e., when the form is submitted)
    if request.method == 'POST':
        form = ProfileForm(request.POST)  # Create a form instance with POST data
        # Check if the form data is valid
        if form.is_valid():
            form.save()  # Save the form data to the database
            return redirect('matches_list')  # Redirect to the matches list after saving
    else:
        form = ProfileForm()  # If the request is GET, create an empty form

    # Render the profile creation form template, passing the form as context
    return render(request, 'templates/profile_form.html', {'form': form})

# View to display a list of profiles (assuming only male profiles are shown)
def matches_list(request):
    profiles = Profile.objects.filter(gender='M')  # Filter profiles by gender ('M' for male)
    # Render the matches list template, passing the filtered profiles as context
    return render(request, 'templates/matches_list.html', {'profiles': profiles})
