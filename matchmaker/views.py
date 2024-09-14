from django.shortcuts import render, redirect
from .forms import ProfileForm
from .models import Profile, Match
from .utils import generate_matches
from django.db.models import Q

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
    return render(request, '/Users/khanhvu/Documents/fullstack/dating_app/matchmaker/templates/profile_form.html', {'form': form})

def matches_list(request):
    search_query = request.GET.get('search', '')  # Get the search query from the GET request
    if search_query:
        # Filter profiles by name or other fields (you can customize the search logic here)
        profiles = Profile.objects.filter(
            Q(name__icontains=search_query) | 
            Q(occupation__icontains=search_query) |
            Q(gender__icontains=search_query)
        )
    else:
        # If no search query, show all profiles
        profiles = Profile.objects.all()
    
    return render(request, 'matches_list.html', {'profiles': profiles})