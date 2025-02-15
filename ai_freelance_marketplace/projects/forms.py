from django import forms
from .models import Project, Bid, Rating,ProjectUpdate
from django.utils import timezone


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'budget', 'deadline', 'required_skills']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'required_skills': forms.Textarea(attrs={
                'rows': 2,
                'class': 'resize-none',
                'placeholder': 'Enter required skills separated by commas'
            }),
        }

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score', 'comment']
        widgets = {
            'score': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

class ProjectCompletionForm(forms.Form):
    confirmation = forms.BooleanField(
        required=True,
        label="I confirm that I have completed all the requirements for this project.",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )



class ProjectUpdateForm(forms.ModelForm):
    required_skills = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Python, Java, JavaScript',
        }),
        help_text='Enter skills separated by commas'
    )

    class Meta:
        model = Project
        fields = ['title', 'description', 'required_skills', 'budget', 'deadline', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }



class ProjectStatusUpdateForm(forms.Form):
    STATUS_CHOICES = [
        ('just_started', 'Just Started'),
        ('intermediate', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        })
    )
    work_details = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'required': True,
            'placeholder': 'Describe the current progress and any updates...'
        })
    )


class ProjectCreationForm(forms.ModelForm):
    required_skills = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Python, Java, JavaScript',
        }),
        help_text='Enter skills separated by commas'
    )

    class Meta:
        model = Project
        fields = ['title', 'description', 'required_skills', 'budget', 'deadline']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'deadline': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local',
                    'min': timezone.now().strftime('%Y-%m-%dT%H:%M')  # Set minimum date to now
                }
            ),
        }


class RepostProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'required_skills', 'budget', 'deadline']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'deadline': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local',
                    'min': timezone.now().strftime('%Y-%m-%dT%H:%M')
                }
            ),
        }

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if not deadline:
            deadline = timezone.now() + timedelta(days=30)  # Default to 30 days from now
        return deadline