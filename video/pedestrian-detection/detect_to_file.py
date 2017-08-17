# USAGE
# python detect.py --images images

# import the necessary packages
from __future__ import print_function
from imutils.object_detection import non_max_suppression
from imutils import paths
import numpy as np
import argparse
import imutils
import cv2
import ntpath
import os, re


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--images", required=True, help="path to images directory")
args = vars(ap.parse_args())

# initialize the HOG descriptor/person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# loop over the image paths
imageFolder = args["images"]
#imagePaths = list(paths.list_images(args["images"] + "."))

# get list of input files
ls = os.listdir(imageFolder)
imagePaths = list(filter(lambda x: re.match('\S+\d+\.jpg', x),ls))

outfile = imageFolder + "HOGdetector_output.csv"

for imagePath in imagePaths:
	# load the image and resize it to (1) reduce detection time
	# and (2) improve detection accuracy
	image = cv2.imread(imageFolder + imagePath)
	scale = float(image.shape[1]*0.0025)
	#print(scale)
	#imagePath = ntpath.basename(imagePath)
	image = imutils.resize(image, width=min(400, image.shape[1]))
	orig = image.copy()

	# detect people in the image
	(rects, weights) = hog.detectMultiScale(image, winStride=(4, 4),
		padding=(8, 8), scale=1.05)

	# draw the original bounding boxes
	for (x, y, w, h) in rects:
		cv2.rectangle(orig, (x, y), (x + w, y + h), (0, 0, 255), 2)

	# apply non-maxima suppression to the bounding boxes using a
	# fairly large overlap threshold to try to maintain overlapping
	# boxes that are still people
	rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
	pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)

	# draw the final bounding boxes
	for (xA, yA, xB, yB) in pick:
		cv2.rectangle(image, (xA, yA), (xB, yB), (0, 255, 0), 2)
    
	for i in range(0,len(pick)):
		with open(outfile,'a') as file:
			x1 = pick[i,0] * scale
			y1 = pick[i,1] * scale
			x2 = pick[i,2] * scale 
			y2 = pick[i,3] * scale
			#print(pick[i,:])
			file.writelines("{},{},{},{},{},{}\n".format(imagePath,x1,y1,x2,y2,"1,0,0,0,0"))

	# show some information on the number of bounding boxes
	filename = imagePath[imagePath.rfind("/") + 1:]
	print("[INFO] {}: {} original boxes, {} after suppression".format(
		filename, len(rects), len(pick)))

	# show the output images
	#cv2.imshow("Before NMS", orig)
	#cv2.imshow("After NMS", image)
	#cv2.waitKey(0)
	#print(imagePath)
    
	#pngout = imagePath + '_out.jpg'
	#cv2.imwrite(pngout,image)
