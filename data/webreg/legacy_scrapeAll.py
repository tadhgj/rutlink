import json
import sys
from bs4 import BeautifulSoup
import requests as requests
from tqdm import tqdm
import datetime
import operator

#http://sis.rutgers.edu/oldsoc/courses.json?subject=198&semester=12022&campus=NB&level=U
#http://sis.rutgers.edu/oldsoc/courses.json?subject=198&semester=12022&campus=NB,NK,CM&level=U
# above works but only gets subject 198 which isn't very useful
#http://sis.rutgers.edu/oldsoc/courses.json?semester=12022&campus=CM&level=U,G
#break down api...
#base url
base_url = "http://sis.rutgers.edu/oldsoc/courses.json"

#ALL COURSES ARE 20MB in unzipped form
#surprisingly only 871kb gzipped

#NEW API ALERT BABYYYY
#https://sis.rutgers.edu/soc/api/courses.json?year=2022&term=9&campus=NB
#this does work

#split term off
#get all courses for new brunswick in one file here lets gooo


currentDayList = []
locationList = []
campusList = []
buildingCodeList = []



#get year argument from command line
#expecting 4 digit year
year = sys.argv[1]
#expecting 1 digit term code
        #7 - summer
        #9 - fall
        #0 - winter
        #1 - spring
term = sys.argv[2]
#expecting NB,NK,CM
schoolcampus = sys.argv[3]

#if unset, use default (figure out from current date)
# currCalendarYear = datetime.datetime.now().year
# currMonth = datetime.datetime.now().month
# currDay = datetime.datetime.now().day

#found this from
#https://github.com/anxious-engineer/Rutgers-Course-API/blob/56af65bd17c5ddf512be5bb2a3d28f05c8d50085/DB-PoC/rusoc/api.py
month_to_semester_map = {
    '1' : '1',
     1 : '1',
     '2' : '1',
     2 : '1',
     '3' : '1',
     3 : '1',
     '4' : '1',
     4 : '1',
     '5' : '1',
     5 : '1',
     '6' : '1',
     6 : '1',
     '7' : '7',
     7 : '7',
     '8' : '7',
     8 : '7',
     '9' : '9',
     9 : '9',
     '10' : '9',
     10 : '9',
     '11' : '9',
     11 : '9',
     '12' : '9',
     12 : '9',
}

# if year == "":
#     #get current school year
#     year = str(currCalendarYear)    
# if term == "":
#     #determine which term it is
#     #after jan 15th and before may 2 is spring session
#     if currMonth >= 1 and currMonth <= 4:
#         #spring
#         term = "1"
#     elif currMonth >= 5 and currMonth <= 8:
#         #summer
#         term = "5"
#     elif currMonth >= 9 and currMonth <= 12:
#         #fall
#         term = "9"
        
# if schoolcampus == "":
#     schoolcampus = "NB"


#https://sis.rutgers.edu/soc/?term=92022
#this can convert PH -> to PHARMACY & id:3750

#nameConversion
nameConvertUrl = "https://sis.rutgers.edu/soc/?term="+term+""+year
print(nameConvertUrl)
# r = requests.get("https://sis.rutgers.edu/soc/?term=92022")
r = requests.get(nameConvertUrl)
soup = BeautifulSoup(r.content, features="html.parser")
jsonDiv = json.loads(soup.find('div', {"id": "initJsonData"}).text)

buildingCodes = [d["code"] for d in jsonDiv["buildings"]]
buildingNames = [d["name"] for d in jsonDiv["buildings"]]
buildingIDs = [d["id"] for d in jsonDiv["buildings"]]

def getBuildingID(buildingCodeAbbrev):
    tempIndex = buildingCodes.index(buildingCodeAbbrev)
    return {
        "name": buildingNames[tempIndex],
        "id": buildingIDs[tempIndex]
    }

#print(dict.keys(jsonDiv))

#print(json.dumps(jsonDiv, indent=2))
#print(json.dumps(jsonDiv['buildings'], indent=2))


