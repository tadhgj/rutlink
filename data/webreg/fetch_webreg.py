# for json file parsing
import json

# for saving files
import sys
import os

# for scraping associated webpages
from bs4 import BeautifulSoup

# for making network requests
import requests as requests

# for a pretty terminal progress bar
from tqdm import tqdm

# for parsing dates
import datetime

# for getting the current semester
import read_term_schedule

# for database
import sqlite3
import uuid


# handle command line arguments
import argparse

year = ""
term = ""
schoolcampus = ""

# take -year, -term, -campus
argparser = argparse.ArgumentParser()
argparser.add_argument("-year", help="year to fetch", type=str)
argparser.add_argument("-term", help="term to fetch", type=str)
argparser.add_argument("-campus", help="campus to fetch", type=str)



# set everything not given from args...
schoolcampus = "NB"
arr = read_term_schedule.getTermAndYear()
term = arr[0]
year = arr[1]

# overwrite with args
if len(sys.argv) > 1:
    args = argparser.parse_args()
    if args.year:
        year = args.year
    if args.term:
        term = args.term
    if args.campus:
        schoolcampus = args.campus



print("Year: "+year)
print("Term: "+term)
# continue...

# https://sis.rutgers.edu/soc/api/courses.json?year=2023&term=9&campus=NB
# https://sis.rutgers.edu/soc/api/courses.json?year=2023&term=9&campus=NB
courseURLBase = "https://sis.rutgers.edu/soc/api/courses.json?year="+year+"&term="+term+"&campus="+schoolcampus
# print(courseURLBase)

#download this url
# courseURL = "https://sis.rutgers.edu/soc/api/courses.json?year=2022&term=9&campus=NB,NK,CM"
#              https://sis.rutgers.edu/soc/api/courses.json?year=2022&term=9&campus=NB,NK,CM
#print progress for this download
print("Downloading course data...")
r = requests.get(courseURLBase, stream=True)

total_size_in_bytes= int(r.headers.get('content-length', 0))
block_size = 1024 #1 Kibibyte
progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
with open('temp.json', 'wb') as file:
    for data in r.iter_content(block_size):
        progress_bar.update(len(data))
        file.write(data)
progress_bar.close()
# if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
#     print("ERROR, something went wrong")

print("Download complete.")

# use temp.json...
coursedataJSON = ""
#read test.dat to get json data
with open('temp.json') as json_file:
    coursedataJSON = json.load(json_file)


print("Num of classes: "+str(len(coursedataJSON)))


# set up sqlite...
# set up database
conn = sqlite3.connect('data/webreg/webreg.db')
c = conn.cursor()
# create lots of tables
# table 1:
# name: Teachers
# columns: teacherid, teachername
c.execute("DROP TABLE IF EXISTS Teachers")
c.execute('''CREATE TABLE IF NOT EXISTS Teachers
                (teacherid text, teachername text)''')

# table 2:
# name: Courses
# columns: courseid, shortname, fullname, coursecode, credits
# check if table exists
# if it does, delete it
c.execute("DROP TABLE IF EXISTS Courses")
# if not, create it
c.execute('''CREATE TABLE IF NOT EXISTS Courses
                (courseid text, shortname text, fullname text, coursecode text, credits text)''')

# get number of columns in table
c.execute("SELECT * FROM Courses")
num_cols = len(c.description)
print("num cols: "+str(num_cols))
# print each col
for i in range(num_cols):
    print(c.description[i][0])

# table 3:
# name: TeacherSection
# columns: teacherid, sectionid
c.execute("DROP TABLE IF EXISTS TeacherSection")
c.execute('''CREATE TABLE IF NOT EXISTS TeacherSection
                (teacherid text, sectionid text)''')

# table 4:
# name: Sections
# columns: sectionid, index, isOpen, finalSituation,
c.execute("DROP TABLE IF EXISTS Sections")
c.execute('''CREATE TABLE IF NOT EXISTS Sections
                (sectionid text, sectionindex text, sectionnumber text, isOpen text, finalSituation text)''')

# table 5:
# name: CourseSection
# columns: courseid, sectionid
c.execute("DROP TABLE IF EXISTS CourseSection")
c.execute('''CREATE TABLE IF NOT EXISTS CourseSection
                (courseid text, sectionid text)''')

