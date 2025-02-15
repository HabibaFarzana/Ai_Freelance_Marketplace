from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Project, Bid, Review

class ProjectsTestCase(TestCase):
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
        self.project = Project.objects.create(
            title='Test Project',
            description='This is a test project',
            client=self.client_user,
            budget=1000.00,
            deadline=timezone.now() + timezone.timedelta(days=7)
        )

    def test_project_creation(self):
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(self.project.title, 'Test Project')
        self.assertEqual(self.project.client, self.client_user)

    def test_bid_creation(self):
        bid = Bid.objects.create(
            project=self.project,
            freelancer=self.freelancer_user,
            amount=900.00,
            proposal='This is a test proposal'
        )
        self.assertEqual(Bid.objects.count(), 1)
        self.assertEqual(bid.project, self.project)
        self.assertEqual(bid.freelancer, self.freelancer_user)

    def test_review_creation(self):
        review = Review.objects.create(
            project=self.project,
            reviewer=self.client_user,
            reviewee=self.freelancer_user,
            rating=5,
            comment='Excellent work!'
        )
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(review.project, self.project)
        self.assertEqual(review.reviewer, self.client_user)
        self.assertEqual(review.reviewee, self.freelancer_user)