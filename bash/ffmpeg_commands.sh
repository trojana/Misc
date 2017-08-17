# get list of files saved in mylist.txt
for f in *.jpg; do echo "$f" >> mylist.txt; done

# concatenate videos in list
# with a bash for loop
for f in ./*.mp4; do echo "file '$f'" >> mylist.txt; done
ffmpeg -f concat -safe 0 -i mylist.txt -c copy output.mp4

# get images from video
ffmpeg -i ResiStreet/output.mp4  -r 15 output_%05d.jpg

# resize images
 ffmpeg -i output_%05d.jpg -vf scale=w=500:h=375 output_%05d.jpg

# remove audio
ffmpeg -i example.mkv -c copy -an example-nosound.mkv

#convert MTS to MP4
IFS=$(echo -en "\n\b"); for i in *.MTS; do ffmpeg -i "$i" -vcodec mpeg4 -b:v 15M -acodec libmp3lame -b:a 192k "$i.mp4"; done

# cut video after specific time 
ffmpeg -i indoor_049.mp4 -ss 00:00:00.0 -t 00:00:10.0 -async 1  -strict -2  cut_indoor_049.mp4

#create GIf
convert -delay 20 -loop 0 *.jpg animated.gif

# autorotate video
for i in *.mp4; do  ffmpeg -i "$i" -c:a copy "rotated$i"; done