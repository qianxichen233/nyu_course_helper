from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class Course(models.Model):
    course_type=models.CharField(max_length=255)
    course_num=models.IntegerField()
    school=models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.course_type+' '+str(self.course_num)

class Professor(models.Model):
    professor_name=models.CharField(max_length=255)
    school=models.CharField(max_length=255, blank=True, null=True)
    rate=models.FloatField(blank=True, null=True)
    level_of_diff=models.FloatField(blank=True, null=True)
    take_again=models.CharField(max_length=255, blank=True, null=True)

class CourseSection(models.Model):
    course_belong=models.ForeignKey(Course, on_delete=models.CASCADE)
    term=models.CharField(max_length=255, blank=True, null=True)
    course_id=models.IntegerField(unique=True)
    section_num=models.CharField(max_length=255, blank=True, null=True)
    class_status=models.CharField(max_length=255, blank=True, null=True)
    instruction_mode=models.CharField(max_length=255, blank=True, null=True)
    professor=models.ManyToManyField(Professor, related_name="teach", blank=True)
    location=models.CharField(max_length=255, blank=True, null=True)
    credit=models.IntegerField(blank=True, null=True)
    pre_requisites=models.ManyToManyField(Course, related_name="pre_requisites", blank=True)
    co_requisites=models.ManyToManyField(Course, related_name="co_requisites", blank=True)
    anti_requisites=models.ManyToManyField(Course, related_name="anti_requisites", blank=True)
    course_time_day=models.CharField(max_length=10, blank=True, null=True)
    course_time_st=models.CharField(max_length=10, blank=True, null=True)
    course_time_ed=models.CharField(max_length=10, blank=True, null=True)
    course_component=models.CharField(max_length=10, blank=True, null=True)

class CustomAccountManager(BaseUserManager):
    def create_superuser(self, email, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        return self.create_user(email=email,password=password, **other_fields)

    def create_user(self, username, email, password, **other_fields):
        if not email:
            raise ValueError('No Email address')
        email=self.normalize_email(email)
        user=self.model(email=email, username=username, **other_fields)
        user.set_password(password)
        user.save()
        return user
    
class MyUser(AbstractBaseUser, PermissionsMixin):
    email=models.EmailField(unique=True)
    username=models.CharField(max_length=255, unique=True)
    MyField=models.CharField(max_length=255, default='')
    Course_list=models.ManyToManyField(Course)
    start_date=models.DateField(default=timezone.now)
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=False)
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username']

    objects=CustomAccountManager()
    
    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj=None):
        return self.is_staff
    
    def has_module_perms(self, app_label):
        return True