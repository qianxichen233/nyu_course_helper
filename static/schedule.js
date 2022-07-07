var schedule_index=0;
var course_schedules;

var page_index_map=[];
var page_index_map_index=0;

var break_times_set=[]

var week_map={
    'mon':'1',
    'tue':'2',
    'wed':'3',
    'thu':'4',
    'fri':'5'
};

var color_table=['#588093','#433352','#a2b9b2','#f6b065','#C0362C','#FF9642','#816C5B','#668D3C','#0097AC','#3CD6E6','#007996'];

var fixed_course=[];

var course_add_status=0;

function convert_to_min(time)
{
    var minutes=0;
    if(time.split(' ')[1]=="PM") minutes=720;
    tmp=time.split(' ')[0].split('.');
    if(tmp[0]!="12")
        minutes+=60*parseInt(tmp[0]);
    minutes+=parseInt(tmp[1]);
    return minutes;
}

function convert_to_time_str(st, ed)
{
    st_hour=parseInt(st/60);
    st_min=st%60;
    ed_hour=parseInt(ed/60);
    ed_min=ed%60;
    return (st_hour<10?"0":"")+String(st_hour)+":"+(st_min<10?"0":"")+String(st_min)+"-"+(ed_hour<10?"0":"")+String(ed_hour)+":"+(ed_min<10?"0":"")+String(ed_min);
}

