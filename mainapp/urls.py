from django.urls import path
from . import views

urlpatterns=[
    path('',views.index,name='index'),
    path('register',views.register,name='register'),
    path('login',views.login,name='login'),
    path('logout',views.logout,name='logout'),
    path('profile/<str:username>',views.profile, name='profile'),
    path('addcourse',views.addcourse,name='addcourse'),
    path('deletecourse',views.deletecourse,name='deletecourse'),
    path('courseschedule',views.courseschedule,name='courseschedule'),
    path('calculate_course',views.calculate_course,name='calculate_course')
]