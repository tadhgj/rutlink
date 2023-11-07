# for json file parsing
import json

# for saving files
import sys

# for scraping associated webpages
from bs4 import BeautifulSoup

# for making network requests
import requests as requests

# import argparse
import argparse

import datetime

debug = False
# handle command line arguments


def parseSingletonDate(dateString):
    if (debug):
        print("parseSingletonDate: " + dateString)
    # expecting roughly 3 cases
    # Sat, September 10, 2022	
    # Wed, November 27, 2024 \n(Friday Classes)
    # October 25, 2022
    # and sometimes just "" (empty string)

    # if empty string
    if dateString == "":
        return None
    else:
        # split away preceding weekday IF 2 COMMAS
        if dateString.count(",") == 2:
            # join array from index 1 to end
            # dateString = Arr.join(", ", dateString.split(",")[1:]);
            dateString = ", ".join(dateString.split(", ")[1:]).strip()
            if (debug):
                print("preceding weekday detected, split away")
                print("dateString is now: " + dateString)
        else:
            # not expecting preceding weekday
            pass

        # split away trailing "(Friday Classes)" IF 1 PARENTHESIS
        if dateString.count("(") == 1:
            dateString = dateString.split("(")[0].strip()
        else:
            # not expecting trailing "(Friday Classes)"
            pass

        # should now look like "September 10, 2022"
        # set year
        year = dateString.split(",")[-1].strip()
        # if (debug):
            # print("year is: " + year)

        # set month
        month = dateString.split(",")[0].split(" ")[0].strip()
        # if (debug):
            # print("month is: " + month)
        # parse month from string to number
        month = datetime.datetime.strptime(month, "%B").month
        # if (debug):
            # print("month is now: " + str(month))


        # set day
        day = dateString.split(",")[0].split(" ")[-1].strip()
        # check if date is valid for given month and year
        if int(day) > 31:
            # wrong
            return None
        else:
            # check if date is valid for given month and year
            if int(month) == 2 and int(day) > 28:
                # check if leap year
                if int(year) % 4 == 0:
                    # leap year
                    pass
                else:
                    # not leap year
                    return None
            elif int(month) in [4, 6, 9, 11] and int(day) > 30:
                # wrong
                return None
            else:
                # correct
                pass

        # check year is 4 digits
        if int(year) < 1000 or int(year) > 9999:
            # invalid year
            return None

        # pad 0 if necessary
        if int(month) < 10:
            month = "0" + str(month)
        else:
            month = str(month)

        # pad 0 if necessary
        if int(day) < 10:
            day = "0" + str(day)
        else:
            day = str(day)

        # return as a string yyyy-mm-dd
        retString = year + "-" + month + "-" + day
        if (debug):
            print("returning: " + retString)
        return retString

def parseDateString(dateString):
    if (debug):
        print("parseDateString: " + dateString)
    # return ["type", ["dates"]]
    # look for instances of " to "
    if " to\xa0" in dateString:
        if (debug):
            print("range detected:")
        # split by " to "
        dates = dateString.split(" to\xa0")

        # Thu, November 24 to\xa0Sun, November 27, 2022
        # should split to
        # ["Thu, November 24", "Sun, November 27, 2022"]
        # but we want to include the year in the first date like this
        # ["Thu, November 24, 2022", "Sun, November 27, 2022"]

        # so if the second date has two commas, the second one preceding the year
        # and the first date has one comma
        # append the year to the first item
        if dates[1].count(",") == 2 and dates[0].count(",") == 1:
            # append the year to the first item
            dates[0] = dates[0] + ", " + dates[1].split(", ")[-1]

        # parse each date...
        for i in range(len(dates)):
            dates[i] = parseSingletonDate(dates[i])
        return ["range", dates]
    else:
        # if \xa0 is in dateString, and the second line isn't (...), then it's a "list"
        if "\xa0" in dateString:
            if (debug):
                print("line break detected:")
                print(dateString.split("\xa0"))

            if "(" == dateString.split("\xa0")[1][0]:
                # only parse the first date
                return ["instant", [parseSingletonDate(dateString.split("\xa0")[0])]]
            else:
                # ...
            
                if "(" not in dateString.split("\xa0")[1]:
                    # split by \xa0
                    dates = dateString.split("\xa0")
                    # parse each date...
                    for i in range(len(dates)):
                        dates[i] = parseSingletonDate(dates[i])
                    return ["list", dates]
                else:
                    print("hi")
        else:
            # check if empty
            if dateString == "":
                return None

            # otherwise, it's an "instant"
            return ["instant", [parseSingletonDate(dateString)]]

