from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from projects.models import Project
from accounts.models import FreelancerProfile, Skill

class ApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.User = get_user_model()
        self.client_user = self.User.objects.create_user(
            username='client',
            email='client@test.com',
            password='testpass123',
            user_type='client'
        )
        self.freelancer_user = self.User.objects.create_user(
            username='freelancer',
            email='freelancer@test.com',
            password='testpass123',
            user_type='freelancer'
        )
        self.skill = Skill.objects.create(name='Python')
        self.freelancer_profile = FreelancerProfile.objects.create(
            user=self.freelancer_user,
            hourly_rate=50.00,
            experience_years=5
        )
        self.freelancer_profile.skills.add(self.skill)
        self.project = Project.objects.create(
            title='Test Project',
            description='This is a test project requiring Python skills',
            client=self.client_user,
            budget=1000.00,
            deadline='2023-12-31'
        )

    def test_project_list(self):
        self.client.force_authenticate(user=self.client_user)
        response = self.client.get(reverse('project-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_submit_bid(self):
        self.client.force_authenticate(user=self.freelancer_user)
        url = reverse('project-submit-bid', kwargs={'pk': self.project.id})
        data = {
            'amount': 900.00,
            'proposal': 'I can do this project efficiently.'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_price_recommendation(self):
        self.client.force_authenticate(user=self.freelancer_user)
        url = reverse('project-get-price-recommendation', kwargs={'pk': self.project.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('price_recommendation', response.data)

    def test_match_freelancers(self):
        self.client.force_authenticate(user=self.client_user)
        url = reverse('project-match-freelancers', kwargs={'pk': self.project.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only one freelancer in the system