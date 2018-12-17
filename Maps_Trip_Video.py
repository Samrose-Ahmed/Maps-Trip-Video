import googlemaps
import os
import numpy
import json
import polyline
import math
import requests
import re
from geographiclib.geodesic import Geodesic
from StringIO import StringIO
from PIL import Image
import cv2

def twoPtBearing(pt1,pt2):
    return (Geodesic.WGS84.Inverse(pt1[0], pt1[1], pt2[0], pt2[1]))['azi1']

def twoPtDist(pt1,pt2):
    return (Geodesic.WGS84.Inverse(pt1[0], pt1[1], pt2[0], pt2[1]))['s12']
    
def movebyDistAlongLine(pt1, pt2,dist):
    bearing=twoPtBearing(pt1,pt2)
    
    outGeoDict=Geodesic.WGS84.Direct(pt1[0], pt1[1], bearing ,dist)
    return(outGeoDict['lat2'],outGeoDict['lon2'])

#fix
def averageBearing(b1,b2):
    b1=math.degrees(b1)
    b2=math.degrees(b2)
    if (b1 > b2):
        temp = b1
        b1 = b2
        b2 = temp
    if (b2 - b1> 180): 
        b2 -= 360
 
    bfin = (b1 + b2)/2
 
    if (bfin < 0):
       bfin += 360
        
    return math.radians(bfin)



myKey='MY_KEY'
gmaps=googlemaps.Client(myKey)

directions_result = gmaps.directions("40.720677, -73.988931",
                                     #"40.721449, -73.988543",
                                     "40.721301, -73.987934",
                                     mode="driving")

#Distance between streetview captures in meters
captureInterval=10

pts=polyline.decode(directions_result[0]['overview_polyline']['points']);

k=0
for i in range(0,len(pts)-1):
    startPt=pts[i]
    endPt=pts[i+1]
    bearing=twoPtBearing(startPt,endPt)
    
    while twoPtDist(startPt,endPt)>captureInterval:
        parameters= {'size':'600x600',
                     'location':str(startPt[0])+','+str(startPt[1]),
                     'heading':str(bearing),
                     'source':'outdoor',
                     #'signature':,
                     'key':myKey}
        
        response=requests.get('https://maps.googleapis.com/maps/api/streetview',params=parameters)

        imgfile=Image.open(StringIO(response.content))
        imgfile.save('img'+str(k)+'.jpg')
        print('Saving img'+str(k)+'.jpg')
        
        k+=1
        startPt=movebyDistAlongLine(startPt,endPt,captureInterval)
   
    if i<len(pts)-2:
        print('Making a turn')
        nextAngle=twoPtBearing(endPt,pts[i+2]) 
            
        parameters["heading"]=str(averageBearing(bearing,nextAngle))
        response=requests.get('https://maps.googleapis.com/maps/api/streetview',params=parameters)

        imgfile=Image.open(StringIO(response.content))
        imgfile.save('img'+str(k)+'.jpg')
        print('Saving img'+str(k)+'.jpg')
        k+=1

fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter('output.avi',fourcc,24,(600,600))
for i in range(k):
    img= cv2.imread('img'+str(i)+'.jpg')
    out.write(img)
    os.remove('img'+str(i)+'.jpg')
out.release()

   
       



    






    
