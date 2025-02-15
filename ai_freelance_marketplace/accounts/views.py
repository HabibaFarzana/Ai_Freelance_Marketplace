from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser, FreelancerProfile, ClientProfile
from .forms import CustomUserChangeForm, FreelancerProfileForm, ClientProfileForm
from projects.models import Project ,Rating,ProjectUpdate,Bid
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth.backends import ModelBackend
from django.db.models import Avg,Q
from .forms import SignUpForm 
from .forms import ClientProfile
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.db import IntegrityError
from django.contrib.auth import get_user_model
CustomUser = get_user_model()

def index(request):
    return render(request, 'index.html')


def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        user_type = request.POST['user_type']

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password1,
                user_type=user_type  # Assuming 'user_type' is a field in CustomUser
            )
            user.backend = 'django.contrib.auth.backends.ModelBackend'  # Explicitly set the backend
            user.save()

            # Log the user in
            auth_login(request, user)  # Specify the backend
            messages.success(request, f"Account created for {username} as a {user_type}.")
            return redirect('home')  # Redirect to the home page or any other page
        except IntegrityError:
            messages.error(request, "Username already exists.")
            return redirect('register')
    else:
        return render(request, 'accounts/register.html')



def express_interest(request):

    return render(request, 'express_interest.html')

# @ensure_csrf_cookie
# def login(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             user.backend = 'django.contrib.auth.backends.ModelBackend'
#             auth_login(request, user)  # Corrected login method
#             messages.success(request, f"Welcome back, {user.username}!")
#             return redirect('user_list')
#         else:
#             messages.error(request, 'Invalid username or password.')
#     return render(request, 'accounts/login.html')

# accounts/views.py replace login function:

@ensure_csrf_cookie
def login(request):
    user_type = request.GET.get('user_type') or request.POST.get('user_type')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user_type == 'client' and user.user_type == 'client':
                auth_login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('user_list')
            elif user_type == 'freelancer' and user.user_type == 'freelancer':
                auth_login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('user_list')
            else:
                if user_type == 'client':
                    messages.error(request, 'Only clients can log in here.')
                else:
                    messages.error(request, 'Only freelancers can log in here.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html', {'user_type': user_type})

@login_required
def dashboard(request):
    user = request.user
    if user.user_type == 'client':
        return client_dashboard(request)
    elif user.user_type == 'freelancer':
        return freelancer_dashboard(request)
    else:
        return redirect('home')

@login_required
def client_dashboard(request):
    projects = Project.objects.filter(client=request.user).exclude(client_cleared_history=True).order_by('-created_at')
    context = {
        'projects': projects,
    }
    return render(request, 'accounts/client_dashboard.html', context)

from ai_features.recommendation_system import recommend_projects  # Add this import

@login_required
def freelancer_dashboard(request):
    hired_projects = Project.objects.filter(
        hired_freelancer=request.user
    ).exclude(freelancer_cleared_history=True).select_related('client').order_by('-created_at')
    
    bid_projects = Project.objects.filter(
        bids__freelancer=request.user,
        status='open'
    ).exclude(
        hired_freelancer=request.user
    ).distinct().order_by('-created_at')
    
    user = request.user
    try:
        freelancer_profile = FreelancerProfile.objects.get(user=user)
        recommended_projects = recommend_projects(user)  # Get recommended projects
    except FreelancerProfile.DoesNotExist:
        freelancer_profile = None
        recommended_projects = []
    
    context = {
        'hired_projects': hired_projects,
        'bid_projects': bid_projects,
        'user': request.user,
        'recommended_projects': recommended_projects,
    }
    return render(request, 'accounts/freelancer_dashboard.html', context)

 
class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/profile_form.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        if self.request.user.user_type == 'freelancer':
            return FreelancerProfile.objects.get_or_create(user=self.request.user)[0]
        else:
            return ClientProfile.objects.get_or_create(user=self.request.user)[0]

    def get_form_class(self):
        if self.request.user.user_type == 'freelancer':
            return FreelancerProfileForm
        else:
            return ClientProfileForm

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CustomUser, FreelancerProfile, ClientProfile
from .forms import FreelancerProfileForm, ClientProfileForm, CustomUserForm

# @login_required
# def profile_view(request):
#     user = request.user
#     if user.user_type == 'freelancer':
#         profile = FreelancerProfile.objects.get(user=user)
#         completed_projects = Project.objects.filter(hired_freelancer=user, status='completed')
#         ratings = Rating.objects.filter(rated_user=user)
#     else:  # client
#         profile = ClientProfile.objects.get(user=user)
#         completed_projects = Project.objects.filter(client=user, status='completed')
#         ratings = Rating.objects.filter(rater=user)

#     context = {
#         'user': user,
#         'profile': profile,
#         'completed_projects': completed_projects,
#         'ratings': ratings,
#     }
#     return render(request, 'accounts/profile.html', context)

