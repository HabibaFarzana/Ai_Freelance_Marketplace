from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from projects.models import Project
from accounts.models import FreelancerProfile, Skill
from .dynamic_pricing import train_pricing_model, get_price_recommendation
from .project_matching import match_project_to_freelancers

class AiFeaturesTestCase(TestCase):
    def setUp(self):
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
            deadline=timezone.now() + timezone.timedelta(days=7)
        )

    def test_dynamic_pricing(self):
        model = train_pricing_model([self.project])
        recommendation = get_price_recommendation(model, self.project, self.freelancer_user)
        self.assertIsInstance(recommendation, float)
        self.assertTrue(0 < recommendation < 10000)  # Assuming a reasonable price range

    def test_project_matching(self):
        matches = match_project_to_freelancers(self.project, [self.freelancer_user])
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0][0], self.freelancer_user)
        self.assertIsInstance(matches[0][1], float)
        self.assertTrue(0 <= matches[0][1] <= 1)  # Similarity score should be between 0 and 1