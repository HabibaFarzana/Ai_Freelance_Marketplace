import cv2
import numpy as np
from django.conf import settings
import os

def process_screenshot(screenshot):
    # Convert the screenshot to a numpy array
    nparr = np.frombuffer(screenshot.read(), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Perform some basic image processing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)

    # Count the number of edges as a simple metric of activity
    activity_level = np.sum(edges) / 255

    return activity_level

def analyze_work_session(screenshots):
    activity_levels = [process_screenshot(screenshot) for screenshot in screenshots]
    average_activity = sum(activity_levels) / len(activity_levels)
    
    if average_activity > 1000:
        return "High activity"
    elif average_activity > 500:
        return "Moderate activity"
    else:
        return "Low activity"

def generate_feedback(activity_level, time_spent):
    if activity_level == "High activity":
        return f"Great job! You've been very productive in the last {time_spent} minutes."
    elif activity_level == "Moderate activity":
        return f"You've been working steadily for {time_spent} minutes. Keep it up!"
    else:
        return f"Your activity level seems low for the past {time_spent} minutes. Is everything okay?"