import sys
import requests
from bs4 import BeautifulSoup
import config
# Request data
INIT_URL = 'https://course.nuk.edu.tw/Sel/SelectMain1.asp'
RESULT_URL = "https://course.nuk.edu.tw/Sel/roomlist1.asp"
try:
    username = sys.argv[1]
    passwd = sys.argv[2]
except IndexError:
    print("帳號密碼輸入有誤")
    exit()
loginData = {
    "Account":sys.argv[1],
    "Password":sys.argv[2],
    "B1":"登　　入"
}
data = ""

print("Requesting data....")
s = requests.Session()
req = s.post(INIT_URL, verify=False, data=loginData)
req.encoding = "big5"
# print(req.text)
req2 = s.get(RESULT_URL, verify=False)
req2.encoding = "big5"
# print(req2.text)
data = req2.text
# with open("index.html", mode="w") as f:
#     f.write(req2.text)

firstWeekMonDate = input("第一周的星期一之日期(預設為20190909):")
if firstWeekMonDate == "" : firstWeekMonDate = "20190909"
endWeekFriDate = input("最後一周的星期五之日期(預設為20200110):")
if endWeekFriDate == "" : endWeekFriDate = "20200110"
print("Parsing data....")

soup = BeautifulSoup(data, "html.parser")
soup = soup.select("tr")[1:]
course = {}
result = {}
for rowIdx, row in enumerate(soup):
    col = row.select("td")
    col_a = row.select("td a")
    for colIdx, ele in enumerate(col):
        if ele.text == "　": continue
        if "href" in str(ele):
            result[str(ele).split("<br/>")[-2]] = {
                "room":str(ele).split("<br/>")[-1].replace("</td>", ""),
                "id":str(ele).split("<br/>")[-3][str(ele).find('k">')+3:str(ele).find("</a>")]
            }
        if colIdx > 1:
            rowIdxFix = rowIdx
            if rowIdx>5:
                rowIdxFix = rowIdxFix-1
            try:
                course[str(ele).split("<br/>")[-2]].append((colIdx-1, rowIdxFix))
            except:
                course[str(ele).split("<br/>")[-2]] = [(colIdx-1, rowIdxFix)]
for key in course.keys():
    result[key]["time"] = course[key]
# print(result)
print("Generating ics....")

icsResult = ""
for key in result.keys():
    time = result[key]["time"]
    startTime = config.SESSION_INTERVAL[time[0][1]][0]
    endTime = config.SESSION_INTERVAL[time[-1][1]][1]
    # print(key, ":", config.DAY_NAME[time[0][0]], startTime, "~", endTime)
    ics = """
BEGIN:VEVENT
DTSTART;TZID=Asia/Taipei:{}T{}00
DTEND;TZID=Asia/Taipei:{}T{}00
RRULE:FREQ=WEEKLY;UNTIL={}T155959Z;BYDAY={}
DESCRIPTION:{}
LOCATION:{}
SEQUENCE:1
STATUS:CONFIRMED
SUMMARY:{}
TRANSP:OPAQUE
END:VEVENT""".format( str(int(firstWeekMonDate)+int(time[0][0])-1), 
                str(startTime.replace(":","")), 
                str(int(firstWeekMonDate)+int(time[0][0])-1), 
                str(endTime.replace(":","")), 
                str(endWeekFriDate), config.DAY_NAME_ENG[time[0][0]-1], 
                key,
                str(result[key]["room"]), key
    )
    # print(ics)
    icsResult+=ics
    # break
with open('my.ics', 'w', encoding="utf8") as f:
    f.writelines("""BEGIN:VCALENDAR
VERSION:2.0""")
    f.writelines(icsResult)
    f.write("""
END:VCALENDAR""")
