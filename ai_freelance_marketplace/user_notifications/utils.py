# # notifications/utils.py
# from .models import UserNotification

# def create_notification(recipient, notification_type, message, url):
#     return UserNotification.objects.create(
#         recipient=recipient,
#         notification_type=notification_type,
#         message=message,
#         url=url
#     )

# def create_bid_notification(project, bidder):
#     message = f"{bidder.username} submitted a bid for your project: {project.title}"
#     url = f"/projects/{project.id}/"
#     create_notification(project.client, 'bid', message, url)

# def create_hire_notification(project, freelancer):
#     message = f"You've been hired for the project: {project.title}"
#     url = f"/projects/{project.id}/"
#     create_notification(freelancer, 'hire', message, url)

# def create_message_notification(conversation, sender, recipient):
#     message = f"New message from {sender.username}"
#     url = f"/conversation/{conversation.id}/"
#     create_notification(recipient, 'message', message, url)

# def create_file_notification(project, uploader, file_name, action="uploaded"):
#     message = f"{uploader.username} {action} file: {file_name}"
#     url = f"/projects/{project.id}/"
#     for user in [project.client, project.hired_freelancer]:
#         if user != uploader:
#             create_notification(user, 'file', message, url)