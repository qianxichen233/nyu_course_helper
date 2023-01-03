# nyu course scheduler
---
A simple web page build with Django that can fetch course information from nyu course search page, integrated with information on https://www.ratemyprofessors.com to display all the avaliable course schedules sorted by average professor rating
# Features
- enter all the courses (eg. CS-UY 1134) you want to take, and confirm, all schedules will be presented with beautiful charts from 8:00 to 20:00. Schedules are sorted by average professor rating fetched from ratemyprofessors, and can be swtiched by pressing left/right arrow or click corresponding buttons.
- Support filters that can hidden schedules that contains specific time range.
- More detailed information of each course sections including professor name/rating, location, etc are also avaliable on the charts.

# Limitation
- delay for each request is huge (around 20-30 seconds) since when the requested course is not stored in the database, a new crawler will be started to fetch course information.
- (2023-1-2) professor rating function is not working due to changes in the ratemyprofessors website's structure and api.
