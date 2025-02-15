from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from projects.models import Project
from accounts.models import FreelancerProfile

def get_skill_vector(skills):
    if not skills:
        return ''
    return ' '.join(skills.lower().split(','))

def recommend_freelancers(project, top_n=5):
    # Get all freelancer profiles
    freelancer_profiles = FreelancerProfile.objects.all()

    # Create skill vectors
    project_skills = get_skill_vector(project.required_skills)
    freelancer_skills = [get_skill_vector(profile.skills) for profile in freelancer_profiles]

    # If project has no skills or all freelancers have no skills, return empty list
    if not project_skills or not any(freelancer_skills):
        return []

    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer()
    skill_vectors = vectorizer.fit_transform([project_skills] + freelancer_skills)

    # Calculate cosine similarity
    cosine_similarities = cosine_similarity(skill_vectors[0:1], skill_vectors[1:]).flatten()

    # Get top N similar freelancers
    top_indices = np.argsort(cosine_similarities)[-top_n:][::-1]
    
    recommended_freelancers = [
        {
            'freelancer': freelancer_profiles[int(i)].user,
            'similarity_score': float(cosine_similarities[i]),
            'matching_skills': set(project_skills.split()) & set(freelancer_skills[int(i)].split())
        }
        for i in top_indices if cosine_similarities[i] > 0
    ]

    return recommended_freelancers

# def recommend_projects(freelancer, top_n=5):
#     # Get all open projects
#     open_projects = Project.objects.filter(status='open')

#     # Create skill vectors
#     freelancer_skills = get_skill_vector(freelancer.freelancer_profile.skills)
#     project_skills = [get_skill_vector(project.required_skills) for project in open_projects]

#     # If freelancer has no skills or all projects have no skills, return empty list
#     if not freelancer_skills or not any(project_skills):
#         return []

#     # Create TF-IDF vectorizer
#     vectorizer = TfidfVectorizer()
#     skill_vectors = vectorizer.fit_transform([freelancer_skills] + project_skills)

#     # Calculate cosine similarity
#     cosine_similarities = cosine_similarity(skill_vectors[0:1], skill_vectors[1:]).flatten()

#     # Get top N similar projects
#     top_indices = cosine_similarities.argsort()[-top_n:][::-1]
    
#     recommended_projects = [
#         {
#             'project': open_projects[int(i)],
#             'similarity_score': float(cosine_similarities[i]),
#             'matching_skills': set(freelancer_skills.split()) & set(project_skills[int(i)].split())
#         }
#         for i in top_indices if cosine_similarities[i] > 0
#     ]

#     return recommended_projects

def recommend_projects(user, top_n=5):
    try:
        freelancer_profile = FreelancerProfile.objects.get(user=user)
    except FreelancerProfile.DoesNotExist:
        return []

    # Get all open projects
    open_projects = Project.objects.filter(status='open')

    # Create skill vectors
    freelancer_skills = get_skill_vector(freelancer_profile.skills)
    project_skills = [get_skill_vector(project.required_skills) for project in open_projects]

    # If freelancer has no skills or all projects have no skills, return empty list
    if not freelancer_skills or not any(project_skills):
        return []

    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer()
    skill_vectors = vectorizer.fit_transform([freelancer_skills] + project_skills)

    # Calculate cosine similarity
    cosine_similarities = cosine_similarity(skill_vectors[0:1], skill_vectors[1:]).flatten()

    # Get top N similar projects
    top_indices = cosine_similarities.argsort()[-top_n:][::-1]
    
    recommended_projects = [
        {
            'project': open_projects[int(i)],
            'similarity_score': float(cosine_similarities[i]) * 100,  # Convert to percentage
            'matching_skills': set(freelancer_skills.split()) & set(project_skills[int(i)].split())
        }
        for i in top_indices if cosine_similarities[i] > 0
    ]

    return recommended_projects