#get coords of buildings
#for now, import file. later, pull directly from URL
buildingLayer = open("fromMap/buildings-parking-layer.json")
buildingLayerJson = json.load(buildingLayer)
#print(json.dumps(buildingLayerJson, indent=2))
#print(dict.keys(buildingLayerJson))
buildingLayerIndex = [d["id"] for d in buildingLayerJson['features']]
def getBuildingGeoData(buildingID):
    if buildingID in buildingLayerIndex:
        curr = buildingLayerJson['features'][buildingLayerIndex.index(buildingID)]
        return {
            "geometry": curr['geometry'],
            "properties": curr['properties']
        }
    else:
        return

#get coords of regions
#NOT HELPFUL!
# campusLayer = open("fromMap/districts.json")
# campusLayerJSON = json.load(campusLayer)
# #print(json.dumps(buildingLayerJson, indent=2))
# #print(dict.keys(buildingLayerJson))
# campusLayerIndex = [d["id"] for d in campusLayerJSON['features']]
# print(campusLayerIndex)
# def getDistrictGeoData(campusID):
#     campusID = int(campusID)
#     if campusID in campusLayerIndex:
#         #print("Campus id:"+str(campusID))
#         curr = campusLayerJSON['features'][campusLayerIndex.index(campusID)]
#         return {
#             "geometry": curr['geometry'],
#             "properties": curr['properties']
#         }
#     else:
#         return


#MAP API ALERT!!!
#https://maps.rutgers.edu/#/?click=true&selected=3117
map_base_url = ""


#IMAGE API
image_base_url = "https://storage.googleapis.com/rutgers-campus-map-building-images-prod/"
image_end_url = "/00.jpg"


#IMPORT NOW DOWNLOAD LATER
# coursedataFile = open("fromSIS/courses2.json")
# coursedataJSON = json.load(coursedataFile)


#download
#https://sis.rutgers.edu/soc/api/courses.json?year=2022&term=9&campus=NB,NK,CM

#could look into 
#https://scheduling.rutgers.edu/scheduling/class-scheduling/standard-course-periods-0
#this page to help compress the data
#since most classes follow the standard course periods listed here,
#the abbreviations can be used to express the standard class times
#and the full times can be used for the exceptions

#Standard Course Periods
# 80min Periods	        55min Periods	        180min Periods
# 1	8:30 – 9:50am	    1*	8:45 – 9:40am	    1,2	        8:30 – 11:30am
# 2	10:20 – 11:40am	    2*	10:35 – 11:30am 	2,3	        10:20am – 1:20pm
# 3	12:10 – 1:30pm	    3*	12:25 – 1:20pm	    3,4	        12:10 – 3:10pm
# 4	2:00 – 3:20pm	    4*	2:15 – 3:10pm	    4,5	        2:00 – 5:00pm
# 5	3:50 – 5:10pm	    5*	4:05 – 5:00pm	    5,6	        3:50 – 6:50pm
# 6	5:40 – 7:00pm	    6*	5:55 – 6:50pm	    6,7     	5:40 – 8:40pm
# 7	7:30 – 8:50pm	    7*	7:45 – 8:40pm	    Grad Eve	6:00 – 9:00pm
# 8	9:20 – 10:40pm	    8*	9:35 – 10:30pm	    7,8	        7:30 – 10:30pm

#Standard period combinations: 2x80min, 2x55min
#  	Monday	Tuesday	Wednesday	Thursday	Friday
# 1	MTh1	TF1	    W1F6	    MTh1	    TF1
# 2	MTh2	TF2	    W2F5	    MTh2	    TF2
# 3	MTh3	TF3	    W3F4	    MTh3	    TF3
# 4	MW4	    TTh4	MW4	        TTh4	    W3F4
# 5	MW5	    TTh5	MW5	        TTh5	    W2F5
# 6	MW6	    TTh6	MW6	        TTh6	    W1F6
# 7	MW7	    TTh7	MW7	        TTh7	 
# 8	MW8	    TTh8	MW8	        TTh8	 


