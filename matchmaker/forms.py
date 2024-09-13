from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'name', 
            'age', 
            'gender', 
            'relationship_status', 
            'looking_for', 
            'settle_timeline', 
            'occupation', 
            'interests'
        ]
        widgets = {
            'interests': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your interests, separated by commas'}),
            'settle_timeline': forms.NumberInput(attrs={'min': 0, 'max': 60}),
        }

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        
        # Add classes for styling
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Customize specific fields
        self.fields['age'].widget.attrs.update({'min': 18, 'max': 100})
        self.fields['gender'].widget = forms.Select(choices=Profile.GENDER_CHOICES)
        self.fields['relationship_status'].widget = forms.Select(choices=Profile.RELATIONSHIP_STATUS_CHOICES)
        self.fields['looking_for'].widget = forms.Select(choices=Profile.LOOKING_FOR_CHOICES)

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age < 18:
            raise forms.ValidationError("You must be at least 18 years old to use this service.")
        return age

# Usage:
# In your views.py:
# from .forms import ProfileForm
#
# def create_profile(request):
#     if request.method == 'POST':
#         form = ProfileForm(request.POST)
#         if form.is_valid():
#             profile = form.save()
#             return redirect('profile_detail', pk=profile.pk)
#     else:
#         form = ProfileForm()
#     return render(request, 'create_profile.html', {'form': form})