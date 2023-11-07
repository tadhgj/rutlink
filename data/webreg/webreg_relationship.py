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

# for log
import logging

# handle command line arguments
import argparse

year = ""
term = ""
schoolcampus = ""

# # take -year, -term, -campus
# argparser = argparse.ArgumentParser()
# argparser.add_argument("-year", help="year to fetch", type=str)
# argparser.add_argument("-term", help="term to fetch", type=str)
# argparser.add_argument("-campus", help="campus to fetch", type=str)



# set everything not given from args...
schoolcampus = "NB"
# arr = read_term_schedule.getTermAndYear()
# term = arr[0]
# year = arr[1]

# overwrite with args
# if len(sys.argv) > 1:
#     args = argparser.parse_args()
#     if args.year:
#         year = args.year
#     if args.term:
#         term = args.term
#     if args.campus:
#         schoolcampus = args.campus



# print("Year: "+year)
# print("Term: "+term)
# continue...

# # https://sis.rutgers.edu/soc/api/courses.json?year=2023&term=9&campus=NB
# # https://sis.rutgers.edu/soc/api/courses.json?year=2023&term=9&campus=NB
# courseURLBase = "https://sis.rutgers.edu/soc/api/courses.json?year="+year+"&term="+term+"&campus="+schoolcampus
# # print(courseURLBase)

# #download this url
# # courseURL = "https://sis.rutgers.edu/soc/api/courses.json?year=2022&term=9&campus=NB,NK,CM"
# #              https://sis.rutgers.edu/soc/api/courses.json?year=2022&term=9&campus=NB,NK,CM
# #print progress for this download
# print("Downloading course data...")
# r = requests.get(courseURLBase, stream=True)

# total_size_in_bytes= int(r.headers.get('content-length', 0))
# block_size = 1024 #1 Kibibyte
# progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
# with open('temp.json', 'wb') as file:
#     for data in r.iter_content(block_size):
#         progress_bar.update(len(data))
#         file.write(data)
# progress_bar.close()
# # if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
# #     print("ERROR, something went wrong")

# print("Download complete.")

# # use temp.json...
# coursedataJSON = ""
# #read test.dat to get json data
# with open('temp.json') as json_file:
#     coursedataJSON = json.load(json_file)


# print("Num of classes: "+str(len(coursedataJSON)))



# get multiple course data...
# get:
listt = [
    ["2024","01"],
    ["2023","09"],
    ["2023","01"],
    ["2022","09"],
    ["2022","01"]
]


def getCourseData(year, term):
    courseURLBase = "https://sis.rutgers.edu/soc/api/courses.json?year="+year+"&term="+term+"&campus="+schoolcampus

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
    returnJSON = ""
    #read test.dat to get json data
    with open('temp.json') as json_file:
        returnJSON = json.load(json_file)

    return returnJSON


class_rel_dict = []
class_rel_dict_index = []

def addJSONToRelList(coursedataJSON, semester):
    for i in tqdm(range(len(coursedataJSON))):

        courseIndex = i

        course = coursedataJSON[courseIndex]

        courseid = course['courseString']

        # print(courseid)



        # parse prereq list...
        prereq_str = course['preReqNotes']
        # extract every instance of xx:xxx:xxx from prereq_str where x is a digit
        prereq_list = []

        # split by spaces
        prereq_spaces = prereq_str.split(" ")
        # for each...
        for item in prereq_spaces:
            # check for 2 ":"s
            if item.count(":") == 2:
                # remove all non-numeric characters
                item = item.replace("(", "")
                item = item.replace(")", "")
                # including :, (, ), and -
                # use regex
                # digitem = ''.join(filter(str.isdigit, item))

                # check if there are 2 + 3 + 3 digits
                # if len(digitem) == 8:
                    # prereq_list.append(item)

                if item.replace(":","").isdigit():
                    prereq_list.append(item)

        # group by ()??


        # check if course in class_rel_dict_index...
        if courseid in class_rel_dict_index:

            # update things?
            class_rel_dict[class_rel_dict_index.index(courseid)]['semesterList'].append(semester)

            continue

        # add course to class_rel_dict_index
        # add course to class_rel_dict
        # add attributes
        class_rel_dict_index.append(courseid)
        class_rel_dict.append(
            {
                'id': courseid,
                'name': course['title'],
                'prereq_string': prereq_str,
                'prereqs': prereq_list,
                'isPrereqFor': [],
                'semesterList': [semester]
            }
        )

        # for each item in prereq_list...
        # for prereq in prereq_list:
            # check if in 


