from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser, FreelancerProfile, ClientProfile
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'user_type')
    def save(self, commit=True):
        Customuser = super().save(commit=False)
        Customuser.email = self.cleaned_data['email']
        Customuser.user_type = self.cleaned_data['user_type']
        if commit:
            Customuser.save()
        return Customuser    

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'bio', 'profile_picture')

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'location', 'interests', 'bio', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'resize-none'}),
            'interests': forms.Textarea(attrs={'rows': 2, 'class': 'resize-none', 
                                             'placeholder': 'Enter your interests separated by commas'}),
        }

class FreelancerProfileForm(forms.ModelForm):
    class Meta:
        model = FreelancerProfile
        fields = ['working_profession', 'skills', 'description']
        widgets = {
            'skills': forms.Textarea(attrs={
                'rows': 2,
                'class': 'resize-none',
                'placeholder': 'Enter skills separated by commas (e.g., Python, JavaScript, UI Design)'
            }),
            'description': forms.Textarea(attrs={'rows': 4}),
            'working_profession': forms.TextInput(attrs={'placeholder': 'e.g., Full Stack Developer'})
        }

class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = ['company_name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }



class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = CustomUser
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')

        return cleaned_data
