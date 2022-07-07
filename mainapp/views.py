from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.http import JsonResponse
from .models import *
import json
from time import sleep
from .schedule import generate_schedule
from copy import deepcopy

def index(request):
    return render(request,'index.html')

def register(request):
    if(request.method=='POST'):
        if(request.POST['password']!=request.POST['Repassword']):
            messages.info(request,'Password not the same!')
            return redirect('register')
        email=request.POST['email']
        username=request.POST['username']
        password=request.POST['password']
        if(MyUser.objects.filter(email=email).exists()):
            messages.info(request,'Email already exists!')
            return redirect('register')
        if(MyUser.objects.filter(username=username).exists()):
            messages.info(request,'Username already exists!')
            return redirect(register)
        user=MyUser.objects.create_user(username=username, email=email, password=password)
        user.save()
        return redirect('login')
    return render(request, 'register.html')

def login(request):
    if(request.method=='POST'):
        email=request.POST['email']
        password=request.POST['password']
        user=auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('/')
        else:
            messages.info(request,'Incorrect username or password')
            return redirect('login')
    return render(request,'login.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

def profile(request, username):
    if(username==request.user.username):
        course_list=MyUser.objects.filter(username=username).get().Course_list.all()
        return render(request, 'profile.html',{'username':username,'courselist':course_list})
    
def addcourse(request):
    if(request.method=='POST'):
        course=request.POST['course']
        course_type=course[:course.find(' ')]
        course_num=course[course.rfind(' ')+1:]
        try:
            course_obj=Course.objects.filter(course_type=course_type, course_num=course_num).get()
        except:
            course_obj=Course(course_type=course_type, course_num=course_num, school="")
            course_obj.save()
        MyUser.objects.filter(username=request.user.username).get().Course_list.add(course_obj)
        return redirect('profile/'+request.user.username)

def deletecourse(request):
    if(request.method=='POST'):
        course=request.POST['course']
        course_type=course[:course.find(' ')]
        course_num=course[course.rfind(' ')+1:]
        course_obj=Course.objects.filter(course_type=course_type, course_num=course_num).get()
        MyUser.objects.filter(username=request.user.username).get().Course_list.remove(course_obj)
        if course_obj.myuser_set.count() == 0:
            course_obj.delete()
        return redirect('profile/'+request.user.username)

def courseschedule(request):
    return render(request,'schedule.html')

def calculate_course(request):
    if(request.is_ajax()):
        courses=[]
        query=json.load(request)
        try:
            index=0
            while(True):
                courses.append(query['course'+str(index)])
                index+=1
        except:
            pass
        options={}
        options['ign_pro']=query['ign_pro']
        options['ign_loc']=query['ign_loc']
        options['ign_stat']=query['ign_stat']
        options['ear_time']=int(query['ear_time'].split(':')[0])*60+int(query['ear_time'].split(':')[1])
        options['lte_time']=int(query['lte_time'].split(':')[0])*60+int(query['lte_time'].split(':')[1])
        options['break_interval']=query['break_interval']
        schedules=generate_schedule(courses, options)
        #print(schedules)
        all_schedules={}
        index=0
        for schedule in schedules:
            schd={}
            for i in range(len(schedule['schedule'])):
                schd['course'+str(i)]=schedule['schedule'][i]
            schd['avg_rate']=deepcopy(schedule['avg_rate'])
            schd['length']=len(schedule['schedule'])
            all_schedules['schedule'+str(index)]=deepcopy(schd)
            index+=1
        #print(all_schedules)
        #print(index)
        return JsonResponse({'schedules':all_schedules})