# table 5.5
# name: CourseCoreCodes:
# columns: courseid, corecode ( like "CC" or "AHo", courseid will repeat)
c.execute("DROP TABLE IF EXISTS CourseCoreCodes")
c.execute('''CREATE TABLE IF NOT EXISTS CourseCoreCodes
                (courseid text, corecode text)''')

# table 6:
# name: Meetings
# columns: meetingid, meetingday, meetingstart, meetingend, meetingtype, meetingcampusid, meetingbuilding, meetingroom, courseid
c.execute("DROP TABLE IF EXISTS Meetings")
c.execute('''CREATE TABLE IF NOT EXISTS Meetings
                (meetingid text, meetingday text, meetingstart text, meetingend text, meetingtype text, meetingtypestring text, meetingcampusid text, meetingbuilding text, meetingroom text, coursestring text, courseid text)''')
                # meeting type is LEC and WORKSHOP which is great
                # or RECIT
                # or ONLINE INSTRUCTION(INTERNET)
                # or PROJ-IND which has no time
                # meetingmodecode: 
                # 02 means in person
                # 90 means online
                # 19 is proj-independent
                # 03 is recitation
                # 15 is INTERNSP
                # 04 is SEM (seminar?)
                # 05 is LAB
                # 21 is HONORS
                # 20 is PROJ-GRP

                #campusid: campusLocation which is 2 for busch
                #building

# table 7:
# name: SectionMeeting
# columns: sectiondid, meetingid
c.execute("DROP TABLE IF EXISTS SectionMeeting")
c.execute('''CREATE TABLE IF NOT EXISTS SectionMeeting
                (sectionid text, meetingid text)''')


