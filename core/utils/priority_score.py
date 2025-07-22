import re
import numpy as np
from textblob import TextBlob
from core.models import Complaint

# impact-related keywords
impact_keywords = {
    'college': 20,
    'institute': 20,
    'department': 15,
    'staff': 10,
    'students': 10,
    'lab': 10,
    'hostel': 10,
    'room': 5,
    'my': 2,
    'personal': 2,
}

time_keywords = ['urgent', 'immediately', 'asap', 'now', 'soon', 'emergency']

def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment_score = abs(blob.sentiment.polarity)  # Urgency / tone
    return min(sentiment_score * 100, 100)  # Normalize

def keyword_impact_score(text):
    score = 0
    for word, weight in impact_keywords.items():
        if word in text:
            score += weight
    return min(score, 100)

def similar_complaint_count(title, description):
    text = (title + " " + description).lower()
    count = Complaint.objects.filter(
        description__icontains=title[:15]  # simple pattern match
    ).count()
    return min(count * 10, 100)  # cap at 100

def urgency_keyword_score(text):
    return 30 if any(k in text for k in time_keywords) else 0

def get_user_score(user):
    if user.user_type == "parent":
        return 90
    elif user.user_type == "staff":
        return 70
    else:
        return 50


def calculate_priority_score(title, description, user, category):
    score = 0

    # 1. Urgency based on keywords
    urgency_keywords = ["urgent", "immediately", "emergency", "asap"]
    combined_text = (title + " " + description).lower()
    if any(keyword in combined_text for keyword in urgency_keywords):
        score += 30

    # 2. User score (e.g., student's past complaint count or user type)
    if hasattr(user, 'is_staff') and user.is_staff:
        score += 10  # Less priority for internal complaints
    else:
        score += 20  # More priority for student complaints

    # 3. Department impact based on category
    category_name = category.name.lower() if hasattr(category, 'name') else str(category).lower()
    if "network" in category_name or "server" in category_name:
        score += 30  # College-wide impact
    elif "lab" in category_name or "department" in category_name:
        score += 20  # Dept-level impact
    else:
        score += 10  # Individual impact

    return min(score, 100)  # Cap to 100

