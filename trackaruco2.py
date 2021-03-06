#!/usr/bin/env python
import cv2
import cv2.aruco as aruco
import numpy as np
import paho.mqtt.publish as publish  #import the client1
import paho.mqtt.client as mqtt
import time
import math
import ConfigParser
import os
import sys
#import aruco

config = ConfigParser.ConfigParser()
config.read("settings.ini")
 
vmin =  int(config.get("HSV", "vmin"))
vmax =  int(config.get("HSV", "vmax"))
smin =  int(config.get("HSV", "smin"))
smax =  int(config.get("HSV", "smax"))
hmin =  int(config.get("HSV", "hmin"))
hmax =  int(config.get("HSV", "hmax"))

ctlx =  int(config.get("correction", "tlx"))
#ctly =  int(config.get("correction", "tly"))
ctrx =  int(config.get("correction", "trx"))
#ctry =  int(config.get("correction", "try"))

cblx =  int(config.get("correction", "blx"))
#cbly =  int(config.get("correction", "bly"))

cbw = int(config.get("correction", "bw"))
cby = int(config.get("correction", "by"))
cty = int(config.get("correction", "ty"))

#cbrx =  int(config.get("correction", "brx"))
#cbry =  int(config.get("correction", "bry"))




def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    try:
        client.subscribe("tracker/#")
        print "subscribed"
    except:
        print "WARNING NOT ERROR subscribe inside connect failed"
        pass

def on_message(client1, userdata, message):
    print("message received  "  ,str(message.payload.decode("utf-8")))
    if str(message.payload) == "reset":
        cap.release()
        cv2.destroyAllWindows()
        os.execv(sys.executable, ['python'] + sys.argv)
    
broker_address="127.0.0.1"
mqttclient = mqtt.Client("P1")    #create new instance
mqttclient.on_connect = on_connect        #attach function to callback
mqttclient.on_message=on_message        #attach function to callback
time.sleep(1)
mqttclient.connect(broker_address)      #connect to broker
mqttclient.loop_start()



kernel = np.ones((5,5),np.uint8)

# Take input from webcam
cap = cv2.VideoCapture(-1)

# set resolution
camwidth = 640
camheight = 480
trackwidth = camwidth / 2
trackheight = trackwidth
#trackheight = camheight / 2
cap.set(3,camwidth)
cap.set(4,camwidth)

def order_points(pts):
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype = "float32")

    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # return the ordered coordinates
    return rect

def four_point_transform(image, pts):
    # obtain a consistent order of the points and unpack them
    # individually
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    # dst = np.array([
        # [0, 0],
        # [maxWidth - 1, 0],
        # [maxWidth - 1, maxHeight - 1],
        # [0, maxHeight - 1]], dtype = "float32")
    dst = np.array([
        [0, 0],
        [trackwidth - 1 , 0],
        [trackwidth - 1, trackheight - 1],
        [0, trackheight - 1]], dtype = "float32")

    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    #print M
    #time.sleep(30)
    warped = cv2.warpPerspective(image, M, (trackwidth,trackheight))

    # return the warped image
    return warped
    


def nothing(x):
    pass
# Creating a windows for later use
#cv2.namedWindow('HueComp')
#cv2.namedWindow('SatComp')
#cv2.namedWindow('ValComp')
#cv2.namedWindow('closing')
cv2.namedWindow('Tracking')
cv2.namedWindow('camera')


# Creating track bar for min and max for hue, saturation and value
# You can adjust the defaults as you like
#cv2.createTrackbar('hmin', 'HueComp',hmin,179,nothing)
#cv2.createTrackbar('hmax', 'HueComp',hmax,179,nothing)

#cv2.createTrackbar('smin', 'SatComp',smin,255,nothing)
#cv2.createTrackbar('smax', 'SatComp',smax,255,nothing)

#cv2.createTrackbar('vmin', 'ValComp',vmin,255,nothing)
#cv2.createTrackbar('vmax', 'ValComp',vmax,255,nothing)

#pts = np.array([(ctlx, ctly), (ctrx, ctry), (cblx + cbw, cby), (cblx , cby)])    
cv2.createTrackbar('topleftx', 'Tracking',ctlx,trackwidth,nothing)
#cv2.createTrackbar('toplefty', 'Tracking',ctly,240,nothing)
cv2.createTrackbar('toprightx', 'Tracking',ctrx,trackwidth,nothing)
#cv2.createTrackbar('toprighty', 'Tracking',ctry,240,nothing)
cv2.createTrackbar('bottomleftx', 'camera',cblx,trackwidth,nothing)
cv2.createTrackbar('bottomwidth', 'camera',cbw,trackwidth,nothing)
cv2.createTrackbar('bottomy', 'camera',cby,trackheight,nothing)
cv2.createTrackbar('topy', 'Tracking',cty,trackheight,nothing)
#cv2.createTrackbar('bottomlefty', 'camera',cbly,240,nothing)