for i in tqdm(range(len(coursedataJSON))):
    courseIndex = i

    #progress bar
    # print("course #: "+str(courseIndex)+"/"+str(len(coursedataJSON))+"")
    # progress_bar_2.update(courseIndex)


    course = coursedataJSON[courseIndex]
    # print("Course: "+str(course['title']))
    # add to db IF course['courseString'] not equal to any course courseid in db
    c.execute("SELECT * FROM Courses WHERE coursecode=?", (course['courseString'],))

    courseID = None
    courseFetch = c.fetchone()
    if courseFetch is None:
        #add to db
        # create courseID - only for internal use
        courseID = uuid.uuid4().hex

        # duplicate short to long name
        courseLongName = course['expandedTitle']
        if courseLongName == "":
            courseLongName = course['title']

        # courseid, shortname, fullname, coursecode
        c.execute("INSERT INTO Courses VALUES (?, ?, ?, ?, ?)", (courseID, course['title'], courseLongName, course['courseString'], course['credits']))

    else:
        #already in db
        # print("course "+course['courseString']+" already in db")
        courseID = courseFetch[0]
        pass
    
    # check if course exists
    # if not, add it
    # if so, get course id

    # add all coursecodes

    if len(course['coreCodes']) > 1:
        # print course name
        print("course: "+course['title']+ ", "+ course['courseString'] + ", " + str(len(course['coreCodes'])) + " core codes")
        # map core codes list to comma separated string
        coreCodesString = ", ".join(map(str, course['coreCodes']))

        for courseCode in range(len(course['coreCodes'])):
            print("course code: "+course['coreCodes'][courseCode]['coreCode'])

    for courseCode in range(len(course['coreCodes'])):

        c.execute("INSERT INTO CourseCoreCodes VALUES (?, ?)", (course['courseString'], course['coreCodes'][courseCode]['coreCode']))


    #print("Section count: "+str(len(course['sections'])))
    #for each section of the class:

    for sectionIndex in range(len(course['sections'])):

        # add to db IF section index not already listed
        section = course['sections'][sectionIndex]
        
        c.execute("SELECT * FROM Sections WHERE sectionindex=?", (section['index'],))

        sectionID = None
        if c.fetchone() is None:
            #add to db
            # create sectionID - only for internal use
            sectionID = uuid.uuid4().hex

            # sectionid, sectionindex, isOpen, finalSituation
            c.execute("INSERT INTO Sections VALUES (?, ?, ?, ?, ?)", (sectionID, section['index'], section['number'], section['openStatus'], section['examCodeText']))
            # examCodeText is like
            # No Final Exam
            # By arrangement
            # Spanish
            # During class hour
        else:
            print("section already in db")
            sectionID = c.fetchone()[0]            

        # do courses
        # add to courseSection if not in
        c.execute("INSERT INTO CourseSection VALUES (?, ?)", (courseID, sectionID))

        # do teachers
        instructorList = section['instructors']
        for instructorIndex in range(len(instructorList)):
            teacherName = instructorList[instructorIndex]['name']
            # add to teacher db if not in
            c.execute("SELECT * FROM Teachers WHERE teachername=?", (teacherName,))
            teacherID = None
            teacherThing = c.fetchone()
            if teacherThing is None:
                #add to db
                # create teacherID - only for internal use
                teacherID = uuid.uuid4().hex
                c.execute("INSERT INTO Teachers VALUES (?, ?)", (teacherID, teacherName))
            else:
                # set teacherID
                # print("FETCHONE:", teacherThing)
                teacherID = teacherThing[0]

            

            # add to teacherSection
            c.execute("INSERT INTO TeacherSection VALUES (?, ?)", (teacherID, sectionID))



        #print("Meeting times: "+str(len(section['meetingTimes'])))
        # PAY ATTENTION TO SESSIONDATES
        #not sure what they are but i should figure out

        for meetingIndex in range(len(section['meetingTimes'])):
            meeting = section['meetingTimes'][meetingIndex]

            # search db for class matching
            # meetingday, meetingstart, meetingend, meetingcampusid, meetingbuilding, meetingroom, coursecode
            # those are duplicates
            meetingID = None
            c.execute("SELECT * FROM Meetings WHERE meetingday=? AND meetingstart=? AND meetingend=? AND meetingcampusid=? AND meetingbuilding=? AND meetingroom=? AND courseid=?", (meeting['meetingDay'], meeting['startTimeMilitary'], meeting['endTimeMilitary'], meeting['campusLocation'], meeting['buildingCode'], meeting['roomNumber'], course['courseString']))

            resultingMeeting = c.fetchone()

            if resultingMeeting is None:

                # add to db
                # meetingid, meetingday, meetingstart, meetingend, meetingtype, meetingcampusid, meetingbuilding, meetingroom, coursecode, courseid
                meetingID = uuid.uuid4().hex
                c.execute("INSERT INTO Meetings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (meetingID, meeting['meetingDay'], meeting['startTimeMilitary'], meeting['endTimeMilitary'], meeting['meetingModeCode'], meeting['meetingModeDesc'], meeting['campusLocation'], meeting['buildingCode'], meeting['roomNumber'], course['courseString'], courseID))

                # add to sectionMeeting
                c.execute("INSERT INTO SectionMeeting VALUES (?, ?)", (sectionID, meetingID))

            else:
                print("meeting already in db")

            continue

            #if meetingDay is blank, this is an online class. only skip this meeting, the other times may be in person!
            if meeting['meetingDay'] == "" or meeting['campusLocation'] == "O":
                #skip this, it's an online class
                onlineClasses.append({
                    "course": course,
                    "section": section,
                    "meetingNum": meetingIndex,
                    "skipReason": "online"
                })
                continue

            if meeting['campusAbbrev'] == "OFF":
                #off campus, skip
                # print("skipping off campus class")
                offCampusClasses.append({
                    "course": course,
                    "section": section,
                    "skipReason": "off campus"
                }) 
                continue


            #campusName may be "** INVALID **"
            #campusAbbrev may be "**"
            #ignore these
            skipbool = False
            # if meeting['campusAbbrev'] == "**":
            #     #skip this, it's an online class
            #     # print("skipping online class")
            #     onlineClasses.append({
            #         "course": course,
            #         "section": section,
            #         "skipReason": "online"
            #     })
            #     skipbool = True

            #if meeting['campusAbbrev'] == "DNB":
                #this is downtown new brunswick. interesting
                #print(meeting)
                #continue

            if meeting['campusAbbrev'] == "" or meeting['buildingCode'] == "" or meeting['meetingDay'] == "":
                #these classes are blank for whatever reason.
                otherErrorClasses.append({
                    "course": course,
                    "section": section,
                    "skipReason": "..."
                })
                skipbool = True

            # if meeting['buildingCode'] == "":
            #     #blank building code?!
            #     skipbool = True

            # if meeting['meetingDay'] == "":
            #     #blank meeting day. prob online
            #     skipbool = True




            #check skipbool
            if not skipbool:
                print("not skipping")
                # else...
                # check if list contains this campusAbbrev+"-"+buildingCode+"-"
                # not sure if building codes can be duplicated across campuses.

                betterBuildingCode = meeting['campusAbbrev'] + " " + meeting['buildingCode'] + " " + meeting[
                    'roomNumber']
                # if meeting['roomNumber'] == "A2":
                #    print(betterBuildingCode)
                #    print(course['title'] + ", " + meeting['meetingDay'])

                buildingObj = getBuildingID(meeting['buildingCode'])
                buildingID = buildingObj['id']
                buildingName = buildingObj['name']

                buildingGeo = getBuildingGeoData(buildingID)
                if buildingGeo:
                    buildingShape = buildingGeo['geometry']
                    buildingLat = buildingGeo['properties']['lat']
                    buildingLng = buildingGeo['properties']['lng']
                    buildingNameNice = buildingGeo['properties']['name']
                else:
                    # print("building code: "+buildingID)
                    print("BUILD GEO ERR" + betterBuildingCode + " " + meeting['meetingDay'])
                    print("class name: " + course['title'])
                    # print(json.dumps(course, indent=2))
                    buildingShape = []
                    buildingLat = ""
                    buildingLng = ""
                    buildingNameNice = buildingName

                betterRoomNameObj = {
                    "bigCampus": course['campusCode'],
                    "campusShort": meeting['campusAbbrev'],
                    "campus": meeting['campusName'],
                    "buildingCode": meeting['buildingCode'],
                    "buildingID": buildingID,
                    "buildingName": buildingName,
                    "buildingNameNice": buildingNameNice,
                    "buildingLat": buildingLat,
                    "buildingLng": buildingLng,
                    "buildingPhoto": image_base_url + buildingID + image_end_url,
                    "buildingOutline": buildingShape,
                    "roomNumber": meeting['roomNumber']
                }
                # print(betterBuildingCode + " " + meeting['meetingDay'])

                # create class data object here...
                # OLD
                # classDataObject = {
                #     "name": course['title'],
                #     "day": meeting['meetingDay'],
                #     "start": meeting['startTimeMilitary'],
                #     "end": meeting['endTimeMilitary']
                # }
                # NEW
                classDataObject = {
                    "nameShort": course['title'],
                    # sometimes expandedTitle is blank... what to do?
                    "name": (course['expandedTitle']).strip(),
                    "start": meeting['startTimeMilitary'],
                    "instructors": section['instructors'],
                    "index": section["index"],
                    "end": meeting['endTimeMilitary']
                }

                currentDay = meeting['meetingDay']
                if currentDay not in currentDayList:
                    currentDayList.append(currentDay)

                location = course['mainCampus']
                if location not in locationList:
                    locationList.append(location)

                campus = meeting['campusName']
                if campus not in campusList:
                    campusList.append(campus)

                buildingCode = meeting['buildingCode'] + "-" + meeting['campusAbbrev']
                if buildingCode not in buildingCodeList:
                    buildingCodeList.append(buildingCode)

                if betterBuildingCode not in byClassroomIndex:
                    byClassroomIndex.append(betterBuildingCode)
                    byClassRoomName.append(betterRoomNameObj)
                    byClassroomData.append({
                        "U": [],
                        "M": [],
                        "T": [],
                        "W": [],
                        "H": [],
                        "F": [],
                        "S": []
                    })

                    #check if class overlaps?
                    print("add new room: "+betterBuildingCode)
                    byClassroomData[byClassroomIndex.index(betterBuildingCode)][currentDay].append(classDataObject)
                else:
                    # print("add to existing room")

                    #check if this is already in the list
                    if (classDataObject in byClassroomData[byClassroomIndex.index(betterBuildingCode)][currentDay]):
                        print("already in list!")
                        # print(classDataObject)
                        # print(byClassroomData[byClassroomIndex.index(betterBuildingCode)][currentDay])
                        pass
                    else:
                        byClassroomData[byClassroomIndex.index(betterBuildingCode)][currentDay].append(classDataObject)

                    # byClassroomData[byClassroomIndex.index(betterBuildingCode)][currentDay].append(classDataObject)

                #sort by start
                byClassroomData[byClassroomIndex.index(betterBuildingCode)][currentDay] = sorted(byClassroomData[byClassroomIndex.index(betterBuildingCode)][currentDay], key=lambda d: d["start"])



# disconnect from db
conn.commit()
conn.close()

# delete temp.json
os.remove("temp.json")