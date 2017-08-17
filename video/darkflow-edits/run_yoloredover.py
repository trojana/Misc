# !python

import os
import sys
import cv2
import re
import numpy as np
from darkflow.net.build import TFNet
from track.eliminateoverlaps import *
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

# colors for different bboxes for visualization
colors = [(255,0,0), (0,255,0),(0,0,255),(255,255,0),(0,255,255),(255,0,255),(192,192,192),(128,128,128),
          (128,0,0),(128,128,0),(0,128,0),(128,0,128),(0,128,128),(0,0,128),(0,0,0)]

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
alleldets = []
while True:
    # read the image in
    if working_directory:
        ret=frmcnt<len(files_in_directory)
        if ret:
            file_name=files_in_directory[frmcnt]
            imgcv = cv2.imread(file_name)
    else:
        ret, imgcv = cap.read()
        file_name=''
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
    # eliminate overlaps
    eldets=eliminate1(dets0,0.80,0.60,2.0)
    # store the detections 
    alleldets += list(map(lambda bb: fn + ',' + ','.join(list(map(lambda x: str(x),bb))),eldets))  # save the detections    

    # count the frames
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
        for idx, bbo_f in enumerate(eldets):
            # print('bbo_f: ', bbo_f )
            bbo = list(map(lambda x: int(round(float(x))), bbo_f[0:4]))
            obsc = bbo_f[4]
            label = bbo_f[5]
            cv2.rectangle(img1, (bbo[0], bbo[1]), (bbo[2], bbo[3]), colors[idx%len(colors)], 10)
            cv2.rectangle(img1, (bbo[0], bbo[1]-30), (bbo[2], bbo[1]), colors[idx%len(colors)], -1)
            cv2.putText(img1, label+' %0.2f'%obsc, (bbo[0]+5, bbo[1]-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), 2)
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
    
# record the detections
if outp:
    outp_dets = re.sub(r'(csv|txt)',r'dets.\1',outp)
    if os.path.isfile(outp_dets):
        sys.exit('ERROR: '+outp_dets+' already exists.')
    outp_eldets = re.sub(r'(csv|txt)',r'eldets.\1',outp)
    if os.path.isfile(outp_eldets):
        sys.exit('ERROR: '+outp_eldets+' already exists.')

    content = '\n'.join(alldets)
    with open(outp_dets, 'w') as fro:
        fro.write(content)
    print('Wrote yolo detections into: '+outp_dets)

    content = '\n'.join(alleldets)
    with open(outp_eldets, 'w') as fro:
        fro.write(content)
    print('Wrote yolo+redover detections into: '+outp_eldets)
