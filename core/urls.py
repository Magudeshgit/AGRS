from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("submit/", views.submit_complaint, name="submit_complaint"),
    path("mine/", views.mine_complaints, name="mine_complaints"),
    path('department/', views.department_dashboard, name='department_dashboard'),
    path('department/respond/<int:complaint_id>/', views.respond_to_complaint, name='respond_complaint'),
    path('respond/<int:complaint_id>/', views.respond_to_complaint, name='respond_complaint'),
    path('department/', views.department_dashboard, name='department_dashboard'),
    path('complaint/<int:complaint_id>/resolve/', views.mark_resolved, name='mark_resolved'),
    path('complaint/<int:complaint_id>/escalate/', views.escalate_complaint, name='escalate_complaint'),
    path("complaint/<int:complaint_id>/acknowledge/", views.acknowledge_complaint, name="acknowledge_complaint"),
    path('fetch_emails/', views.fetch_emails_view, name='fetch_emails'),
]
