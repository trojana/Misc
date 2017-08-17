# !python

import os
import sys
import cv2
import re
import numpy as np
from darkflow.net.build import TFNet
import track.sort.sort as srt
import time

# usage and arguments
usage = "Usage: python " + str(sys.argv[0]) + "input_video=/dev/video0 frame_limit=100 output_csv= output_dir="

argv = sys.argv[1:]
vidin='/dev/video0'
if len(argv)>0:
    vidin=argv[0]
    if(vidin == '-h'):
        sys.exit(usage)
endcnt=100
if len(argv)>1:
    endcnt=int(argv[1])
outp=''
if len(argv)>2:
    outp=argv[2]
outdir=''
if len(argv)>3:
    outdir=argv[3]
    if not os.path.isdir(outdir):
        print('WARNING: '+outdir+' does not exist or not directory.')
        outdir=''

# initialize the input source
working_directory=''
if os.path.isdir(vidin):
    # directory with images from video
    #working_directory = '/home/analyticsuser/data/Husband Surprises Wife by Filling House With Puppies!'
    #working_directory = '/home/analyticsuser/data/Nest Cam - Owner catches burglars in act on her phone'
    working_directory = vidin

    # only images
    files_in_directory = sorted([os.path.join(working_directory, file_name)
                          for file_name in os.listdir(working_directory)
                          if os.path.splitext(file_name)[1].lower() in ('.jpg', '.jpeg')])
    file_name=files_in_directory[0]
    imgcv = cv2.imread(file_name)
else:
    # let's read from video
    # cap = cv2.VideoCapture('/home/analyticsuser/data/front_door_001.mp4')
    # cap = cv2.VideoCapture('/home/analyticsuser/data/ResiIndoor03-YT_Indoor-family2_720.2.mp4')
    cap = cv2.VideoCapture(vidin)
    # get image size
    ret, imgcv = cap.read()

# configuration for YOLO
options = {'model': '/home/analyticsuser/darkflow/cfg/yolo.2.0.cfg', 
           'load': '/home/analyticsuser/darkflow/cfg/yolo.2.0.weights', 'threshold': 0.1}
#options = {'model': '/home/analyticsuser/darkflow/cfg/tiny-yolo.cfg', 
#           'load': '/home/analyticsuser/darkflow/cfg/tiny-yolo.weights', 'threshold': 0.1}
tfnet = TFNet(options)

# initialize SORT tracker:
# - 10 consecutive frames with no detection to terminate an existing track
# - 1 consecutive frame (i.e. after an initial frame) to activate the new track (before that will not produce any output)
# - 5 frames to extrapolate an active track (i.e. show predicted output eventhough no detection present for this track)
# - 0.8 unassigned detection over track bbox overlap (intersection over union) threshold to eliminate the detection
# - 0.94 unassigned detection over another stronger unassigned detection overlap (intersection over self bbox area) threshold to eliminate the detection
# - 0.8 unassigned detection over another stronger unassigned detection overlap (intersection over larger bbox area) threshold to eliminate the detection
# - 2.0 defines "stronger" detection disregarding the size -- if the score of the unassigned detection overlapping 
#       another unassigned detection is 2.0-times higher than the score of the other detection, it is stronger, otherwise 
#       larger size decides
# mot_tracker = srt.Sort(10,1,5,0.8,0.94,0.8,2.0)
mot_tracker = srt.Sort(1,0,0,0.55,0.8,0.6,2.0)

# get image size
height = np.size(imgcv, 0)
width = np.size(imgcv, 1) 
print( 'Processing first '+str(endcnt)+' frames of video input '+vidin )
print( 'Frame dimensions: ', width, ' x ', height )
if outdir:
    print('Output will be stored to: '+outdir)


# time measurement
print('Stopwatch running... (be patient)' )
stme = time.time()
frmcnt=0

