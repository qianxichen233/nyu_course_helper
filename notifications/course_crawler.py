from mainapp.models import *
from selenium import webdriver
from time import sleep
from copy import deepcopy
from selenium.common.exceptions import TimeoutException
import re

class crawler:
    def __init__(self):
        self.url="https://sis.nyu.edu/psc/csprod/EMPLOYEE/SA/c/NYU_SR.NYU_CLS_SRCH.GBL"
        self.pro_base_url="https://www.ratemyprofessors.com/search/teachers?"
        self.test_url="file:///Users/qianxichen/Desktop/Class_Search2.html"

        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"
        self.options = webdriver.ChromeOptions()
        self.options.headless = True
        self.options.add_argument(f'user-agent={user_agent}')
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--allow-running-insecure-content')
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--proxy-server='direct://'")
        self.options.add_argument("--proxy-bypass-list=*")
        self.options.add_argument("--start-maximized")
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--no-sandbox')
        self.non_exist_course=[]

        self.school_id={
            'NYU':'675',
            'Tandon':'772',
            'Gallatin':'12867',
            'Dentistry':'5165',
            'Steinhardt':'14119',
            'Professional':'5673',
            'Graduate':'17580',
            'Law':'5003',
        }

    def map_school_name(self, school_name):
        for key in self.school_id:
            if(re.search(key, school_name,re.IGNORECASE)):
                return self.school_id[key]
        return self.school_id['NYU']

    def get_error_courses(self):
        tmp=deepcopy(self.non_exist_course)
        self.non_exist_course=[]
        return tmp

    def send_email(self, email, course_type, course_number, class_status):
        print(f"sending email to {email}: status of {course_type} {course_number} has changed to {class_status}")
        
    def get_major(self, driver, course_type):
        for division in driver.find_elements_by_css_selector("#win0divGROUP\$0>div"):
            school=division.find_element_by_class_name('ps_header-group').get_attribute("innerText")
            for major in division.find_elements_by_class_name("ps-link"):
                if(re.search("\("+course_type+"\)",major.get_attribute("innerText"))):
                    return [major,school]
        return None
    
    def get_course_status(self, driver, course_type, course_numbers):
        if(not len(course_numbers)):
            return False
        print(course_type+" ",end='')
        print(course_numbers)
        major=self.get_major(driver,course_type)
        if(major==None):
            print("fail to find "+str(course_type))
            for course_number in course_numbers:
                self.non_exist_course.append(course_type+' '+str(course_number))
            return False
        school=major[1]
        major=major[0]

        major.click()
        sleep(15)
        tmp_course_numbers=deepcopy(course_numbers)
        for course in driver.find_elements_by_css_selector("#win0divSELECT_COURSE\$0>div"):
            course_title=course.find_element_by_css_selector("div>div>div>div>span>b")
            for course_number in course_numbers:
                if(re.search(course_type+" "+str(course_number)+"\s",course_title.get_attribute("innerText"))):
                    if(course_number in tmp_course_numbers):
                        tmp_course_numbers.remove(course_number)
                    try:
                        term=course.find_element_by_css_selector("div.ps_box-edit>span").get_attribute("innerText")
                        #print("term:"+term)
                    except:
                        #print("No Course Offered")
                        break
                    for section in course.find_elements_by_css_selector("div.ps_box-group>div.ps_box-group>div.ps_box-scrollarea>div.ps_box-scrollarea-row>div.ps_box-group>div.ps_box-scrollarea>div.ps_box-scrollarea-row"):
                    #for section_status in course.find_elements_by_css_selector("div[class='ps-htmlarea'] td>div:nth-child(2)>div:nth-child(4)>span:nth-child(2)"):
                        section=section.find_element_by_css_selector("td:nth-child(1)")

                        try:
                            credit=section.find_element_by_css_selector("div:nth-child(1)").get_attribute("innerText")
                            credit=re.search(".*\|\s(.*)\s.*",credit).group(1)
                        except:
                            credit="0"

                        course_id=section.find_element_by_css_selector("div:nth-child(2)>div:nth-child(1)").get_attribute("innerText")
                        course_id=re.search(".*\s([0-9]+)",course_id).group(1)

                        section_num=section.find_element_by_css_selector("div:nth-child(2)>div:nth-child(3)").get_attribute("innerText")
                        section_num=re.search(".*\s(.+)",section_num).group(1)

                        adjust=0
                        additional_info="None"

                        try:
                            class_status=section.find_element_by_css_selector("div:nth-child(2)>div:nth-child(4)>span:nth-child(2)").get_attribute("innerText")
                        except:
                            class_status=section.find_element_by_css_selector("div:nth-child(2)>div:nth-child(5)>span:nth-child(2)").get_attribute("innerText")
                            additional_info=section.find_element_by_css_selector("div:nth-child(2)>div:nth-child(4)").get_attribute("innerText")
                            adjust+=1

                        instruction_mode=section.find_element_by_css_selector(f"div:nth-child(2)>div:nth-child({6+adjust})").get_attribute("innerText")
                        instruction_mode=re.search(".*\s(.+)",instruction_mode).group(1)

                        component=section.find_element_by_css_selector(f"div:nth-child(2)>div:nth-child({8+adjust})").get_attribute("innerText")
                        component=re.search(".*\s(.+)",component).group(1)

                        section_info=section.get_attribute("innerText")+'\n'
                        pattern=".*\n([0-9]{2}\/[0-9]{2}\/[0-9]{4}\s-\s[0-9]{2}\/[0-9]{2}\/[0-9]{4})((\s([A-Za-z,]+)\s([0-9.]+\s(AM|PM)\s-\s[0-9.]+\s(AM|PM)))|())((\sat\s(((?!with).)*))|())((\swith\s(.+))|())\n.*"
                        res=re.search(pattern,section_info)
                        #print(section_info)
                        #print(res)
                        #print(type(res))

                        weekday=res.group(4)
                        time=res.group(5)
                        location=res.group(11)
                        professors=res.group(16)
                        #print(f"weekday:{weekday}")
                        #print(f"time:{time}")
                        #print(f"location:{location}")
                        #print(f"professors:{professors!=None}")

                        if(CourseSection.objects.filter(course_id=int(course_id)).exists()):
                        #if True:
                            section=CourseSection.objects.filter(course_id=int(course_id)).get()
                            print(f"change info of already-exist section(id={course_id})")
                            section.term=term
                            section.section_num=section_num
                            if(section.class_status!=class_status):
                                for user in section.course_belong.myuser_set.all():
                                    self.send_email(email=user.email, course_type=course_type, course_number=course_number, class_status=class_status)
                            section.class_status=class_status
                            section.instruction_mode=instruction_mode
                            section.professor.clear()
                            if(professors):
                                for professor_name in professors.split(';'):
                                    professor_name=professor_name.strip()
                                    if(Professor.objects.filter(professor_name=professor_name, school=self.map_school_name(school)).exists()):
                                        pro=Professor.objects.filter(professor_name=professor_name, school=self.map_school_name(school)).get()
                                    else:
                                        pro=Professor(professor_name=professor_name, school=self.map_school_name(school))
                                        pro.save()
                                    section.professor.add(pro)

                            if(location):
                                section.location=location
                            section.credit=int(credit)
                            if(weekday):
                                section.course_time_day=weekday
                                section.course_time_st=time[:time.find('-')-1]
                                section.course_time_ed=time[time.find('-')+2:]
                            section.course_component=component
                            section.save()
                        else:
                        #else:
                            print(f"create new section(id={course_id})")
                            if(Course.objects.filter(course_type=course_type, course_num=course_number).exists()):
                                belong_course=Course.objects.filter(course_type=course_type, course_num=course_number).get()
                                if(belong_course.school==""):
                                    belong_course.school=self.map_school_name(school)
                                belong_course.save()
                            else:
                                new_course=Course(course_type=course_type, course_num=course_number, school=self.map_school_name(school))
                                new_course.save()
                                belong_course=new_course
                            new_course_section=CourseSection(
                                course_belong=belong_course,
                                term=term,
                                course_id=int(course_id),
                                section_num=section_num,
                                class_status=class_status,
                                instruction_mode=instruction_mode,
                                credit=int(credit),
                                course_component=component,
                            )
                            new_course_section.save()
                            if(professors):
                                for professor_name in professors.split(';'):
                                    professor_name=professor_name.strip()
                                    if(Professor.objects.filter(professor_name=professor_name, school=self.map_school_name(school)).exists()):
                                        pro=Professor.objects.filter(professor_name=professor_name, school=self.map_school_name(school)).get()
                                    else:
                                        pro=Professor(professor_name=professor_name, school=self.map_school_name(school))
                                        pro.save()
                                    new_course_section.professor.add(pro)

                            if(location):
                                new_course_section.location=location
                            if(weekday):
                                new_course_section.course_time_day=weekday
                                new_course_section.course_time_st=time[:time.find('-')-1]
                                new_course_section.course_time_ed=time[time.find('-')+2:]
                            new_course_section.save()
                    break
        for course_number in tmp_course_numbers:
            print("fail to find "+course_type+' '+str(course_number))
            self.non_exist_course.append(course_type+' '+str(course_number))
        return True
        
    def add_courses(self, courses):
        #print(courses)
        driver=webdriver.Chrome(options=self.options)
        driver.get(self.url)
        last_course=""
        course_nums=[]
        course_type=""
        for course in courses:
            try:
                course_tp=course.course_type
                course_nm=course.course_num
            except:
                course_tp=course[:course.find(' ')]
                course_nm=course[course.find(' ')+1:]
            if(course_tp!=last_course):
                if(self.get_course_status(driver=driver,course_type=course_type,course_numbers=course_nums)):
                    driver.find_element_by_id('NYU_CLS_DERIVED_BACK').click()
                    sleep(10)
                course_nums.clear()
                course_type=course_tp
                last_course=course_type
                course_nums.append(course_nm)
            else:
                course_nums.append(course_nm)
        self.get_course_status(driver=driver,course_type=course_type,course_numbers=course_nums)
        driver.quit()
    
    def update_database(self):
        self.add_courses(Course.objects.order_by("course_type"))
        self.update_professor()

    def find_professor(self, driver, professor):
        url=self.pro_base_url+"query="+professor.professor_name.replace(' ', '%20')+"&sid="+professor.school
        print(f'get info of professor {professor.professor_name}')
        try:
            driver.get(url)
        except TimeoutException:
            driver.execute_script("window.stop();")
        try:
            chart=driver.find_element_by_css_selector('.SearchResultsPage__SearchResultsWrapper-sc-1srop1v-1>div:nth-child(3)>a:nth-child(1)')
            rate=chart.find_element_by_class_name('CardNumRating__CardNumRatingNumber-sc-17t4b9u-2').get_attribute("innerText")
            take_again=chart.find_elements_by_class_name('CardFeedback__CardFeedbackItem-lq6nix-1')[0].find_element_by_class_name('CardFeedback__CardFeedbackNumber-lq6nix-2').get_attribute("innerText")
            level=chart.find_elements_by_class_name('CardFeedback__CardFeedbackItem-lq6nix-1')[1].find_element_by_class_name('CardFeedback__CardFeedbackNumber-lq6nix-2').get_attribute("innerText")
            professor.rate=float(rate)
            professor.level_of_diff=float(level)
            professor.take_again=take_again
            professor.save()
        except:
            print("cannot find corresponding professor")
            pass

    def update_professor(self, soft_update=True):
        driver=webdriver.Chrome(options=self.options)
        driver.set_page_load_timeout(6)
        for professor in Professor.objects.all():
            if(soft_update and professor.rate!=None):
                continue
            self.find_professor(driver, professor)
            sleep(5)
        driver.quit()
