#!/bin/bash
# loop over all video files

for d in *.mp4;
do
    
    eval $(ffprobe -v error -of flat=s=_ -select_streams v:0 -show_entries stream=height,width,r_frame_rate,duration -sexagesimal $d)
    IFS=':','.' read -a duration <<< $streams_stream_0_duration
    read hh <<<  ${duration[0]};
    read mm <<<  ${duration[1]};
    read ss <<<  ${duration[2]};
    read ms <<<  ${duration[3]};

       
    if [ ${ss:1:2} == "0" ];
    then
      read s1 <<< $((${ss:0:1}-1));
      read s2 <<< "9";
    else
      read s1 <<< ${ss:0:1};
      read s2 <<< $((${ss:1:2}-1));
    fi
    
    echo "$ss -> $s1$s2"
    ffmpeg -i "$d" -ss 00:00:00.0 -t "$hh:$mm:$s1$s2.0" -async 1  -strict -2  "cut_$d"
    
    
    #echo "${duration[3]}"
    
    #echo "$hh:$mm:$ss.0"
    #ffmpeg -i nosound-00052.MTS.mp4 -ss 00:00:00.0 -t "$hh:$mm:$ss-1.0" -async 1  -strict -2  cut_nosound-00052.MTS.mp4
	# convert video to frames
#	ffmpeg -i $d  -r "${myarray[0]}" $Directoryname/output_%05d.jpg

    
done





