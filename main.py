from fastapi import FastAPI,Query,Request
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import HTMLResponse
from typing import List
from fastapi.responses import FileResponse
from starlette.responses import StreamingResponse

import io
from PIL import Image

import os
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv
import folium
import random

# import matplotlib.pyplot as plt
# import pandas as pd
import json
from ast import literal_eval
import networkx as nx




# ////////
path = "/Users/arunloganathan/Desktop/Boyd-Orr/glasgow-security-squad/fastApi/api"

        




app = FastAPI()


@app.get("/",response_class=HTMLResponse)
def  read_root():

    location_data = pd.read_csv('location_data.csv')

    #extracting geolocation and building name columns from location_data
    columns1 = ["Geolocation", "Building Name"]
    bl = pd.read_csv("location_data.csv", usecols=columns1)


    #extracting student ids and subject columns from people_data
    columns2 = ["Student ID", "Subject"]
    p_s= pd.read_csv("people_data.csv", usecols=columns2, index_col=None)

    #extracting subject column from people_data and removing duplicates
    keywords = ["Subject"]
    subjects = pd.read_csv("people_data.csv", usecols=keywords, index_col=None)
    subjectsnew = np.unique(subjects).tolist()

    #creating an empty list for every subject and placing it in a dictionary
    student_subjects = {}
    for subject in subjectsnew:
        student_subjects[subject] = []

    #zipping student ids and subjects --> (student1, subject1), ..... (studentn, subjectn)
    #adding each student as a value to the individual subjects
    for student, subject in (zip(p_s["Student ID"], p_s["Subject"])):
        student_subjects[subject].append(student)

    subject_student_num = {}
    for subject in student_subjects:
        subject_student_num[subject] = len(student_subjects[subject])


    plt.rcParams['font.size'] = '4'
    plt.bar(subject_student_num.keys(), subject_student_num.values())
    plt.xlabel('Major title')
    plt.ylabel('Number of students')
    plt.title('Number of students studying the same major')
    plt.savefig(fname = "graph")

    #creating a map of the buildings
    lat_list = []
    long_list = []
    building_location = pd.read_csv("location_data.csv")
    building_location = building_location[["Building Name", "Geolocation"]]

    for geolocation in building_location["Geolocation"]:
        [lat_str, long_str] = geolocation[1:-1].split(" ")
        lat = float(lat_str)
        lat_list.append(lat)
        long = float(long_str)
        long_list.append(long)

    building_name_loc = {}
    building_name_loc["Queen Maragret Building"] = [55.8736412, -4.2915321]

    security_logs = pd.read_csv("security_logs.csv")


    map = folium.Map(location=[np.mean(lat_list), np.mean(long_list)], zoom_start= 17, control_scale= True)
    i = 0
    for lat, long in zip(lat_list, long_list):
        building_name =  building_location["Building Name"][i]
        folium.Marker([lat, long], popup= building_name).add_to(map)
        building_name_loc[building_name] = [lat, long]
        i += 1


    folium.raster_layers.TileLayer('Open Street Map').add_to(map)
    # folium.raster_layers.TileLayer('Stamen Toner').add_to(map)
    # folium.raster_layers.TileLayer('CartoDB Dark_Matter').add_to(map)

    def student_geolocation(name):
        sl = [] #sl = student locations
        i=0
        for student in security_logs["Name"] :
            buildingname = security_logs["Location"][i]
            geolocation = building_name_loc[buildingname]
            if student == name:
                sl.append(geolocation)
            i += 1
        return sl
    color = ['#e079db', '#23d620', '#d14336', '#cc12e5', '#b9ef6e', '#3897a5', '#319e12']

    sus_students = ["Abdul Murphy", "Carolyn Bond", "Martin Smith", "Joanna Lynch", "Keith Saunders", "Keith Wood", "Marilyn White"]

    for color, student in zip(color ,sus_students):
        loc = student_geolocation(student)
        folium.PolyLine(loc,
                    color= color,
                    popup= (student),
                    weight=5,
                    opacity=0.5).add_to(map)
  
    return HTMLResponse(content=map.get_root().render(), status_code=200)


@app.get("/items/")
async def read_items(request: Request):

    a = await request.json()
    print(a["books"])

    return a["books"]


@app.get("/standardDeviation")
async def read_root():
    return {"res":"standard deviation"}


@app.get("/pieChart1")
async def read_root():
    return {"res":"pieChart1"}

@app.get("/pieChart2")
async def read_root():
    return {"res":"pieChart2"}


@app.get("/venDiagram")
async def read_root():
    return {"res":"Ven diagram"}




@app.get("/networkImage")
async def read_root():

    location_data = pd.read_csv('location_data.csv', delimiter=',')
    people_data = pd.read_csv('people_data.csv', delimiter=',', on_bad_lines='skip')

    subjects = people_data["Subject"]
    names = people_data["Name"]
    subjects_dict = {}
    for i in range(len(subjects)):
        subjects_dict[names[i]] = subjects[i]

    societies = people_data["Societies"]
    societies = filter(lambda x: not pd.isna(x), societies)
    societies = map(lambda x: literal_eval(x), societies)
    societies = [item for sublist in list(societies) for item in sublist]
    societies = list(set(societies))
    societies_dict = {society: [] for society in societies}


    societies_two = people_data["Societies"]
    for i in range(len(people_data)):
        if pd.isna(societies_two[i]):
            continue
        for society in literal_eval(societies_two[i]):
            societies_dict[society].append(names[i])
            

            
    relation_one = []
    relation_two = []
    for soc in societies_dict:
        socsNum = len(societies_dict[soc])
        for i in range(socsNum):
            for j in range(i+1, socsNum):
                si = societies_dict[soc][i]
                sj = societies_dict[soc][j]
                if si != sj and subjects_dict[si] == subjects_dict[sj]:
                        relation_one.append(si)
                        relation_two.append(sj)
                        
                        
    df = pd.DataFrame(
        {'ones': relation_one,
        'twos': relation_two,
        })
    G = nx.from_pandas_edgelist(df, "ones", "twos")

    # If you want to include people who aren't
    # related to anyone as isolated nodes
    # uncomment the following

    # loners = []
    # for index, row in df.iterrows():
    #     if pd.isna(row[1]):
    #         loners.append(row[0])
    # for loner in loners:
    #     G.add_node(loner)
        
    pos = nx.spring_layout(G)
    plt.figure(1,figsize=(40, 40)) 
    nx.draw(G, pos, with_labels=True, node_size=100, font_size=8)
    plt.savefig("networkx")
  
    image = Image.open("./networkx.png")
    # image.thumbnail((500, 500))
    imgio = io.BytesIO()
    image.save(imgio, 'png')
    imgio.seek(0)
    return StreamingResponse(content=imgio, media_type="image/png")
