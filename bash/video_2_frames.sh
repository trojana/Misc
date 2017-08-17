#!/bin/bash

# loop over all video files
for d in *.mp4;
do
    # get filename without extension
    filename=$(basename "$d")
    Directoryname="${filename%.*}"
    #extension="${filename##*.}"
    
    # check if directory exist
    if [ ! -d "$Directoryname" ]; then
    
	echo $(mkdir "$Directoryname")
	
	#get frameRate	
	eval $(ffprobe -v error -of flat=s=_ -select_streams v:0 -show_entries stream=height,width,r_frame_rate $d)
	IFS='/' read -a myarray <<< "$streams_stream_0_r_frame_rate"

	# convert video to frames
	ffmpeg -i $d  -r "${myarray[0]}" $Directoryname/output_%05d.jpg
    fi
    
done





