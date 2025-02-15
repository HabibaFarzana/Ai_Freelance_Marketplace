from django.core.management.base import BaseCommand
from datasets import load_dataset
from projects.models import Project
from accounts.models import Client

class Command(BaseCommand):
    help = "Import project data from Hugging Face dataset"

    def handle(self, *args, **kwargs):
        # Load the dataset
        dataset = load_dataset("ayesha08/pake-freelancer-dataset", split="train")

        # Iterate through the dataset and populate the database
        for row in dataset:
            try:
                # Create a client if not already existing
                client, created = Client.objects.get_or_create(
                    name=row['client_name'],  # Assuming 'client_name' is a column in the dataset
                    defaults={'email': f"{row['client_name']}@example.com"}  # Add default data if needed
                )

                # Create a project linked to the client
                Project.objects.create(
                    client=client,
                    title=row['project_title'],  # Assuming 'project_title' is a column
                    description=row['description'],  # Assuming 'description' is a column
                    required_skills=row['skills'].split(','),  # Assuming 'skills' is a comma-separated string
                    budget=row['budget'],  # Assuming 'budget' is a column
                    min_experience_years=row['min_experience_years']  # Assuming 'min_experience_years' is a column
                )
            except Exception as e:
                self.stderr.write(f"Error importing row: {e}")
                continue

        self.stdout.write("Dataset imported successfully!")
