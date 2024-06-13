from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUserModel

class CustomUserAdmin(UserAdmin):
    model = CustomUserModel
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'bio', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

# Register the custom user model with the admin site
admin.site.register(CustomUserModel, CustomUserAdmin)

print("CustomUserModel registered in admin: ", admin.site.is_registered(CustomUserModel))
