
import cv2


#fig=plt.figure(figsize=(16,8), dpi= 80, facecolor='w', edgecolor='k')

#cam = "http://192.168.56.1:5000/video_feed"
#cam = "rtsp://192.168.56.1:554/s1.dsp"
cam = "/home/analyticsuser/data/front_door_001.mp4"
#cam  = "https://www.youtube.com/watch?v=2FmcHiLCwTU"
#cam  = 0 #webcamera

cap = cv2.VideoCapture(cam)
print( cap )