def parseRawTable(thead_list, tbody_list):
    # organize data into a dictionary
    # events = [
    #     {
    #         "name": "First Day of Classes",
    #         "type": "instant", # can be instant, range, or list
    #         "dates": [
    #             # instant:
    #             "2021-09-01",

    #             # range:
    #             "2021-09-01",
    #             "2021-09-04",
    #             # would be inclusive of 9/1 and 9/4

    #             # list:
    #             "2021-09-01",
    #             "2021-09-04",
    #             # would only specify 9/1 and 9/4
    #         ]
    #     }
    # ]
    events = []

    # print theadlist
    # print("thead_list: ", thead_list)
    # print("tbody_list: ", tbody_list)

    sectionCount = 0
    # for each row in tbody_list
    # print tbody list nicely:
    for tbody_object in tbody_list:

        if tbody_object['name'] == "":
            sectionCount += 1
            continue

        # print name:
        # print("row to read: ", tbody_object['name'])

        # check if empty
        if "".join(tbody_object['things']) == "":
            continue

        ti = tbody_object['things']
        # print("starting with: ", ti)
        for i in range(len(ti)):
            # 
            ti[i] = parseDateString(ti[i])

            events.append({
                "name": tbody_object['name'],
                "type": "instant",
                "section": sectionCount,
                "year": thead_list[i+1],
                "dates": ti[i]
            })

        # print(ti)

    # print(events)
    return events



