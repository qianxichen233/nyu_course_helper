from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.

class UserAdminConfig(UserAdmin):
    ordering=('start_date',)
    list_display=('email', 'username', 'is_active', 'is_staff')
    fieldsets=((None, {'fields':('email','username')}),
                ('Permissions',{'fields':('is_staff','is_active')}),
                ('Personal',{'fields':('Course_list',)}))
    add_fieldsets=(
        (None, {'classes':('wide',),
                'fields':('email','username','first_name', 'password','is_active','is_staff')}),
    )

admin.site.register(MyUser,UserAdminConfig)
admin.site.register(Course)
admin.site.register(CourseSection)
admin.site.register(Professor)