function shuffleArray(array)
{
    for (var i = array.length - 1; i > 0; i--)
    {
        var j = Math.floor(Math.random() * (i + 1));
        var temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

function checkinput()
{
    course=document.getElementById("course_input").value;
    if(course=="")
    {
        document.getElementById("invalid_input_info").innerHTML="";
        checkinputall();
        return;
    }
    const pattern = new RegExp('[A-Z]+-[A-Z]+\\s[0-9]+');
    if(!pattern.test(course))
    {
        document.getElementById("invalid_input_info").innerHTML="Format Does Not Match";
        document.getElementById("AddCoursebtn").disabled=true;
    }
    else
    {
        document.getElementById("invalid_input_info").innerHTML="";
        checkinputall();
    }
}

function checkidinput()
{
    id=document.getElementById("course_id_input").value;
    const pattern = new RegExp('[0-9]+');
    if(id=="")
    {
        document.getElementById("invalid_input_info").innerHTML="";
        checkinputall();
        return;
    }
    if(!pattern.test(id))
    {
        document.getElementById("invalid_input_info").innerHTML="Please Input Valid ID";
        document.getElementById("AddCoursebtn").disabled=true;
    }
    else
    {
        document.getElementById("invalid_input_info").innerHTML="";
        checkinputall();
    }
}

function checkinputall()
{
    //console.log("checkall");
    const pattern1 = new RegExp('[A-Z]+-[A-Z]+\\s[0-9]+');
    const pattern2 = new RegExp('[0-9]+');
    course=document.getElementById("course_input").value;
    id=document.getElementById("course_id_input").value;
    if(course==""||!pattern1.test(course))
    {
        document.getElementById("AddCoursebtn").disabled=true;
        return;
    }
    if(course_add_status&&(id==""||!pattern2.test(id)))
    {
        document.getElementById("AddCoursebtn").disabled=true;
        return;
    }
    //console.log("pass");
    document.getElementById("AddCoursebtn").disabled=false;
}

function add_course()
{
    course=document.getElementById("course_input").value;
    id=document.getElementById("course_id_input").value;
    if(!course_add_status) id="";
    else document.getElementById("AddCoursebtn").disabled=true;
    document.getElementById("course_id_input").value="";

    exists_course=document.getElementsByName('course');
    for(i=0;i<exists_course.length;++i)
    {
        if(course==exists_course[i].value)
        {
            document.getElementById("invalid_input_info").innerHTML=course+" Already Exist!";
            return;
        }
    }

    no_course=document.getElementById("no_course_in_list");
    if(no_course!=null)
        document.getElementById("schedules").removeChild(no_course);

    course_name=course;
    if(course_add_status)
        course_name+=" ("+id+")";

    div=document.createElement("div");
    div.className="course_to_schedule";
    div.innerHTML="<p>"+course_name+"</p><input type=\"hidden\" name=\"course\" value=\""+course+"\"/><input type=\"hidden\" name=\"course_id\" value=\""+id+"\"/><button type=\"button\" onclick=\"delete_course(this)\">Delete</button>";
    submit=document.getElementById("form_submit");
    document.getElementById("schedules").appendChild(div);
    document.getElementById("invalid_course_info").innerHTML="";
}

function delete_course(element)
{
    document.getElementById("schedules").removeChild(element.parentNode);
    if(document.getElementsByName('course').length==0)
    {
        span=document.createElement("span");
        span.id="no_course_in_list";
        span.innerHTML="No Course in List";
        document.getElementById("schedules").appendChild(span);
    }
}

function display_schedule()
{
    if(Object.keys(course_schedules['schedules']).length==0)
        return;
    course_divs=document.getElementsByClassName('event-slot');
    element=document.getElementsByClassName('events-container')[0];
    times=course_divs.length;
    remove_index=0;
    for(i=0;i<times;++i)
    {
        if(course_divs[remove_index].classList.contains('schedule-fixed'))
        {
            ++remove_index;
            continue;
        }
        element.removeChild(course_divs[remove_index]);
    }
    if(document.getElementsByClassName('course_list_button').length>0)
        document.getElementsByClassName("schedule-title")[0].removeChild(document.getElementsByClassName('course_list_button')[0]);
    if(course_schedules['schedules']['schedule'+String(schedule_index)]['avg_rate']==0)
        document.getElementById('display_rating').innerText="Average Professor Rating: N/A";
    else
        document.getElementById('display_rating').innerText="Average Professor Rating: "+String(course_schedules['schedules']['schedule'+String(schedule_index)]['avg_rate'].toFixed(2))+"/5.00";
    target=document.getElementsByClassName("events-container")[0];

    color_index=0;
    shuffleArray(color_table);

    for(i=0;i<course_schedules['schedules']['schedule'+String(schedule_index)]['length'];++i)
    {
        course_name=course_schedules['schedules']['schedule'+String(schedule_index)]['course'+String(i)]['course_name'];
        course_id=course_schedules['schedules']['schedule'+String(schedule_index)]['course'+String(i)]['course_id'];
        flag=false;
        for(j=0;j<fixed_course.length;++j)
            if(fixed_course[j]==String(course_id))
                flag=true;
        if(flag) continue;
        studyday=course_schedules['schedules']['schedule'+String(schedule_index)]['course'+String(i)]['studyday'];
        time_st=course_schedules['schedules']['schedule'+String(schedule_index)]['course'+String(i)]['time_st'];
        st_min=convert_to_min(time_st);
        time_ed=course_schedules['schedules']['schedule'+String(schedule_index)]['course'+String(i)]['time_ed'];
        ed_min=convert_to_min(time_ed);
        component=course_schedules['schedules']['schedule'+String(schedule_index)]['course'+String(i)]['component'];
        instruction_mode=course_schedules['schedules']['schedule'+String(schedule_index)]['course'+String(i)]['instruction_mode'];
        loc=course_schedules['schedules']['schedule'+String(schedule_index)]['course'+String(i)]['location'];
        class_status=course_schedules['schedules']['schedule'+String(schedule_index)]['course'+String(i)]['class_status'];
        studydays=studyday.split(',');
        for(j=0;j<studydays.length;++j)
        {
            div=document.createElement('div');
            div.className="event-slot";
            div.setAttribute("onclick","fix_schedule(this);");
            wid=100/(6-parseInt(week_map[studydays[j].toLowerCase()]));
            css=('height: '+String(ed_min-st_min)+'px;')+('grid-column: '+week_map[studydays[j].toLowerCase()]+';')+('grid-row: '+String((st_min-480)/10+1)+';')+('width:'+String(wid)+'%;')+('background-color:')+color_table[color_index]+';';
            div.style.cssText=css;
            div2=document.createElement('div');
            div2.className="schedule-overview";
            span_1=document.createElement('span');
            span_2=document.createElement('span');
            span_1.innerHTML=course_name+" ("+String(course_id)+")";
            span_2.innerHTML=component;
            div2.appendChild(span_1);
            div2.appendChild(document.createElement('br'));
            div2.appendChild(span_2);
            div.appendChild(div2);

            div3=document.createElement('div');
            div3.className="schedule-detail";
            div3.style.cssText+="background-color: "+color_table[color_index]+';';
            span_3=document.createElement('span');
            span_3.innerHTML=time_st.replace('.',':')+"-"+time_ed.replace('.',':');
            span_4=document.createElement('span');
            span_4.innerHTML="Instruction Mode: "+instruction_mode;
            span_5=document.createElement('span');
            span_5.innerHTML="Location: "+loc;
            span_6=document.createElement('span');
            span_6.innerHTML="Class Status: ";
            span_7=document.createElement('span');
            span_7.innerHTML=class_status;
            div3.appendChild(span_3);div3.appendChild(document.createElement('br'));
            div3.appendChild(span_4);div3.appendChild(document.createElement('br'));
            div3.appendChild(span_5);div3.appendChild(document.createElement('br'));
            div3.appendChild(span_6);div3.appendChild(span_7);div3.appendChild(document.createElement('br'));

            if(course_schedules['schedules']['schedule'+String(schedule_index)]['course'+String(i)]['professor']['length']==0)
            {
                span=document.createElement('span');
                span.innerHTML="No Professor";
                div3.appendChild(span);div3.appendChild(document.createElement('br'));
            }
            else
            {
                span=document.createElement('span');
                span.innerHTML="Professor(s):";
                div3.appendChild(span);div3.appendChild(document.createElement('br'));
            }

            for(k=0;k<course_schedules['schedules']['schedule'+String(schedule_index)]['course'+String(i)]['professor']['length'];++k)
            {
                professor_name=course_schedules['schedules']['schedule'+String(schedule_index)]['course'+String(i)]['professor']['professor'+String(k)]['professor_name'];
                if(course_schedules['schedules']['schedule'+String(schedule_index)]['course'+String(i)]['professor']['professor'+String(k)]['professor_rating']==null)
                    professor_rating="N/A";
                else professor_rating=String(course_schedules['schedules']['schedule'+String(schedule_index)]['course'+String(i)]['professor']['professor'+String(k)]['professor_rating'].toFixed(1))+"/5.0";
                span=document.createElement('span');
                span.innerHTML=professor_name+" | "+professor_rating;
                div3.appendChild(span);div3.appendChild(document.createElement('br'));
            }

            div.appendChild(div3);

            target.appendChild(div);
        }
        color_index++;
        if(color_index>=color_table.length) color_index=0;
    }

    for(i=0;i<break_times_set.length;++i)
    {
        div=document.createElement('div');
        div.className="event-slot";
        wid=100/(6-parseInt(week_map[break_times_set[i]['day'].toLowerCase()]));
        css=('height: '+String(break_times_set[i]['ed']-break_times_set[i]['st'])+'px;')+('grid-column: '+week_map[break_times_set[i]['day'].toLowerCase()]+';')+('grid-row: '+String((break_times_set[i]['st']-480)/10+1)+';')+('width:'+String(wid)+'%;')+('background-color:')+color_table[color_index]+';';
        div.style.cssText=css;
        div2=document.createElement('div');
        div2.className="schedule-overview";
        span_1=document.createElement('span');
        span_2=document.createElement('span');
        span_1.innerHTML="Break";
        span_2.innerHTML=convert_to_time_str(break_times_set[i]['st'],break_times_set[i]['ed']);
        div2.appendChild(span_1);
        div2.appendChild(document.createElement('br'));
        div2.appendChild(span_2);
        div.appendChild(div2);
        target.appendChild(div);
    }

    div2=document.createElement("div");
    div2.className="course_list_button";
    total=Object.keys(course_schedules['schedules']).length;
    div2.innerHTML="<button type=\"button\" id=\"pre_btn\" onclick=\"add_schedule_index(-1)\">&#8249;</button><span>"+String(page_index_map_index+1)+"/"+String(page_index_map.length)+"</span><button type=\"button\" id=\"nxt_btn\" onclick=\"add_schedule_index(1)\">&#8250;</button>";
    document.getElementsByClassName("schedule-title")[0].appendChild(div2);
    if(Object.keys(course_schedules['schedules']).length==1)
        document.getElementById('nxt_btn').disabled=true;
}

function course_schedule()
{
    if(document.getElementsByName('course').length==0)
    {
        document.getElementById("invalid_course_info").innerHTML="Please Add At Least One Course";
        return;
    }
    schedule_index=0;
    course_divs=document.getElementsByClassName('event-slot');
    element=document.getElementsByClassName('events-container')[0];
    times=course_divs.length;
    for(i=0;i<times;++i)
    {
        if(course_divs[0].classList.contains('schedule-fixed'))
            continue;
        element.removeChild(course_divs[0]);
    }
    if(document.getElementsByClassName('course_list_button').length>0)
    document.getElementsByClassName("schedule-title")[0].removeChild(document.getElementsByClassName('course_list_button')[0]);
    document.getElementById('display_rating').innerText="";
    elements=document.getElementsByClassName('course_to_schedule');
    data={}
    for(i=0;i<elements.length;++i)
    {
        tmp={}
        tmp['course_name']=elements[i].getElementsByTagName("input")[0].value;
        tmp['course_id']=elements[i].getElementsByTagName("input")[1].value;
        data['course'+String(i)]=tmp;
    }
    data['ign_loc']=document.getElementById('ign_loc').checked;
    data['ign_pro']=document.getElementById('ign_pro').checked;
    data['ign_stat']=document.getElementById('ign_stat').checked;
    data['ear_time']=document.getElementById('earliest_time').value;
    data['lte_time']=document.getElementById('latest_time').value;
    break_times={}
    breaks=document.getElementsByClassName("break-interval");
    break_times['length']=breaks.length;
    for(i=0;i<breaks.length;++i)
    {
        tmp={}
        tmp['day']=breaks[i].innerText.split(' ')[0];
        interval=breaks[i].innerText.split(' ')[1].split('\n')[0].split('-');
        tmp['st']=parseInt(interval[0].split(':')[0])*60+parseInt(interval[0].split(':')[1]);
        if(tmp['st']<480) tmp['st']=480;
        tmp['ed']=parseInt(interval[1].split(':')[0])*60+parseInt(interval[1].split(':')[1]);
        if(tmp['ed']<480) tmp['ed']=480;
        break_times_set.push(tmp);
        break_times["break"+String(i)]=tmp;
    }
    data['break_interval']=break_times;
    //console.log(data)
    document.getElementsByClassName("loading-scene")[0].classList.add("active");
    //document.getElementById('info_display').innerHTML='loading';
    fetch('calculate_course', {
        method: 'POST',
        credentials: 'same-origin',
        headers:{
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken,
    },
        body: JSON.stringify(data)
    })
    .then(response => {
        if(!response.ok) throw new Error();
        return response.json()
    })
    .then(data => {
        if(Object.keys(data['schedules']).length!=0)
            document.getElementsByClassName("loading-scene")[0].classList.remove("active");
        else document.getElementById('info_display').innerHTML='No Available Schedule';
        course_schedules=data;
        //console.log(course_schedules)
        map_index();
        display_schedule();
    }).catch(err =>{
        console.log("Unknown Problem");
    });
}

function add_schedule_index(increment)
{
    index_tmp=schedule_index;
    page_index_map_index+=increment;
    if(page_index_map_index<=0)
    {
        document.getElementById('pre_btn').setAttribute("disabled","disabled");
        if(page_index_map_index!=0)
        {
            page_index_map_index=0;
            return;
        }
    }
    else document.getElementById('pre_btn').removeAttribute("disabled");
    if(page_index_map_index>=page_index_map.length-1)
    {
        document.getElementById('nxt_btn').setAttribute("disabled","disabled");
        if(page_index_map_index!=page_index_map.length-1)
        {
            page_index_map_index=page_index_map.length-1;
            return;
        }
    }
    else document.getElementById('nxt_btn').removeAttribute("disabled");
    schedule_index=page_index_map[page_index_map_index];
    display_schedule();
}

document.onkeydown = function(evt)
{
    if(evt.keyCode==37)
        add_schedule_index(-1);
    else if(evt.keyCode==39)
        add_schedule_index(1);
}

function fix_schedule(ele)
{
    course_id=ele.getElementsByTagName('span')[0].innerHTML.split(' ')[2];
    course_id=course_id.substring(1,course_id.length-1);
    if(ele.classList.contains('schedule-fixed'))
    {
        course_divs=document.getElementsByClassName('event-slot');
        for(i=0;i<course_divs.length;++i)
        {
            if(course_divs[i].getElementsByTagName('span')[0].innerHTML=="Break") continue;
            course_id_tmp=course_divs[i].getElementsByTagName('span')[0].innerHTML.split(' ')[2];
            course_id_tmp=course_id_tmp.substring(1,course_id_tmp.length-1);
            if(course_id_tmp==course_id)
                course_divs[i].classList.remove('schedule-fixed');
        }
        for(i=0;i<fixed_course.length;++i)
        {
            if(fixed_course[i]==course_id)
            {
                fixed_course.splice(i,1);
                break;
            }
        }
    }
    else
    {
        course_divs=document.getElementsByClassName('event-slot');
        for(i=0;i<course_divs.length;++i)
        {
            if(course_divs[i].getElementsByTagName('span')[0].innerHTML=="Break") continue;
            course_id_tmp=course_divs[i].getElementsByTagName('span')[0].innerHTML.split(' ')[2];
            course_id_tmp=course_id_tmp.substring(1,course_id_tmp.length-1);
            if(course_id_tmp==course_id)
                course_divs[i].classList.add('schedule-fixed');
        }
        fixed_course.push(course_id);
    }
    map_index(schedule_index);
    document.getElementsByClassName('course_list_button')[0].innerHTML="<button type=\"button\" id=\"pre_btn\" onclick=\"add_schedule_index(-1)\">&#8249;</button><span>"+String(page_index_map_index+1)+"/"+String(page_index_map.length)+"</span><button type=\"button\" id=\"nxt_btn\" onclick=\"add_schedule_index(1)\">&#8250;</button>";
}

function map_index(current_index)
{
    page_index_map=[];
    for(i=0;i<Object.keys(course_schedules['schedules']).length;++i)
    {
        cnt=0;
        if(fixed_course.length>0)
        {
            for(j=0;j<course_schedules['schedules']['schedule'+String(i)]['length'];++j)
            {
                id=course_schedules['schedules']['schedule'+String(i)]['course'+String(j)]['course_id'];
                for(k=0;k<fixed_course.length;++k)
                {
                    if(fixed_course[k]==String(id))
                    {
                        ++cnt;
                        break;
                    }
                }
            }
        }
        if(cnt==fixed_course.length)
        {
            if(current_index==i)
                page_index_map_index=page_index_map.length;
            page_index_map.push(i);
        }
    }
}

function add_break_time()
{
    break_day=document.getElementById("break_day").value;
    break_st=document.getElementById("break_st").value;
    break_ed=document.getElementById("break_ed").value;
    no_break=document.getElementById("no_break_in_list");
    if(no_break!=null)
        document.getElementsByClassName("break-interval-container")[0].removeChild(no_break);
    div=document.createElement("div");
    div.className="break-interval";
    div.innerHTML="<p>"+break_day+" "+String(break_st)+"-"+String(break_ed)+"</p><button type=\"button\" onclick=\"delete_break_time(this);\">Delete</button>";
    document.getElementsByClassName("break-interval-container")[0].appendChild(div);
}

function delete_break_time(element)
{
    document.getElementsByClassName("break-interval-container")[0].removeChild(element.parentNode);
    if(document.getElementsByClassName("break-interval").length==0)
    {
        span=document.createElement("span");
        span.id="no_break_in_list";
        span.innerHTML="No Breaks Specified";
        document.getElementsByClassName("break-interval-container")[0].appendChild(span);
    }
}

function switch_course_add()
{
    document.getElementById("invalid_input_info").innerHTML="";
    if(course_add_status)
    {
        document.getElementById("course_id_input").classList.remove("active");
        document.getElementsByClassName("add_course_switch")[0].innerText="Add Course With Course ID";
        document.getElementById("course_id_input").style="display: none;";
        document.getElementById("course_id_input").value="";
    }
    else
    {
        document.getElementById("course_id_input").classList.add("active");
        document.getElementsByClassName("add_course_switch")[0].innerText="Add Course With Course Num.";
        document.getElementById("course_id_input").style="display: inline-block;";
        document.getElementById("AddCoursebtn").disabled=true;
    }
    course_add_status^=1;
    checkinputall();
}

