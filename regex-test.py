import re

pattern="([0-9]{2}\/[0-9]{2}\/[0-9]{4}\s-\s[0-9]{2}\/[0-9]{2}\/[0-9]{4})((\s([A-Za-z,]+)\s([0-9.]+\s(AM|PM)\s-\s[0-9.]+\s(AM|PM)))|())((\sat\s(((?!with).)*))|())((\swith\s(.+))|())\n.*"

backup="09/01/2022 - 12/14/2022 Tue,Wed 3.45 PM - 6.45 PM at 721B 613 with Pellegrini, Ann; Bob, Alex"

text="09/01/2022 - 12/14/2022 at 721B 613"

text+='\n'

res=re.search(pattern,text)

print("weekday:"+(res.group(4) if res.group(4)!=None else "None"))
print("time:"+(res.group(5) if res.group(5)!=None else "None"))
print("location:"+(res.group(11) if res.group(11)!=None else "None"))
print("professor:"+(res.group(16) if res.group(16)!=None else "None"))