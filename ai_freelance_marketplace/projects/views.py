from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.mail import send_mail
from .models import Project, Bid, ProjectInterest,Rating, ProjectUpdate
from .forms import ProjectForm, BidForm,RatingForm,ProjectUpdateForm, ProjectStatusUpdateForm,ProjectCreationForm
# from ai_features.project_matching import rank_freelancers, match_project_to_freelancers
from accounts.models import FreelancerProfile, CustomUser
from django.db.models import Avg, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import models
from django.http import HttpResponseForbidden
from ai_features.recommendation_system import recommend_freelancers, recommend_projects
from django.core.exceptions import PermissionDenied
from django.db import transaction

User = get_user_model()

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')

def contact(request):
    return render(request, 'contact.html')


def search_projects(request):
    query = request.GET.get('q', '')
    if query:
        projects = Project.objects.filter(title__icontains=query)
    else:
        projects = Project.objects.all()

    context = {
        'projects': projects,
        'query': query
    }
    return render(request, 'projects/search_projects.html', context)


@login_required
def dashboard(request):
    user = request.user
    if user.user_type == 'client':
        projects = Project.objects.filter(client=user)
        template = 'accounts/client_dashboard.html'
    else:
        submitted_bids = Bid.objects.filter(freelancer=user)
        hired_projects = Project.objects.filter(hired_freelancer=user)
        projects = (submitted_bids | hired_projects).distinct()
        template = 'accounts/freelancer_dashboard.html'

    context = {
        'projects': projects,
        'user': user,
    }
    return render(request, template, context)


@login_required
def project_list(request):
    projects = Project.objects.filter(status='open').order_by('-created_at')
    return render(request, 'projects/project_list.html', {'projects': projects})


# @login_required
# def project_detail(request, pk):
#     project = get_object_or_404(Project, pk=pk)
#     bid_form = None
#     user_bid = None
#     is_interested = False

#     if request.user.user_type == 'freelancer':
#         bid_form = BidForm()
#         freelancer_profile = FreelancerProfile.objects.get(user=request.user)
#         user_bid = Bid.objects.filter(project=project, freelancer=request.user).first()
#         is_interested = ProjectInterest.objects.filter(project=project, freelancer=request.user).exists()

#     bids = Bid.objects.filter(project=project).select_related('freelancer__freelancer_profile')
#     interested_freelancers = CustomUser.objects.filter(project_interests__project=project)

#     context = {
#         'project': project,
#         'bid_form': bid_form,
#         'user_bid': user_bid,
#         'bids': bids,
#         'is_interested': is_interested,
#         'interested_freelancers': interested_freelancers,
#     }
#     return render(request, 'projects/project_detail.html', context)

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, id=pk)
    
    # Add status-specific context
    status_context = {}
    if project.status == 'incomplete':
        status_context = {
            'show_incomplete_warning': True,
            'missed_deadline': project.deadline,
            'can_repost': request.user == project.client,
        }
    
    # Get skills directly from the project's required_skills field
    skills = []
    if project.required_skills:
        skills = [skill.strip() for skill in project.required_skills.split(',') if skill.strip()]
    
    recommended_freelancers = recommend_freelancers(project)
    
    context = {
        'project': project,
        'skills': skills,
        'bids': project.bids.all() if project.status == 'open' else None,
        'recommended_freelancers': recommended_freelancers,
        **status_context,  # Include status-specific context
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectCreationForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.client = request.user
            
            # Clean and save skills
            skills = form.cleaned_data.get('required_skills', '')
            if skills:
                # Split by comma, strip whitespace, and filter out empty strings
                skill_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
                project.required_skills = ','.join(skill_list)
            
            project.save()
            messages.success(request, 'Project created successfully!')
            return redirect('project_detail', pk=project.id)
    else:
        form = ProjectCreationForm()
    
    return render(request, 'projects/create_project.html', {'form': form})


@login_required
def update_project(request, pk):
    project = get_object_or_404(Project, id=pk, client=request.user)
    if request.method == 'POST':
        form = ProjectUpdateForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            
            # Clean and save skills
            skills = form.cleaned_data.get('required_skills', '')
            if skills:
                skill_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
                project.required_skills = ','.join(skill_list)
            else:
                project.required_skills = ''
            
            project.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('project_detail', pk=project.id)
    else:
        form = ProjectUpdateForm(instance=project)
        if project.required_skills:
            form.initial['required_skills'] = project.required_skills
    
    return render(request, 'projects/update_project.html', {'form': form, 'project': project})

@login_required
def submit_bid(request, project_id):
    if request.user.user_type != 'freelancer':
        messages.error(request, "Only freelancers can submit bids.")
        return redirect('project_detail', pk=project_id)

    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.project = project
            bid.freelancer = request.user
            bid.save()
            messages.success(request, "Bid submitted successfully.")
            return redirect('project_detail', pk=project_id)
    else:
        form = BidForm()
    return render(request, 'projects/submit_bid.html', {'form': form, 'project': project})

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, client=request.user)
    if request.method == 'POST':
        project.delete()
        messages.success(request, "Project deleted successfully.")
        return redirect('project_list')  # Redirect to your project list view
    return redirect('project_detail', project_id=project.id)