def create_d3():
    #create d3 lists (nodes), and (source, target)
    d3_obj = {
        'nodes': [],
        'links': []
    }
    

    for course in class_rel_dict:
        d3_obj['nodes'].append({
            'id': course['id'],
            'name': course['name'],
            'prereq_string': course['prereq_string'],
            # split courseid by : and get 2nd element
            'courseType': course['id'].split(":")[1],
            'prereqSize': len(course['prereqs']),
            'isPrereqForSize': len(course['isPrereqFor'])

        })

        for prereq in course['prereqs']:
            #check if points to null course first... skip this then
            if prereq not in class_rel_dict_index:
                continue

            d3_obj['links'].append({
                'source': prereq,
                'target': course['id']
            })

            # add if not exists
            if course['id'] not in class_rel_dict[class_rel_dict_index.index(prereq)]['isPrereqFor']:
                class_rel_dict[class_rel_dict_index.index(prereq)]['isPrereqFor'].append(course['id'])

    with open('d3_webreg.json', 'w') as outfile:
        json.dump(d3_obj, outfile, separators=(',', ':')) 

    with open('rel_debug.json', 'w') as outfile:
        json.dump(class_rel_dict, outfile, separators=(',', ':'))



for item in listt:
    newData = getCourseData(item[0], item[1])

    # add newData to rel list
    addJSONToRelList(newData, item)

    create_d3()



# try:
#     # ath_relationship_dict = {}

#     class_rel_dict = []
#     class_rel_dict_index = []


#     for i in tqdm(range(len(coursedataJSON))):

#         courseIndex = i

#         course = coursedataJSON[courseIndex]

#         courseid = course['courseString']

#         # print(courseid)

#         # check if course in class_rel_dict_index...
#         if courseid in class_rel_dict_index:
#             continue

#         # parse prereq list...
#         prereq_str = course['preReqNotes']
#         # extract every instance of xx:xxx:xxx from prereq_str where x is a digit
#         prereq_list = []

#         # split by spaces
#         prereq_spaces = prereq_str.split(" ")
#         # for each...
#         for item in prereq_spaces:
#             # check for 2 ":"s
#             if item.count(":") == 2:
#                 # check if all digits
#                 if item.replace(":","").isdigit():
#                     prereq_list.append(item)

#         # group by ()??


#         # add course to class_rel_dict_index
#         # add course to class_rel_dict
#         # add attributes
#         class_rel_dict_index.append(courseid)
#         class_rel_dict.append(
#             {
#                 'id': courseid,
#                 'name': course['title'],
#                 'prereq_string': prereq_str,
#                 'prereqs': prereq_list,
#                 'isPrereqFor': [],
#             }
#         )

#         # for each item in prereq_list...
#         # for prereq in prereq_list:
#             # check if in 

#     #create d3 lists (nodes), and (source, target)
#     d3_obj = {
#         'nodes': [],
#         'links': []
#     }
    

#     for course in class_rel_dict:
#         d3_obj['nodes'].append({
#             'id': course['id'],
#             'name': course['name']
#         })

#         for prereq in course['prereqs']:
#             #check if points to null course first... skip this then
#             if prereq not in class_rel_dict_index:
#                 continue

#             d3_obj['links'].append({
#                 'source': prereq,
#                 'target': course['id']
#             })

#     # for ath_id in adv_ath_relationship_dict.keys():
#     #     #find ath
#     #     localAth = False
#     #     for ath in ath_data:
#     #         if int(ath['id']) == int(ath_id):
#     #             localAth = ath
#     #             break

#     #     #find ath in gender list if events are not empty
#     #     if len(localAth['races']) != 0:
#     #         if str(ath_id) in gender_data['Boys']:
#     #             localAth['gender'] = "m"
#     #         else:
#     #             localAth['gender'] = "f"
#     #     else:
#     #         localAth['gender'] = "n"

#     #     #add node
#     #     d3_obj['nodes'].append({
#     #         'id': str(ath_id),
#     #         #this is where I can add arbitrary things to decorate with, things such as
#     #         # name
#     #         'name': localAth['name'],
#     #         # grad Year
#     #         'gradYear': localAth['graduationYear'],
#     #         # athlete's event count

#     #         # athlete gender
#     #         # actually I need to download the gender file for that
#     #         'gender': localAth['gender']
            
#     #     })

#     #     #add links
#     #     for target_id in adv_ath_relationship_dict[ath_id].keys():
#     #         #round score ('s')
#     #         score = round(round(adv_ath_relationship_dict[ath_id][target_id]['s']) / 20, 1)

#     #         #filter
#     #         for ath in ath_data:
#     #             if int(ath['id']) == int(target_id):
#     #                 if int(ath['graduationYear']) not in grad_year_range:
#     #                     continue

#     #         d3_obj['links'].append({
#     #             'source': str(ath_id),
#     #             'target': str(target_id),
#     #             'value': score
#     #         })
            
                   
#     #store file locally
#     # with open('basic_ath_relationship_dict.json', 'w') as outfile:
#     #     json.dump(ath_relationship_dict, outfile, separators=(',', ':'))

#     # with open('adv_ath_relationship_dict.json', 'w') as outfile:
#     #     json.dump(adv_ath_relationship_dict, outfile, separators=(',', ':'))

#     with open('d3_webreg.json', 'w') as outfile:
#         json.dump(d3_obj, outfile, separators=(',', ':'))

    

#     # do something here
# except Exception as e:
#     logging.critical(e, exc_info=True)
#     # time_taken = int(time.time()) - start_time
#     # logging.info("took " + str(time_taken) + " seconds")
#     logging.info("finished with error (see above).")