# processing all
alldets = []
allobjs = []
endcnt=100
#for file_name in files_in_directory[::1]:
while True:
    # read the image in
    if working_directory:
        ret=frmcnt<len(files_in_directory)
        if ret:
            file_name=files_in_directory[frmcnt]
            imgcv = cv2.imread(file_name)
    else:
        ret, imgcv = cap.read()
    if not ret or frmcnt>=endcnt:
        break

    # run YOLO
    result = tfnet.return_predict(imgcv)
    
    # filter resulting detections by object type
    fres = list(filter(lambda x: x['label'] == 'person' or x['label'] == 'dog' or x['label'] == 'cat',result))
    # reformat
    dets0 = list(map( lambda x: [float(x['topleft']['x']),float(x['topleft']['y']),
                                 float(x['bottomright']['x']),float(x['bottomright']['y']),
                                 x['confidence'],x['label']], fres))
    # store the detections 
    fn=file_name if file_name else 'output_%05d'%(frmcnt+1)+'.png'
    alldets += list(map(lambda bb: fn + ',' + ','.join(list(map(lambda x: str(x),bb))),dets0))  # save the detections    
    # run tracker
    dets = np.asarray( dets0 )
    objs, eltracks = mot_tracker.update(dets)
    allobjs += list(map(lambda bb:fn+','+str(int(bb[5]))+','+','.join(list(map(lambda x: str(float(x)),bb[0:5]))),objs))  
    frmcnt+=1

    # record results if requested
    if outdir:
        img1 = imgcv.copy()
        for idx, detection in enumerate(result):
            if detection['label'] == 'person' or detection['label'] == 'dog' or detection['label'] == 'cat':
                cv2.rectangle(imgcv, (detection['topleft']['x'], detection['topleft']['y']), 
                          (detection['bottomright']['x'], detection['bottomright']['y']), 
                          colors[idx % len(colors)], 10)
                cv2.rectangle(imgcv, (detection['topleft']['x'], detection['topleft']['y'] - 20), 
                          (detection['bottomright']['x'], detection['topleft']['y']), (125, 125, 125), -1)
                cv2.putText(imgcv, detection['label'] + ' : %.2f' % detection['confidence'], 
                        (detection['topleft']['x'] + 5, detection['topleft']['y'] - 7), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        for idx, bbo_f in enumerate(objs):
            # print('bbo_f: ', bbo_f )
            bbo = list(map(lambda x: int(round(float(x))), bbo_f[0:4]))
            obsc = bbo_f[4]
            obid = int(bbo_f[5])
            cv2.rectangle(img1, (bbo[0], bbo[1]), (bbo[2], bbo[3]), colors[idx%len(colors)], 10)
            cv2.rectangle(img1, (bbo[0], bbo[1]-30), (bbo[2], bbo[1]), colors[idx%len(colors)], -1)
            cv2.putText(img1, 'id%03d'%obid+' @ %0.2f'%obsc, (bbo[0]+5, bbo[1]-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), 2)
        cv2.rectangle(img1, (width-200, height-30), (width-1, height-1), (255,0,0), -1)
        cv2.putText(img1, '%05d'%frmcnt, (width-195, height-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), 2)
        resimg = np.concatenate((imgcv, img1), axis=1)
        outfnm = outdir+'/'+'output_%05d'%frmcnt+'.png'
        if os.path.isfile(outfnm):
            print( 'WARNING: file '+outfnm+' already exist' )
        else:
            cv2.imwrite(outfnm,resimg)    
    
# time measurement
etme = time.time()
secs=etme-stme
print('Done. Processing speed: ', '%.3f'%(frmcnt/secs), ' fps (', secs, ' secs, ', frmcnt, ' frames)')
    
# content = '\n'.join(alldets)
# with open('yolodet.txt', 'w') as fro:
#     fro.write(content)
    
# content = '\n'.join(allobjs)
# with open('yolosortobjs.txt', 'w') as fro:
#     fro.write(content)