def delete_project_confirm(request, project_id):
    project = get_object_or_404(Project, id=project_id, client=request.user)
    if request.method == "POST":
        project.delete()
        return redirect('project_list')
    return render(request, 'delete_project.html', {'project': project})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from .models import Project, ProjectInterest
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

@login_required
def express_interest(request, project_id=None, pk=None):
    project_id = project_id or pk  # Use whichever is provided
    project = get_object_or_404(Project, id=project_id)
    
    try:
        interest, created = ProjectInterest.objects.get_or_create(project=project, freelancer=request.user)

        if created:
            messages.success(request, f"You have expressed interest in the project '{project.title}'")
            # Attempt to send email
            try:
                subject = f"New interest in your project: {project.title}"
                message = f"{request.user.get_full_name()} wants to work on your project '{project.title}'"
                send_mail(subject, message, 'from@example.com', [project.client.email])
            except Exception as e:
                logger.error(f"Failed to send email: {str(e)}")
                messages.warning(request, "Interest recorded, but notification email could not be sent.")
        else:
            interest.delete()
            messages.success(request, f"You have withdrawn your interest from the project '{project.title}'")

    except ValidationError as e:
        messages.error(request, str(e))
    except Exception as e:
        logger.error(f"Error in express_interest view: {str(e)}")
        messages.error(request, "An error occurred while processing your request. Please try again later.")

    return redirect('project_detail', pk=project_id)


@login_required
def my_projects(request):
    if request.user.user_type == 'client':
        projects = Project.objects.filter(client=request.user).order_by('-created_at')
    else:
        projects = Project.objects.filter(freelancer=request.user).order_by('-created_at')
    return render(request, 'projects/my_projects.html', {'projects': projects})




def freelancer_profile(request, username):
    freelancer = get_object_or_404(User, username=username)
    project_id = request.GET.get('project_id')
    project = None if not project_id else get_object_or_404(Project, id=project_id)
    
    # Get completed projects using hired_freelancer instead of freelancer
    completed_projects = Project.objects.filter(
        hired_freelancer=freelancer, 
        status='completed'
    ).count()
    
    # Get current bids
    current_bids = Bid.objects.filter(
        freelancer=freelancer,
        project__status='open'
    ).select_related('project')
    
    # Get average rating
    average_rating = freelancer.ratings_received.aggregate(
        avg_rating=models.Avg('score')
    )['avg_rating'] or 0
    
    # Get reviews
    reviews = freelancer.ratings_received.all().select_related('project', 'rater')
    
    # Get profile
    profile = freelancer.freelancer_profile
    
    # Calculate suitability reasons if project is provided
    suitability_reasons = []
    if project and profile:
        freelancer_skills = set(skill.lower().strip() for skill in profile.get_skills_list())
        project_skills = set(skill.lower().strip() for skill in project.required_skills.split(',')) if project.required_skills else set()
        
        if freelancer_skills & project_skills:
            suitability_reasons.append("Has relevant skills for this project")
        if completed_projects > 0:
            suitability_reasons.append(f"Has completed {completed_projects} projects")
        if average_rating >= 4:
            suitability_reasons.append("Highly rated freelancer")
    
    context = {
        'freelancer': freelancer,
        'profile': profile,
        'completed_projects': completed_projects,
        'current_bids': current_bids,
        'average_rating': average_rating,
        'reviews': reviews,
        'project': project,
        'suitability_reasons': suitability_reasons,
    }
    
    return render(request, 'projects/freelancer_profile.html', context)


