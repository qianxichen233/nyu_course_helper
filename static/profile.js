function check_course_format()
{
    course=document.getElementById('course').value;
    pattern=/^[A-Z]+-[A-Z]+\s+[0-9]+$/
    if(!pattern.test(course))
    {
        document.getElementById('course_format_hint').innerHTML='Course Format Does Not Match';
        document.querySelector('[value="Add"]').disabled=true;
    }
    else
    {
        document.getElementById('course_format_hint').innerHTML='';
        document.querySelector('[value="Add"]').disabled=false;
    }
}