# My experimental values
# hmn = 12
# hmx = 37
# smn = 145
# smx = 255
# vmn = 186
# vmx = 255

tick = time.time()
dx = 0
dy = 0
wherex = [0,0]
wherey = [0,0]
wherexav = 0
whereyav = 0
oldx = 0
oldy = 0
dia = [0,0]
direction = 90
olddirection = 0
ball=0
msgx = 0
msgy = 0
msgdir = 0
msgdiff = 0
msgradius = 0 
msgbearing = 0

# load board and camera parameters
#boardconfig = aruco.BoardConfiguration("chessboardinfo_small_meters.yml")
#camparam = cv2.aruco.CameraParameters()
#camparam.readFromXMLFile("dfk72_6mm_param2.yml")

# create detector and set parameters
#detector = cv2.aruco.MarkerDetector()
#params = detector.getParams()

#detector.setParams(camparam)
# set minimum marker size for detection
#markerdetector = detector.getMarkerDetector()
#markerdetector.setMinMaxSize(0.01)

aruco_dict = aruco.Dictionary_get(aruco.DICT_ARUCO_ORIGINAL)
parameters =  aruco.DetectorParameters_create() 
    
try:
    _,camframe = cap.read()
    gray = cv2.cvtColor(camframe, cv2.COLOR_BGR2GRAY)
    # Apply thresholding
    ctlx = cv2.getTrackbarPos('topleftx','Tracking')
    #ctly = cv2.getTrackbarPos('toplefty','Tracking')
    ctrx = cv2.getTrackbarPos('toprightx','Tracking')
    #ctry = cv2.getTrackbarPos('toprighty','Tracking')
    cty = cv2.getTrackbarPos('topy','Tracking')            
    cbrx = cv2.getTrackbarPos('bottomrightx','camera')
    cby = cv2.getTrackbarPos('bottomy','camera')
    cblx = cv2.getTrackbarPos('bottomleftx','camera')
    cbw = cv2.getTrackbarPos('bottomwidth','camera')           

    ctly = cty
    ctry = cty
    crby = cby
    clby = cby
    
    #frame = four_point_transform(capframe, pts) 
    #frame = cv2.resize(capframe,(320,320))      
   
 
    #It's working.
    # my problem was that the cellphone put black all around it. The alrogithm
    # depends very much upon finding rectangular black blobs
 
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)  

    for marker in range(len(ids)):
        if ids.item(marker) < 5:  
            # print marker ID and point positions
            print("Marker: {:d}".format(ids.item(marker)))

            if ids.item(marker) == 1:
                ctlx = int(corners[marker].item(0,2, 0))
                ctly = int(corners[marker].item(0,2, 1))
            if ids.item(marker) == 2:
                ctrx = int(corners[marker].item(0,3, 0))
                ctry = int(corners[marker].item(0,3, 1))
            if ids.item(marker) == 3:
                cbrx = int(corners[marker].item(0,0, 0))
                cbry = int(corners[marker].item(0,0, 1))
            if ids.item(marker) == 4:
                cblx = int(corners[marker].item(0,1, 0))
                cbly =  int(corners[marker].item(0,1, 1))  

            #marker.draw(camframe, np.array([255, 255, 255]), 2)

            # # calculate marker extrinsics for marker size of 3.5cm
            # marker.calculateExtrinsics(0.035, camparam)
            # print("Marker extrinsics:\n{:s}\n{:s}".format(marker.Tvec, marker.Rvec))

            #print("detected ids: {}".format(", ".join(str(m.id) for m in markers)))       
    camframe = aruco.drawDetectedMarkers(camframe, corners)

    cby = cbly
    cbw = cbrx - cblx
    cty = (ctly + ctry) / 2
    
    pts = np.array([(ctlx , cty), (ctrx, cty), (cblx + cbw , cby), (cblx,cby)]) 
    tick = time.time()
    wherex = 0
    wherey = 0
    directon = 0

    #img = cv.QueryFrame(capture)
    gridDrawn = False
    while(True):
        for loop in range(5):
            _, capframe = cap.read()
        #capframe = cv2.QueryFrame(cap)


        frame = four_point_transform(capframe, pts) 
        #frame = cv2.resize(capframe,(320,320))  


        # Apply thresholding
        
        corners, ids, rejectedImgPoints = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)  
        if ids is not None:
            for marker in range(len(ids)):
                # print marker ID and point positions
                if ids[marker] > 4:
                    #print("Marker: {:d}".format(marker.id))
                    wherex =  int((corners[marker].item(0,2, 0)+ corners[marker].item(0,3, 0)) / 2)
                    wherey =  int((corners[marker].item(0,2, 1)+ corners[marker].item(0,3, 1)) / 2)
                    cv2.circle(frame, (wherex, wherey), 20, (255,0,0), 3)
              
                    #print wherex,wherey
                    direction = (int(math.atan2((corners[marker].item(0,1, 1) - corners[marker].item(0,2, 1) ),(corners[marker].item(0,1, 0) - corners[marker].item(0,2, 0) )) * 180.0 / 3.1415926) + 450) % 360
                    frame = aruco.drawDetectedMarkers(frame, corners)


                    #print("detected ids: {}".format(", ".join(str(m.id) for m in markers)))
                     
                    # alphaxy = 0.5 
                    # wherexav = int((((wherex[0] + wherex[1]) / 2.0) * alphaxy) + (wherexav * (1- alphaxy)))
                    # whereyav = int((((wherey[0] + wherey[1]) / 2.0) * alphaxy) + (whereyav * (1- alphaxy)))
                    radius = int(math.sqrt(((wherex - (trackwidth / 2)) * (wherex - (trackwidth / 2))) + (((trackheight / 2) - wherey) * ((trackheight / 2) - wherey))))
                    # alphadir = 0.25
                    # direction = (int(math.atan2((wherey[0] - wherey[1]),(wherex[0] - wherex[1])) * 180.0 / 3.1415926) + 450) % 360

                    # diff = (direction - olddirection + 180) % 360 - 180
                    # diff = diff * alphadir
                    # direction = int((olddirection + diff + 360) % 360)            
                    # olddirection = direction
                    bearing = ((180 - ((int(math.atan2((trackheight / 2) - wherey,wherex - (trackwidth / 2)) * 180.0 / 3.1415926) + 450) % 360)) + 360) % 360
            msgs = []
            if (time.time() - tick) > 0.5:
                #msgs = [("where/radius", radius,0,True)]  + msgs              
                msgs = [("robot/1/robot_x", (wherex - (trackwidth / 2)),0,True)]  + msgs
                msgs = [("robot/1/robot_y",((trackheight / 2) - wherey),0,True)] + msgs
                #print "direction" , direction
                #print "diff", diff
                #msgs = [("where/diff", diff ,0,True)] + msgs
                msgs = [("robot/1/robot_direction", direction,0,True)] + msgs  
                msgs = [("robot/1/robot_radius", radius,0,True)] + msgs                  
                msgs = [("robot/1/robot_bearing", bearing,0,True)] + msgs  

                print msgs
                publish.multiple(msgs, hostname="127.0.0.1")
                   
                tick = time.time()
            #else:
            #    print time.time() - tick
        #cv2.imshow("frame", frame)    
        #if gridDrawn is not True:
        for gridStep in range(1,4):
            cv2.line(frame,(0,(trackheight / 4) * gridStep),(trackwidth,(trackheight / 4) * gridStep),(255,0,0),1)
            cv2.line(frame,((trackwidth / 4) * gridStep,0),((trackwidth / 4) * gridStep,trackheight),(255,0,0),1)            
            gridDrawn = True
        cv2.imshow("camera", camframe)             
        cv2.imshow("Tracking", frame)
  
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
except KeyboardInterrupt:
    print ("Keyboard Interrupt")
    
print "exiting prog"

config.set("HSV", "vmin",str(vmin))
config.set("HSV", "vmax",str(vmax))
config.set("HSV", "smin",str(smin))
config.set("HSV", "smax",str(smax))
config.set("HSV", "hmin",str(hmin))
config.set("HSV", "hmax",str(hmax))

config.set("correction", "tlx",str(ctlx))
config.set("correction", "tly",str(ctly))
config.set("correction", "trx",str(ctrx))
config.set("correction", "try",str(ctry))


config.set("correction", "blx",str(cblx))

config.set("correction", "by",str(cby))
config.set("correction", "bw",str(cbw))
config.set("correction", "ty",str(cty)) 
# write changes back to the config file
with open("settings.ini", "wb") as config_file:
    config.write(config_file)  



cap.release()

cv2.destroyAllWindows()