# Standard Period Combinations: 3x80min, 3x55min
# All meetings should take place in the same room
#  	Monday	Tuesday	Wednesday	Thursday	Friday
# 1	MWTh1	TWF1	MWTh1       MWTh1	    TWF1
#                     TWF1
# 2	MWTh2	TWF2	MWTh2       MWTh2	    TWF2
#                     TWF2

# 3	MWTh3	TWF3	MWTh3       MWTh3	    TWF3
#                     TWF3
# 4	MWF4	TThF4	MWF4	    TThF4   	MWF4
#                                           TThF4
# 5	MWF5	TThF5	MWF5	    TThF5	    MWF5
#                                           TThF5
# 6	MWF6	TThF6	MWF6	    TThF6	    MWF6
#                                           TThF6

#https://scheduling.rutgers.edu/scheduling/academic-calendar
scheduleURL = "https://scheduling.rutgers.edu/scheduling/academic-calendar"
sched = requests.get(scheduleURL)
schedSoup = BeautifulSoup(sched.content, features="html.parser")

#find div.responsive-table__scroll table.pretty-table.responsive-enabled
# schedTable = schedSoup.find_all('div', {"class": "responsive-table__scroll"})
# print(schedSoup.body.find({"class": "responsive-table"}))

#found it!
# print(schedSoup.table)

#.find('table', {"class": "pretty-table responsive-enabled"})




#this is for new api, which does not support multiple campuses, so I am using old api
courseURLBase = "https://sis.rutgers.edu/soc/api/courses.json?year="+year+"&term="+term+"&campus="+schoolcampus

#this is for old api, which requires a subject code
# courseURLBase = "http://sis.rutgers.edu/old/soc/courses.json?semester="+term+""+year+"&campus="+schoolcampus

print(courseURLBase)

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
    # print("ERROR, something went wrong")

print("Download complete.")
# r = requests.get(courseURLBase)

# coursedataJSON = r.json()

coursedataJSON = ""
#read test.dat to get json data
with open('temp.json') as json_file:
    coursedataJSON = json.load(json_file)





print("Num of classes: "+str(len(coursedataJSON)))

#remember counts of stuff here
onlineClasses = []
offCampusClasses = []
otherErrorClasses = []
sectionCount = 0


#classes are listed. I want a list formatted based on classroom.

#so, make new list

#course["mainCampus"]


byClassroomIndex = []
byClassRoomName = []
byClassroomData = []

#iterate through each class, read all of their meeting times

#test
#print(json.dumps(coursedataJSON[2], indent=2))

skipCrossPostIndexes = []

# progress_bar_2 = tqdm(total=len(coursedataJSON))

#wrap this with 
# just wrap any iterable with tqdm(iterable) and you're done!

for i in tqdm(range(len(coursedataJSON))):
    courseIndex = i

    #progress bar
    # print("course #: "+str(courseIndex)+"/"+str(len(coursedataJSON))+"")
    # progress_bar_2.update(courseIndex)


    course = coursedataJSON[courseIndex]
    #print("Course: "+str(course['title']))
    #print("Section count: "+str(len(course['sections'])))
    #for each section of the class:

    for sectionIndex in range(len(course['sections'])):
        sectionCount += 1

        section = course['sections'][sectionIndex]
        #print("Meeting times: "+str(len(section['meetingTimes'])))
        # PAY ATTENTION TO SESSIONDATES
        #not sure what they are but i should figure out

        #cross-post check
        if section['index'] in skipCrossPostIndexes:
            #skip section
            #print("skipping dupe")
            continue
        #else:
            #print("not skipping dupe")

        #print("should not show this after skipping dupe")
        if len(section['crossListedSections']) > 0:
            for sectionCross in section['crossListedSections']:
                skipCrossPostIndexes.append(sectionCross['registrationIndex'])


        for meetingIndex in range(len(section['meetingTimes'])):
            meeting = section['meetingTimes'][meetingIndex]
            print("c#:"+str(courseIndex)+", s#:"+str(sectionIndex)+", m#:"+str(meetingIndex)+"..."+course['title'] + ", " + meeting['meetingDay'])
            #print("")
            #sorting by campusAbbrev, campusName, buildingCode
            #use startTimeMilitary and endTimeMilitary
            
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

