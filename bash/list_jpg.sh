#!/bin/bash
# list all directories
 

: <<'END'
# fill in empty "black frames"
for i in {1..300};
do
    echo "file '/media/sf_OC_RESINET/process/ResiIndoor05-Pond5/empty.jpg'" >> jpg_list.txt;
    echo "duration 0.05" >> jpg_list.txt;
done


for iFolder in $(ls -d /media/sf_OC_RESINET/process/ResiIndoor05-Pond5/*/); 
do
    echo $iFolder
    
    # for initialization  fill in 100 first frames (which will be ignored)
    for i in {1..100};
    do
	echo "file '$iFolder""output_00001.jpg'" >> jpg_list.txt;
	echo "duration 0.05" >> jpg_list.txt;
    done
    
    
    for iFile in $iFolder*.jpg; 
    do 
	echo "file '$iFile'" >> jpg_list.txt; 
	echo "duration 0.05" >> jpg_list.txt;
    done
done

#ffmpeg -f concat -safe 0 -i jpg_list_short.txt -c:v libx264 output.mp4


for iFolder in $(ls -d /media/sf_OC_RESINET/process/ResiIndoor05-Pond5/*/); 
do
	echo $iFolder	
	echo "$iFolder" >> info_jpg_list.txt;
	shopt -s nullglob
	numfiles=($iFolder*.jpg)
	numfiles=${#numfiles[@]}
	#aa = $(ls -1q $iFolder*.jpg | wc -l)
	echo $numfiles
	echo "100" >> info_jpg_list.txt;
	echo "$numfiles" >> info_jpg_list.txt;
done
END

declare -i counter=0
destinationDirectory='/media/sf_OC_RESINET/process/ResiIndoor05-Pond5-All/'
empty_file='/media/sf_OC_RESINET/process/ResiIndoor05-Pond5/empty.jpg' 
iFolder='/media/sf_OC_RESINET/process/ResiIndoor05-Pond5/front_door_001/'
# there are first 200 empty frames to run RTSP Camera simulator + Sighthound
for i in {1..200};
	do
		counter=$counter+1
		prefix=$(printf "%05d\n" $counter)
		basename=${empty_file##*/}
		echo $destinationDirectory$prefix"_"${basename%%-*}
		cp -a $empty_file $destinationDirectory$prefix"_"${basename%%-*}	
	done
for iFolder in $(ls -d /media/sf_OC_RESINET/process/ResiIndoor05-Pond5/*/); 	
do
	for i in {1..100};
	do
		counter=$counter+1
		prefix=$(printf "%05d\n" $counter)
		basename=${empty_file##*/}
		echo $destinationDirectory$prefix"_"${basename%%-*}
		cp -a $empty_file $destinationDirectory$prefix"_"${basename%%-*}	
	done
	for file in $iFolder*.jpg; do
		counter=$counter+1
		prefix=$(printf "%05d\n" $counter)
		basename=${file##*/}
		echo $destinationDirectory$prefix"_"${basename%%-*}
		cp -a $file $destinationDirectory$prefix"_"${basename%%-*}
	done
done