@login_required
def profile_view(request):
    user = request.user
    if user.user_type == 'freelancer':
        profile, created = FreelancerProfile.objects.get_or_create(user=user)
        completed_projects = Project.objects.filter(hired_freelancer=user, status='completed')
        ratings = Rating.objects.filter(rated_user=user)
    else:  # client
        profile, created = ClientProfile.objects.get_or_create(user=user)
        completed_projects = Project.objects.filter(client=user, status='completed')
        ratings = Rating.objects.filter(rater=user)

    context = {
        'user': user,
        'profile': profile,
        'completed_projects': completed_projects,
        'ratings': ratings,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        user_form = CustomUserForm(request.POST, request.FILES, instance=user)
        if user.user_type == 'freelancer':
            profile_form = FreelancerProfileForm(request.POST, instance=user.freelancer_profile)
        else:
            profile_form = ClientProfileForm(request.POST, instance=user.client_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('profile_view')
    else:
        user_form = CustomUserForm(instance=user)
        if user.user_type == 'freelancer':
            profile_form = FreelancerProfileForm(instance=user.freelancer_profile)
        else:
            profile_form = ClientProfileForm(instance=user.client_profile)
    
    return render(request, 'accounts/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

# def freelancer_profile(request, username):
#     freelancer = get_object_or_404(User, username=username, user_type='freelancer')
#     freelancer_profile = FreelancerProfile.objects.get(user=freelancer)
    
#     completed_projects = Project.objects.filter(freelancer=freelancer, status='completed').count()
    
#     average_rating = Rating.objects.filter(rated_user=freelancer).aggregate(Avg('score'))['score__avg'] or 0
    
#     current_bids = Bid.objects.filter(freelancer=freelancer).select_related('project')
    
#     project_id = request.GET.get('project_id')
#     suitability_reasons = []

def freelancer_profile(request, username):
    freelancer = get_object_or_404(CustomUser, username=username, user_type='freelancer')
    # Explicitly create the FreelancerProfile if it doesn't exist
    freelancer_profile, created = FreelancerProfile.objects.get_or_create(user=freelancer)
    
    completed_projects = Project.objects.filter(freelancer=freelancer, status='completed').count()
    
    average_rating = Rating.objects.filter(rated_user=freelancer).aggregate(Avg('score'))['score__avg'] or 0
    
    current_bids = Bid.objects.filter(freelancer=freelancer).select_related('project')
    
    project_id = request.GET.get('project_id')
    suitability_reasons = []
    
    # Rest of the existing code remains the same...
    
    if project_id:
        try:
            project = Project.objects.get(id=project_id)
            
            # Check skills match
            if project.required_skills and freelancer_profile.skills:
                project_skills = set(s.strip().lower() for s in project.required_skills.split(','))
                freelancer_skills = set(s.strip().lower() for s in freelancer_profile.skills.split(','))
                matching_skills = project_skills.intersection(freelancer_skills)
                
                if matching_skills:
                    suitability_reasons.append(f"Has {len(matching_skills)} required skills: {', '.join(matching_skills)}")
            
            # Check previous similar projects
            similar_projects = Project.objects.filter(
                freelancer=freelancer,
                status='completed',
                required_skills__icontains=project.required_skills
            ).count()
            
            if similar_projects > 0:
                suitability_reasons.append(f"Completed {similar_projects} similar projects")
            
            # Calculate bid competitiveness
            freelancer_bid = Bid.objects.filter(project=project, freelancer=freelancer).first()
            if freelancer_bid:
                avg_bid = Bid.objects.filter(project=project).aggregate(Avg('amount'))['amount__avg']
                if avg_bid and freelancer_bid.amount <= avg_bid:
                    suitability_reasons.append("Competitive bid price")
        except Project.DoesNotExist:
            # Handle case where project doesn't exist
            pass
    
    context = {
        'freelancer': freelancer,
        'profile': freelancer_profile,
        'completed_projects': completed_projects,
        'average_rating': round(average_rating, 1),
        'current_bids': current_bids,
        'suitability_reasons': suitability_reasons,
    }
    
    return render(request, 'projects/freelancer_profile.html', context)

@login_required
def start_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, hired_freelancer=request.user)
    
    if project.status != 'hired':
        messages.error(request, "This project cannot be started at this time.")
        return redirect('project_detail', pk=project_id)
    
    if request.method == 'POST':
        initial_details = request.POST.get('initial_details')
        project.start_project()
        if initial_details:
            ProjectUpdate.objects.create(
                project=project,
                details=initial_details,
                status='just_started'
            )
        messages.success(request, "Project has been started successfully!")
        return redirect('project_detail', pk=project_id)
    
    return render(request, 'projects/start_project.html', {'project': project})


# added

@login_required
def user_list(request):
    users = CustomUser.objects.exclude(id=request.user.id)
    return render(request, 'accounts/user_list.html', {'users': users})

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CustomUser, FreelancerProfile, ClientProfile

@login_required
def profile(request):
    user = request.user
    profile = None
    
    try:
        if user.user_type == 'freelancer':
            profile = FreelancerProfile.objects.get_or_create(user=user)[0]
        else:
            profile = ClientProfile.objects.get_or_create(user=user)[0]
    except Exception as e:
        # Log the error or handle it appropriately
        profile = None

    return render(request, 'profile.html', {
        'user': user,
        'profile': profile,
    })

@login_required
def user_profile(request, user_id):
    # Profile viewed by another user
    viewed_user = get_object_or_404(CustomUser, id=user_id)
    profile = None
    
    try:
        if viewed_user.user_type == 'freelancer':
            profile = FreelancerProfile.objects.get(user=viewed_user)
        else:
            profile = ClientProfile.objects.get(user=viewed_user)
    except Exception as e:
        # Log the error or handle it appropriately
        profile = None

    return render(request, 'accounts/user_profile.html', {
        'profile_user': viewed_user,
        'profile': profile,
    })