@login_required
def add_rating(request, pk):
    project = get_object_or_404(Project, id=pk)
    
    if request.user != project.client and request.user != project.hired_freelancer:
        messages.error(request, "You don't have permission to rate this project.")
        return redirect('project_detail', pk=pk)
    
    if project.status != 'completed':
        messages.error(request, "You can only rate completed projects.")
        return redirect('project_detail', pk=pk)
    
    if Rating.objects.filter(project=project, rater=request.user).exists():
        messages.error(request, "You have already rated this project.")
        return redirect('project_detail', pk=pk)
    
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.project = project
            rating.rater = request.user
            rating.rated_user = project.hired_freelancer if request.user == project.client else project.client
            rating.save()
            messages.success(request, "Rating submitted successfully.")
            return redirect('project_detail', pk=pk)
    else:
        form = RatingForm()
    
    context = {
        'form': form,
        'project': project,
    }
    return render(request, 'projects/add_rating.html', context)


@login_required
@require_POST
def hire_freelancer(request, project_id, freelancer_id):
    project = get_object_or_404(Project, id=project_id, client=request.user)
    freelancer = get_object_or_404(CustomUser, id=freelancer_id, user_type='freelancer')

    if project.status != 'open':
        messages.error(request, "This project is not open for hiring.")
        return redirect('project_detail', pk=project_id)

    if project.hired_freelancer:
        messages.error(request, f"You can't hire for this project. You have already hired {project.hired_freelancer.username}.")
        return redirect('project_detail', pk=project_id)

    bid = Bid.objects.filter(project=project, freelancer=freelancer).first()
    if not bid:
        messages.error(request, "This freelancer has not placed a bid on your project.")
        return redirect('project_detail', pk=project_id)

    project.hired_freelancer = freelancer
    project.status = 'hired'
    project.save()

    # You might want to notify the freelancer here (e.g., send an email)

    messages.success(request, f"You have successfully hired {freelancer.username} for your project.")
    return redirect('project_detail', pk=project_id)