def parsePage(soup):
    # find table.pretty-table.responsive-enabled
    table = soup.find('table', class_='pretty-table responsive-enabled')

    # or die
    if table is None:
        print("could not find table.pretty-table.responsive-enabled")
        exit(1)

    # read thead
    thead = table.find('thead')
    thead_list = [] # expected to be list ["Events", "2022-2023", "2023-2024", "2024-2025"] 
                    # or whatever the year may be

    thead_rows = thead.find_all('tr')
    for thead_row in thead_rows:
        thead_cols = thead_row.find_all('th')
        for thead_col in thead_cols:
            thead_list.append(thead_col.text.strip())

    # debug
    if (debug):
        print("thead_list:")
        print(thead_list)

    # read tbody
    tbody = table.find('tbody')
    tbody_list = []
    # tbody object: {name: "", things: ["", "", "", ""]}

    tbody_rows = tbody.find_all('tr')
    for tbody_row in tbody_rows:
        tbody_cols = tbody_row.find_all('td')
        tbody_object = {}
        tbody_object['name'] = tbody_cols[0].text.strip()
        tbody_object['things'] = []
        for tbody_col in tbody_cols[1:]:
            tbody_object['things'].append(tbody_col.text.strip())
        tbody_list.append(tbody_object)

    eventList = parseRawTable(thead_list, tbody_list)

    # determine which term we're in:
    # look for 
    # "Fall Semester Begins"
    # "Regular Classes End" with the same section as "Fall Semester Begins"
    # "Winter Session Begin"
    # "Winter Session End"
    # "Spring Semester Begins"
    # "Regular Classes End" with the same section as "Spring Semester Begins"
    # "Summer Session Begins"
    # "Summer Session End"

    # print(eventList)

    seasonRange = {
        # "year": {
        #     "fall": {
        #         "start": "",
        #         "end": ""
        #     },
        #     "winter": {
        #         "start": "",
        #         "end": ""
        #     },
        #     "spring": {
        #         "start": "",
        #         "end": ""
        #     },
        #     "summer": {
        #         "start": "",
        #         "end": ""
        #     }
        # }
    }

    def createyear(year):
        seasonRange[year] = {
            "fall": {
                "start": "",
                "end": ""
            },
            "winter": {
                "start": "",
                "end": ""
            },
            "spring": {
                "start": "",
                "end": ""
            },
            "summer": {
                "start": "",
                "end": ""
            }
        }

    # creating a nice semester detector
    # ignores other events for now
    
    currentSection = 0
    for event in eventList:
        # print()
        # print(event)
        # print()
        if event['name'] == "Fall Semester Begins":
            # print("fall!")
            currentSection = event['section']
            # expecting instant
            if event['type'] != "instant":
                print("expected instant, got " + event['type'] + " instead")
                exit(1)
            # create year if not exists
            if event['year'] not in seasonRange:
                createyear(event['year'])

            seasonRange[event['year']]['fall']['start'] = event['dates'][1][0]
            continue
        
        if event['name'] == "Regular Classes End" and event['section'] == currentSection:
            # print("fall end!")
            if event['type'] != "instant":
                print("expected instant, got " + event['type'] + " instead")
                exit(1)
            if event['year'] not in seasonRange:
                createyear(event['year'])
            seasonRange[event['year']]['fall']['end'] = event['dates'][1][0]
            continue

        if event['name'] == "Winter Session Begins":
            # print("winter!")
            currentSection = event['section']
            if event['type'] != "instant":
                print("expected instant, got " + event['type'] + " instead")
                exit(1)
            if event['year'] not in seasonRange:
                createyear(event['year'])
            seasonRange[event['year']]['winter']['start'] = event['dates'][1][0]
            continue

        if event['name'] == "Winter Session Ends":
            # print("winter end!")
            if event['type'] != "instant":
                print("expected instant, got " + event['type'] + " instead")
                exit(1)
            if event['year'] not in seasonRange:
                createyear(event['year'])
            seasonRange[event['year']]['winter']['end'] = event['dates'][1][0]

        if event['name'] == "Spring Semester Begins":
            # print("spring!")
            currentSection = event['section']
            if event['type'] != "instant":
                print("expected instant, got " + event['type'] + " instead")
                exit(1)
            if event['year'] not in seasonRange:
                createyear(event['year'])
            seasonRange[event['year']]['spring']['start'] = event['dates'][1][0]

        if event['name'] == "Regular Classes End" and event['section'] == currentSection:
            # print("spring end!")
            if event['type'] != "instant":
                print("expected instant, got " + event['type'] + " instead")
                exit(1)
            if event['year'] not in seasonRange:
                createyear(event['year'])
            seasonRange[event['year']]['spring']['end'] = event['dates'][1][0]

        if event['name'] == "Summer Session Begins":
            # print("summer!")
            currentSection = event['section']
            if event['type'] != "instant":
                print("expected instant, got " + event['type'] + " instead")
                exit(1)
            if event['year'] not in seasonRange:
                createyear(event['year'])
            seasonRange[event['year']]['summer']['start'] = event['dates'][1][0]

        if event['name'] == "Summer Session Ends":
            # print("summer end!")
            if event['type'] != "instant":
                print("expected instant, got " + event['type'] + " instead")
                exit(1)
            if event['year'] not in seasonRange:
                createyear(event['year'])
            seasonRange[event['year']]['summer']['end'] = event['dates'][1][0]

    # print(seasonRange)

    # detect which term it is
    for schoolYearIndex in range(len(seasonRange)):
        schoolYearName = list(seasonRange.keys())[schoolYearIndex]
        schoolYearData = seasonRange[schoolYearName]

        # print("schoolYearName: ", schoolYearName)

        for seasonIndex in range(len(schoolYearData)):
            seasonName = list(schoolYearData.keys())[seasonIndex]
            seasonData = schoolYearData[seasonName] 

            # print("seasonName: ", seasonName)

            if seasonData['start'] == "":
                continue
            if seasonData['end'] == "":
                continue
            # check if current date is between start and end
            # convert yyyy-mm-dd to seconds since epoch
            # check if current date is between start and end
            startEpoch = datetime.datetime.strptime(seasonData['start'], "%Y-%m-%d").timestamp()
            nowEpoch = datetime.datetime.now().timestamp()
            endEpoch = datetime.datetime.strptime(seasonData['end'], "%Y-%m-%d").timestamp()

            # print("nowEpoch: ", nowEpoch)
            # print("startEpoch: ", startEpoch)
            # print("endEpoch: ", endEpoch)

            term = ""
            year = ""

            if nowEpoch < endEpoch and nowEpoch > startEpoch:
                # found it
                # print("current semester is: ",seasonName, schoolYearName)

                firstYearOfSchoolYear = schoolYearName.split("-")[0]
                secondYearOfSchoolYear = schoolYearName.split("-")[1]

                if seasonName == "fall":
                    # fall
                    term = "9"
                    year = firstYearOfSchoolYear
                elif seasonName == "winter":
                    # winter
                    term = "0"
                    year = secondYearOfSchoolYear
                elif seasonName == "spring":
                    # spring
                    term = "1"
                    year = secondYearOfSchoolYear
                elif seasonName == "summer":
                    # summer
                    term = "7"
                    year = secondYearOfSchoolYear

                #9 - fall
                #0 - winter   
                #1 - spring
                #7 - summer
                # want to return "9 2023"
                # if so, print the school year and season
                return [term, year]
    
    # some error occurred
    return ["",""]

# export this function:

def fetchPage():
    # https://scheduling.rutgers.edu/scheduling/academic-calendar

    # open that page
    page = requests.get("https://scheduling.rutgers.edu/scheduling/academic-calendar")

    # parse the html
    soup = BeautifulSoup(page.content, 'html.parser')
    return parsePage(soup)


def getTermAndYear():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-debug', action='store_true', default=False, help='print more things')
    # args = parser.parse_args()
    # parse_results = parser.parse_args()
    # debug = parse_results.debug

    return fetchPage()

# print(getTermAndYear())
