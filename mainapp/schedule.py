from prometheus_client import Info
from notifications.course_crawler import crawler
from copy import deepcopy
from .models import *

def generate_schedule(courses: list, options: dict):
    courses_info=[]
    possible_schedule=[]
    schedule_tmp=[]
    def my_sort(elem):
        return elem['avg_rate']

    def convert_time(time: str):
        if(time[-2:]=='PM'):
            min=720
        else:
            min=0
        time=time[:-3]
        min+=int(time.split('.')[0])*60
        min+=int(time.split('.')[1])
        return min

    def dfs(index: int):
        #print(f'index={index}')
        if(index==len(courses_info)):
            #print('append',end=' ')
            #print(schedule_tmp)
            possible_schedule.append(deepcopy(schedule_tmp))
            return
        for i in range(len(courses_info[index])):
            flag=False
            for j in range(len(schedule_tmp)):
                if(set(courses_info[index][i].course_time_day.split(','))&set(courses_info[j][schedule_tmp[j]].course_time_day.split(','))):
                    st0=convert_time(courses_info[index][i].course_time_st)
                    ed0=convert_time(courses_info[index][i].course_time_ed)
                    st1=convert_time(courses_info[j][schedule_tmp[j]].course_time_st)
                    ed1=convert_time(courses_info[j][schedule_tmp[j]].course_time_ed)
                    if(st1<=st0<ed1 or st0<=st1<ed0):
                        flag=True
                        break
            if(flag):
                continue
            schedule_tmp.append(i)
            dfs(index+1)
            schedule_tmp.pop()
    #add non-exist course into the database
    new_courses=[]
    for course in courses:
        course_type=course['course_name'][:course['course_name'].find(' ')]
        course_num=course['course_name'][course['course_name'].find(' ')+1:]
        if(not Course.objects.filter(course_type=course_type, course_num=course_num).exists()):
            new_courses.append(deepcopy(course['course_name']))
    if(len(new_courses)>0):
        new_courses.sort()
        my_crawler=crawler()
        my_crawler.add_courses(new_courses)
        my_crawler.update_professor()

    #collect course information from database
    for course in courses:
        course_type=course['course_name'][:course['course_name'].find(' ')]
        course_num=course['course_name'][course['course_name'].find(' ')+1:]
        course_id=course['course_id']
        if(course_id!=""):
            if(not CourseSection.objects.filter(course_id=course_id).exists()):
                #cannot find the course id
                continue
            section=CourseSection.objects.filter(course_id=course_id).get()
            course_info=[section]
            courses_info.append(course_info)
            continue
        if(Course.objects.filter(course_type=course_type, course_num=course_num).exists()):
            components=Course.objects.filter(course_type=course_type, course_num=course_num).get().coursesection_set.all().values('course_component').distinct()
            for component in components:
                course_info=[]
                for section in Course.objects.filter(course_type=course_type, course_num=course_num).get().coursesection_set.filter(course_component=component['course_component']):
                    st_time=convert_time(section.course_time_st)
                    ed_time=convert_time(section.course_time_ed)
                    flag=False
                    for i in range(options['break_interval']['length']):
                        if(options['break_interval']['break'+str(i)]['day'] not in section.course_time_day.split(',')):
                            continue
                        if(options['break_interval']['break'+str(i)]['st']<ed_time<options['break_interval']['break'+str(i)]['ed'] or
                           st_time<options['break_interval']['break'+str(i)]['ed']<ed_time):
                            flag=True
                            break
                    if(flag):
                        continue
                    if((not options['ign_stat']) and section.class_status!='Open'):
                        continue
                    if(st_time<options['ear_time'] or
                       ed_time>options['lte_time']):
                        continue
                    for each_course in course_info:
                        if(each_course.course_time_day==section.course_time_day and
                           each_course.course_time_st==section.course_time_st and
                           each_course.course_time_ed==section.course_time_ed and
                           (options['ign_loc'] or each_course.location==section.location)):
                            flag=True
                            break
                    if(flag):
                        continue
                    course_info.append(section)
                courses_info.append(course_info)

    #print(courses_info)

    #brute force method
    dfs(0)
    
    res=[]
    for schd in possible_schedule:
        #print(schd)
        tmp=[]
        info={}
        sum=0
        cnt=0
        for i in range(len(schd)):
            #print(courses_info[i][schd[i]])
            info['course_id']=courses_info[i][schd[i]].course_id
            info['studyday']=courses_info[i][schd[i]].course_time_day
            info['time_st']=courses_info[i][schd[i]].course_time_st
            info['time_ed']=courses_info[i][schd[i]].course_time_ed
            info['component']=courses_info[i][schd[i]].course_component
            if(courses_info[i][schd[i]].location==None):
                info['location']="Unspecified"
            else:
                info['location']=courses_info[i][schd[i]].location
            info['instruction_mode']=courses_info[i][schd[i]].instruction_mode
            info['course_name']=courses_info[i][schd[i]].course_belong.course_type+' '+str(courses_info[i][schd[i]].course_belong.course_num)
            professor_info={}
            professor_index=0
            for professor in courses_info[i][schd[i]].professor.all():
                each_professor={}
                each_professor['professor_name']=professor.professor_name
                each_professor['professor_rating']=professor.rate
                professor_info['professor'+str(professor_index)]=each_professor
                professor_index+=1
            professor_info['length']=professor_index
            info['professor']=professor_info
            info['class_status']=courses_info[i][schd[i]].class_status

            tmp.append(deepcopy(info))
            if(CourseSection.objects.filter(course_id=info['course_id']).get().professor.count()==0):
                continue
            max_rate=-1
            for professor in CourseSection.objects.filter(course_id=info['course_id']).get().professor.all():
                if(professor.rate==None):
                    continue
                max_rate=max(max_rate, professor.rate)
            if(max_rate==-1):
                continue
            sum+=max_rate
            cnt+=1
        res.append({'schedule':deepcopy(tmp),'avg_rate':sum/cnt if cnt!=0 else 0})
    res.sort(key=my_sort, reverse=True)
    return res
