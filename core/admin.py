from django.contrib import admin
from .models import *

admin.site.register(Complaint)
admin.site.register(LLMTrainingSample)
admin.site.register(VoiceInput)
admin.site.register(EmailComplaint)
admin.site.register([NotificationLog, WhatsAppLog, department, Response])

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'user_type', 'is_staff', 'contact']
    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('user_type',)}),
    )

admin.site.register(CustomUser)