# progress_bar_2.close();

# print(skipCrossPostIndexes)
print("skipped online classes: " + str(len(onlineClasses)))
print("skipped off-campus classes: " + str(len(offCampusClasses)))
print("skipped other error classes: " + str(len(otherErrorClasses)))

#write these errors to a file
with open('onlineClasses.json', 'w') as outfile:
    json.dump(onlineClasses, outfile)

with open('offCampusClasses.json', 'w') as outfile:
    json.dump(offCampusClasses, outfile)

with open('otherErrorClasses.json', 'w') as outfile:
    json.dump(otherErrorClasses, outfile)

print("total section count: " + str(sectionCount))


#parameters:
#subject
    #subject codes are on page thing
    #can use bs4 to scrape this
        #https://sis.rutgers.edu/soc/#subjects?semester=12022&campus=CM&level=U,G
        #has good info in <div id="initJsonData"> element
    #scrap that there's an api!!!
    #https://sis.rutgers.edu/oldsoc/subjects.json?semester=92022&campus=NB&level=U
    #can i query each subject at once?

#semester
    #72022 is summer 2022
    #92022 is fall 2022
    #02023 is winter 2023
    #12022 is spring 2022
    #procedurally, then
        #7 - summer
        #9 - fall
        #0 - winter
        #1 - spring
        #then add year afterwards
        #example, for 2022-2023 school year, fall is 2022, winter is 2023, spring is 2023?
            #this is stupid because spring occurs in 2023. Is it not showing next spring?

#campus
    #can be NB, NK, CM
    #can combine but not useful for this application
#level
    #can be U, G, or UG for both under and graduate
    #should always use U,G for this application


#print(byClassroomData)

def betterAppend(objDefArr, objectToAppend):
    for j in range(len(objDefArr)):
        print("jk")

def doesItExist(object, parameter, nestedparameter, check):
    for x in object:
        print(x)
        if object[parameter][nestedparameter] == check:
            return True
            break

    return False

def indexObjComplicated(object, parameter, nestedparameter, check):
    for i in range(len(object)):
        #print("j:"+str(i)+" param:"+parameter+" ,nest: "+nestedparameter+", check:"+check)
        #print(object)
        #print(object[int(i)])
        #print(object[int(i)][str(parameter)])
        for j in range(len(object[int(i)][str(parameter)])):
            #print("k:"+str(j))
            #print("thingtocheck: '" + object[int(i)][str(parameter)][int(j)][str(nestedparameter)] + "'")
            if object[int(i)][str(parameter)][int(j)][str(nestedparameter)] == check:
                return j
                break

    return -1

def secondIndexObjSimple(object, parameter, check):
    for i in range(len(object)):
        #print("j:"+str(i)+" param:"+parameter+", check:"+check)
        #print(object)
        #print(object[int(i)])

        if parameter not in dict.keys(object[int(i)]):
            continue

        #print(object[int(i)][str(parameter)])

        #if nestedparameter not in dict.keys(object[int(i)][str(parameter)]):
        #    continue

        #print("thingtocheck: '" + object[int(i)][str(parameter)] + "'")


        if object[int(i)][str(parameter)] == check:
            return i
            break

    return -1

#generate timestamp
timestampStr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#generate termNice
termNice = ""
if term == "7":
    termNice = "Summer"
elif term == "9":
    termNice = "Fall"
elif term == "0":
    termNice = "Winter"
elif term == "1":
    termNice = "Spring"

byGroupies = [{
    "metadata": {
        "request": {
            "year": year,
            "term": term,
            "schoolcampus": schoolcampus,
            "termNice": termNice,
            "url": courseURLBase
        },
        "timestamp": timestampStr,
    },
    "campuses": []
}]
#start with bigCampus/location...

