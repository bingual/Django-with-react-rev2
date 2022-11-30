from django.contrib import admin

from accounts.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['pk', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser']
    list_display_links = ['username']
