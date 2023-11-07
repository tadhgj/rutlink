# for json file parsing
import json

# for saving files
import sys
import os
import io

# for scraping associated webpages
from bs4 import BeautifulSoup

# for making network requests
import requests as requests
# for ignoring errors
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

# for a pretty terminal progress bar
from tqdm import tqdm

# for parsing dates
import datetime

# for getting the current semester
import read_term_schedule

# for database
import sqlite3
import uuid


# set up database under data/webreg/building.db
conn = sqlite3.connect('data/webreg/building.db')
c = conn.cursor()
# create tables


def dropCreate(name, columns):
    c.execute("DROP TABLE IF EXISTS "+name)
    colStr = ""
    for i in range(len(columns)):
        colStr += columns[i] + " text"
        if i != len(columns)-1:
            colStr += ", "
    c.execute("CREATE TABLE IF NOT EXISTS "+name+" ("+colStr+")")

dropCreate("Buildings", ["buildingid", "buildingdigitid, bulidingcharid", "origname", "name", "category", "categories", "latitude", "longitude"])


#https://sis.rutgers.edu/soc/
#this can convert PH -> to PHARMACY & id:3750
# yes, even without specifying any semester or anything,
# the webpage contains all of the building codes and names
# why? don't know, don't care. it's very quick and easy
# so I'm not complaining


# handle network requests
s = requests.Session()

def download_file(url):
    # ignore errors
    disable_warnings(InsecureRequestWarning)

    # Make the request to download the file
    response = s.get(url, stream=True, verify=False)

    # Get the total file size in bytes
    total_size_in_bytes = int(response.headers.get('content-length', 0))

    # Create a progress bar with the total file size
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)

    # Create a BytesIO object to hold the downloaded data
    data = io.BytesIO()

    # Iterate over the response content in blocks of 1024 bytes
    for chunk in response.iter_content(chunk_size=1024):
        # Write the chunk to the BytesIO object
        data.write(chunk)

        # Update the progress bar with the number of bytes written
        progress_bar.update(len(chunk))

    # Close the progress bar
    progress_bar.close()

    # Return the downloaded data as a bytes object
    return data.getvalue()




#nameConversion
nameConvertUrl = "https://sis.rutgers.edu/soc/"
# print(nameConvertUrl)
# r = requests.get(nameConvertUrl)

print("Downloading building name data...")
r = download_file(nameConvertUrl)
print("Building name data downloaded.")

# reading building name data
print("Parsing building name data...")
soup = BeautifulSoup(r, features="html.parser")
jsonDiv = json.loads(soup.find('div', {"id": "initJsonData"}).text)
buildingsInitial = jsonDiv["buildings"]
print("Building name data parsed.")

# buildingCodes = [d["code"] for d in jsonDiv["buildings"]]
# buildingNames = [d["name"] for d in jsonDiv["buildings"]]
# buildingIDs = [d["id"] for d in jsonDiv["buildings"]]

# print(buildingCodes)
# print(buildingNames)
# print(buildingIDs)



# def getBuildingID(buildingCodeAbbrev):
#     tempIndex = buildingCodes.index(buildingCodeAbbrev)
#     return {
#         "name": buildingNames[tempIndex],
#         "id": buildingIDs[tempIndex]
#     }


#get coords of buildings
#for now, import file. later, pull directly from URL
#buildingLayer = open("fromMap/buildings-parking-layer.json")


# simple: request this URL and see what it then requests
# https://maps.rutgers.edu/api/syncId
# this page returns 
# {"syncId":"1697578574042 (Oct 17, 2023, 5:36 PM EDT)"}
# PERFECT

# works
def getMapJsonFile():
    # get sync id
    syncIdURL = "https://maps.rutgers.edu/api/syncId"

    # print(syncIdURL)
    syncIdRequest = download_file(syncIdURL)

    syncIdJSON = json.loads(syncIdRequest)
    syncId = syncIdJSON['syncId']

    # get buildings-parking-layer
    buildingsParkingLayerURL = "https://storage.googleapis.com/rutgers-campus-map-prod-public-sync/"+syncId+"/buildings-parking-layer.json"

    # buildingsParkingLayerRequest = requests.get(buildingsParkingLayerURL)
    # print(buildingsParkingLayerURL)
    buildingsParkingLayerRequest = download_file(buildingsParkingLayerURL)


    buildingsParkingLayerJSON = json.loads(buildingsParkingLayerRequest)
    return buildingsParkingLayerJSON


print("Downloading building layer data...")
buildingsAdditional = getMapJsonFile()
buildingLayerJson = buildingsAdditional
print("Building layer data downloaded.")

buildingLayerIndex = [d["id"] for d in buildingLayerJson['features']]
print(buildingLayerIndex)

def getBuildingGeoData(buildingID):
    if buildingID in buildingLayerIndex:
        curr = buildingLayerJson['features'][buildingLayerIndex.index(buildingID)]
        return {
            "geometry": curr['geometry'],
            "properties": curr['properties']
        }
    else:
        return None



# put it together
# for each building, add building char id to BuildingOriginal
for i in range(len(buildingsInitial)):
    print("Adding building "+str(i+1)+" of "+str(len(buildingsInitial))+" to database...")
    # create UUID
    buildingDBID = uuid.uuid4().hex

    # define everything
    # print(buildingsInitial[i])
    buildingdigitid = buildingsInitial[i]["id"]
    origname = buildingsInitial[i]["name"]
    # try to get further information...
    buildingcharid = buildingsInitial[i]["code"]
    name = ""
    category = ""
    categories = ""
    latitude = ""
    longitude = ""
    buildingExtendedData = getBuildingGeoData(buildingdigitid)
    if buildingExtendedData != None:
        # print(buildingExtendedData['properties'])
        name = buildingExtendedData["properties"]["name"]
        category = buildingExtendedData["properties"]["category"]
        categories = ""
        if "categories" in buildingExtendedData["properties"]:
            categories = buildingExtendedData["properties"]["categories"]
            categories = ", ".join(categories)
        latitude = buildingExtendedData["properties"]["lat"]
        longitude = buildingExtendedData["properties"]["lng"]
    else:
        print("Building "+buildingsInitial[i]["name"]+" not found in buildingsAdditional")

    # print("ready to add:")
    # print(buildingDBID)
    # print(buildingdigitid)
    # print(buildingcharid)
    # print(origname)
    # print(name)
    # print(category)
    

    c.execute("INSERT INTO Buildings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (buildingDBID, buildingdigitid, buildingcharid, origname, name, category, categories, latitude, longitude))
    

# disconnect from db
conn.commit()
conn.close()