for i in range(len(byClassroomIndex)):
    #if i > 3:
    #    exit()
    #print(i)
    #print(byGroupies)
    things = byClassroomData[i]
    #instead of byGroupies.campuses[where code=LIV].buildings[where Code=BE].rooms[where number=101].schedule[where
    #betterAppend([byGroupies], ["code", "LIV"])

    #check for campus
    #print("checking for campus: "+byClassRoomName[i]['campusShort'])
    campusIndex = indexObjComplicated(byGroupies, "campuses", "code", byClassRoomName[i]['campusShort'])
    #print("campusIndex of "+byClassRoomName[i]['campusShort']+": "+str(campusIndex))
    if campusIndex != -1:
        campusTarget = byGroupies[0]['campuses'][campusIndex]
        #check for building
        buildingIndex = secondIndexObjSimple(campusTarget['buildings'], "ID", byClassRoomName[i]['buildingID'])
        if buildingIndex != -1:
            campusTarget['buildings'][buildingIndex]['rooms'].append({
                "number": byClassRoomName[i]['roomNumber'],
                "schedule": byClassroomData[i]
            })

            campusTarget['buildings'][buildingIndex]['rooms'] = sorted(campusTarget['buildings'][buildingIndex]['rooms'], key=lambda d: d["number"])
        else:
            campusTarget['buildings'].append(
                {
                    "sanityCheck": byClassRoomName[i]['campusShort'],
                    "Code": byClassRoomName[i]['buildingCode'],
                    "ID": byClassRoomName[i]['buildingID'],
                    "Name": byClassRoomName[i]['buildingName'],
                    "NameNice": byClassRoomName[i]['buildingNameNice'],
                    "Lat": byClassRoomName[i]['buildingLat'],
                    "Lon": byClassRoomName[i]['buildingLng'],
                    "Photo": byClassRoomName[i]['buildingPhoto'],
                    # "Shape": byClassRoomName[i]['buildingOutline'],
                    # "roomCount": 0,
                    "rooms": [
                        {
                            "number": byClassRoomName[i]['roomNumber'],
                            "schedule": byClassroomData[i]
                        }
                    ]
                }
            )
    else:
        byGroupies[0]['campuses'].append({
            "code": byClassRoomName[i]['campusShort'],
            "name": byClassRoomName[i]['campus'],
            "buildings": [
                {
                    "sanityCheck": byClassRoomName[i]['campusShort'],
                    "Code": byClassRoomName[i]['buildingCode'],
                    "ID": byClassRoomName[i]['buildingID'],
                    "Name": byClassRoomName[i]['buildingName'],
                    "NameNice": byClassRoomName[i]['buildingNameNice'],
                    "Lat": byClassRoomName[i]['buildingLat'],
                    "Lon": byClassRoomName[i]['buildingLng'],
                    "Photo": byClassRoomName[i]['buildingPhoto'],
                    # "roomCount": 0,
                    "rooms": [
                        {
                            "number": byClassRoomName[i]['roomNumber'],
                            "schedule": byClassroomData[i]
                        }
                    ]
                }
            ]
        })



    #sort byClassroomData[i] by startTime
    # combinedObject.append({
    #     "roomStr": byClassroomIndex[i],
    #     "room": byClassRoomName[i],
    #     "things": byClassroomData[i]
    # })