@login_required
@require_POST
def mark_project_completed(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Ensure only the assigned freelancer can mark as completed
    if request.user != project.freelancer:
        messages.error(request, "Only the assigned freelancer can mark the project as completed.")
        return redirect('project_detail', pk=project_id)
    
    if project.status != 'in_progress':
        messages.error(request, "Only in-progress projects can be marked as completed.")
        return redirect('project_detail', pk=project_id)
    
    project.mark_completed()
    messages.success(request, "Project marked as completed. The client can now leave a review.")
    
    return redirect('project_detail', pk=project_id)

@login_required
def submit_review(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Ensure only the client can review completed projects
    if request.user != project.client or project.status != 'completed':
        messages.error(request, "You can only review completed projects that you own.")
        return redirect('project_detail', pk=project_id)
    
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.project = project
            review.reviewer = request.user
            review.reviewee = project.freelancer
            review.save()
            
            messages.success(request, "Review submitted successfully.")
            return redirect('project_detail', pk=project_id)
    else:
        form = RatingForm()
    
    return render(request, 'projects/submit_review.html', {
        'form': form,
        'project': project
    })

@login_required
def start_project(request, pk):
    project = get_object_or_404(Project, id=pk, hired_freelancer=request.user)
    
    if project.status != 'hired':
        messages.error(request, "This project cannot be started at this time.")
        return redirect('project_detail', pk=pk)
    
    project.start_project()
    messages.success(request, "Project has been started successfully!")
    return redirect('start_project', pk=pk)

@login_required
def update_project_status(request, project_id):
    project = get_object_or_404(Project, id=project_id, hired_freelancer=request.user)
    
    if request.method == 'POST':
        form = ProjectStatusUpdateForm(request.POST)
        if form.is_valid():
            new_status = form.cleaned_data['status']
            work_details = form.cleaned_data['work_details']
            
            try:
                with transaction.atomic():
                    # Update project status
                    project.status = new_status
                    if new_status == 'completed':
                        project.completed_at = timezone.now()
                    project.current_work_details = work_details
                    project.save()
                    
                    # Create project update record
                    ProjectUpdate.objects.create(
                        project=project,
                        details=work_details,
                        status=new_status
                    )
                
                messages.success(request, "Project status updated successfully!")
                return redirect('project_detail', pk=project_id)
            except PermissionDenied:
                messages.error(request, "You don't have permission to perform this action.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = ProjectStatusUpdateForm(initial={'status': project.status})
    
    return render(request, 'projects/update_project_status.html', {
        'form': form,
        'project': project
    })


@login_required
def confirm_project_completion(request, project_id):
    project = get_object_or_404(Project, id=project_id, client=request.user)
    
    if project.status != 'completed':
        messages.error(request, "This project is not ready for confirmation.")
        return redirect('project_detail', project_id=project_id)
    
    if request.method == 'POST':
        project.status = 'confirmed'
        project.save()
        messages.success(request, "Project completion confirmed! Please leave a review.")
        return redirect('submit_review', project_id=project_id)
    
    return render(request, 'projects/confirm_completion.html', {'project': project})

@login_required
def clear_project_history(request, pk):
    project = get_object_or_404(Project, id=pk)
    
    if request.user != project.client and request.user != project.hired_freelancer:
        messages.error(request, "You don't have permission to clear this project's history.")
        return redirect('project_detail', pk=pk)
    
    if project.status != 'completed':
        messages.error(request, "You can only clear history for completed projects.")
        return redirect('project_detail', pk=pk)
    
    if request.user == project.client:
        project.client_cleared_history = True
    else:
        project.freelancer_cleared_history = True
    
    project.save()
    messages.success(request, "Project history has been cleared from your view.")
    return redirect('dashboard')

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
    
    # Get recommended projects
    recommended_projects = recommend_projects(request.user)
    
    context = {
        'hired_projects': hired_projects,
        'bid_projects': bid_projects,
        'recommended_projects': recommended_projects,
        'user': request.user,
    }
    return render(request, 'accounts/freelancer_dashboard.html', context)

# In views.py
from .forms import RepostProjectForm

# views.py
@login_required
def repost_project(request, pk):
    original_project = get_object_or_404(Project, pk=pk, client=request.user)
    
    if request.method == 'POST':
        form = RepostProjectForm(request.POST)
        if form.is_valid():
            new_project = Project.objects.create(
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                required_skills=form.cleaned_data['required_skills'],
                budget=form.cleaned_data['budget'],
                deadline=form.cleaned_data['deadline'],
                client=request.user,
                status='open'
            )
            
            messages.success(request, "Project has been reposted successfully!")
            return redirect('project_detail', pk=new_project.pk)
    else:
        # Pre-populate form with original project data
        initial_data = {
            'title': original_project.title,
            'description': original_project.description,
            'required_skills': original_project.required_skills,
            'budget': original_project.budget,
            'deadline': timezone.now() + timezone.timedelta(days=30)  # Default to 30 days from now
        }
        form = RepostProjectForm(initial=initial_data)

    return render(request, 'projects/repost_project.html', {
        'form': form,
        'original_project': original_project
    })