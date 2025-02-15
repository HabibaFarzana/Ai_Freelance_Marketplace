from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import FreelancerProfile, ClientProfile, Skill

class AccountsTestCase(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.freelancer = self.User.objects.create_user(
            username='freelancer',
            email='freelancer@test.com',
            password='testpass123',
            user_type='freelancer'
        )
        self.client_user = self.User.objects.create_user(
            username='client',
            email='client@test.com',
            password='testpass123',
            user_type='client'
        )
        self.skill = Skill.objects.create(name='Python')

    def test_user_creation(self):
        self.assertEqual(self.User.objects.count(), 2)
        self.assertEqual(self.freelancer.user_type, 'freelancer')
        self.assertEqual(self.client_user.user_type, 'client')

    def test_freelancer_profile(self):
        profile = FreelancerProfile.objects.create(
            user=self.freelancer,
            hourly_rate=50.00,
            experience_years=5
        )
        profile.skills.add(self.skill)
        self.assertEqual(profile.user, self.freelancer)
        self.assertEqual(profile.skills.count(), 1)
        self.assertEqual(profile.hourly_rate, 50.00)

    def test_client_profile(self):
        profile = ClientProfile.objects.create(
            user=self.client_user,
            company_name='Test Company',
            industry='Technology'
        )
        self.assertEqual(profile.user, self.client_user)
        self.assertEqual(profile.company_name, 'Test Company')
        self.assertEqual(profile.industry, 'Technology')