exampleObjThing = {
    "metadata": {},

    "campuses": [
        {
            "code": "LIV",
            "name": "LIVINGSTON",
            #"buildingCount": 0,
            #try to get geometry!
            #"geometry": {},
            "buildings": [
                {
                    "Code": "BE",
                    "ID": "4145",
                    "Name": "BECK HALL",
                    "NameNice": "Beck Hall",
                    "Lat": 0,
                    "Lon": 0,
                    "Photo": "url...",
                    #"roomCount": 0,
                    "rooms": [
                        {
                            "number": 101,
                            "schedule": {
                                "M": [],
                                "T": [
                                    {
                                        "className": "...",
                                        "classNameShort": "..",
                                        "start": "",
                                        "end": "",
                                        "instructors": []
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
    ]
}


file_name = termNice+""+str(year)+".json"

combinedObject = []
for i in range(len(byClassroomIndex)):
    #sort byClassroomData[i] by startTime
    combinedObject.append({
        "roomStr": byClassroomIndex[i],
        "room": byClassRoomName[i],
        "things": byClassroomData[i]
    })

        # "room": {
        #     "campusCode": meeting['campusCode'],
        #     "id": ""
        # },
        # "days": {
        #     "M": [],
        #     "T": [],
        #     "W": [],
        #     "H": [],
        #     "F": [],
        # }

#write to file now...
json_object = json.dumps(combinedObject)

# Writing to sample.json
with open("didit.json", "w") as outfile:
    outfile.write(json_object)

# write to file now...
json_object_2 = json.dumps(byGroupies)

# Writing to sample.json
#get good filename
#Spring2022.json for example

with open(file_name, "w") as outfile:
    outfile.write(json_object_2)


#https://dcs.rutgers.edu/classrooms/building-identification-codes
#website that lists most of the building codes?
#convenient ABBREV, 4digcode, campus and clean building name


#https://dcs.rutgers.edu/classrooms/find-a-classroom
#website that lists all rooms




# https://storage.googleapis.com/rutgers-campus-map-building-images-prod/4153/00.jpg
#image api!!!!
#awesome

#popular-destinations.json
#https://storage.googleapis.com/rutgers-campus-map-prod-public-sync/1665710767211%20(Oct%2013,%202022,%209:26%20PM%20EDT)/buildings/popular-destinations.json
#has full name, (building abbrev), 4-digit building ID
#does not have many buildings. useless.

#site-ids.json
#https://storage.googleapis.com/rutgers-campus-map-prod-public-sync/1665710767211%20(Oct%2013,%202022,%209:26%20PM%20EDT)/site_ids.json
#has

#search.json
#https://storage.googleapis.com/rutgers-campus-map-prod-public-sync/1665710767211%20(Oct%2013,%202022,%209:26%20PM%20EDT)/search.json
#biggest!

#districts.json
#https://storage.googleapis.com/rutgers-campus-map-public-data-prod/districts.json
#districts? just lat long stuff

#IMPORTANT
#buildings-parking-layer.json
#https://storage.googleapis.com/rutgers-campus-map-prod-public-sync/1665721747083%20(Oct%2014,%202022,%2012:29%20AM%20EDT)/buildings-parking-layer.json
#1665721747083%20(Oct%2014,%202022,%2012:29%20AM%20EDT)
#unix time %20 ( MMM %20 DD ,%20 YYYY ,%20 HH:MM %20 AM/PM %20 EDT )
#1665721747083 (Oct 14, 2022, 12:29 AM EDT)
#unix time (MMM, DD, YYYY, HH:MM AM/PM EDT)

# https://storage.googleapis.com/rutgers-campus-map-prod-public-sync/1697578574042%20(Oct%2017,%202023,%205:36%20PM%20EDT)/buildings-parking-layer.json

# old: 1665721747083%20(Oct%2014,%202022,%2012:29%20AM%20EDT)
# new: 1697578574042%20(Oct%2017,%202023,%205:36%20PM%20EDT)

# 1697578574042 - what is this
# %20           - space
# (Oct%2017,%202023,%205:36%20PM%20EDT) - (Oct 17, 2023, 5:36 PM EDT)
# but this was accessed at 6:21 PM. how am I supposed to get the current filename?
#print(currentDayList)
#print(locationList)
#print(campusList)
buildingCodeList = sorted(buildingCodeList)
#print(json.dumps(buildingCodeList, indent=2))

#data format
#make obj with campusList, campus short as grouping. consider adding region geometry later
#inside campus, we have buildings

#list of buildings - not sorted by campus
# - image
# - address
# - lat
# - long
# - each room
# # - schedule grouped by days
# # # # course name,
# # # # recitation/lecture,
# # # # instructor,


