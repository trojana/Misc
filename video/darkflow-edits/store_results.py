import os
import sys
import cv2
import numpy as np
from darkflow.net.build import TFNet
import track.sort.sort as srt
import pandas as pd
import datetime
import imageio

def main():
    # colors for different bboxes for visualization
    colors = [(255,0,0), (0,255,0),(0,0,255),(255,255,0),(0,255,255),(255,0,255),(192,192,192),(128,128,128),
              (128,0,0),(128,128,0),(0,128,0),(128,0,128),(0,128,128),(0,0,128),(0,0,0)]

    # configuration for YOLO
    options = {'model': '/home/analyticsuser/darkflow/cfg/yolo.2.0.cfg',
               'load': '/home/analyticsuser/darkflow/cfg/yolo.2.0.weights', 'threshold': 0.1}
    # options = {'model': '/home/analyticsuser/darkflow/cfg/tiny-yolo.cfg',
    #            'load': '/home/analyticsuser/darkflow/cfg/tiny-yolo.weights', 'threshold': 0.1}

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
    mot_tracker = srt.Sort(10,1,5,0.8,0.94,0.8,2.0)

    # init a camera reader
    cap = cv2.VideoCapture('/home/analyticsuser/data/front_door_001.mp4')
    #cap = cv2.VideoCapture(0)


    # init a dataframe with raw detections
    raw_detections = pd.DataFrame(columns=('Date', 'Timestamp', 'ID', 'Filename',
                                           'TopLeftX', 'TopLeftY', 'BottomRightX', 'BottomRightY', 'Confidence'))

    current_directory = os.getcwd()
    # creating root directory for surveillance results
    root_directory = os.path.join(current_directory, 'Surveillance_results_dummy')
    if not os.path.exists(root_directory):
        os.mkdir(root_directory)
    os.chdir(root_directory)

    # a file for storing high-level information about detections
    detections_info_file = 'Test_' + datetime.date.strftime(datetime.datetime.now(),'%Y-%m-%d %H-%M') + '.csv'
    with open(detections_info_file, 'w') as output:
        output.write('Date,Timestamp,ID,Duration,Filename\n')

    # creating a directory for frames with some detections
    raw_images_directory = os.path.join(root_directory, 'raw_images')
    if not os.path.exists(raw_images_directory):
        os.mkdir(raw_images_directory)

    gifs_directory = os.path.join(root_directory, 'gifs')
    if not os.path.exists(gifs_directory):
        os.mkdir(gifs_directory)
 
    number_of_processed_images = 0 
    start_check_time = datetime.datetime.utcnow()
    def millis():
        dt = datetime.datetime.utcnow() - start_check_time
        ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
        return ms
    times_detection = []
    
    
    while (True):
        ret, image_opencv = cap.read()
        # print(ret)
        # print(type(image_opencv))

        start_check_time = datetime.datetime.utcnow()
        result = tfnet.return_predict(image_opencv)
        times_detection.append(millis())

        # tracking
        persons = list(filter(lambda x: x['label'] == 'person', result))
        detections = np.asarray(list(map(lambda x: [float(x['topleft']['x']), float(x['topleft']['y']),
                                    float(x['bottomright']['x']), float(x['bottomright']['y']),
                                    x['confidence']], persons)))

        tracker_results, recently_dismissed_ids = mot_tracker.update(detections)

        if len(tracker_results):
            current_time = datetime.datetime.now()
            file_name = str(current_time) + '.jpg'
            cv2.imwrite(os.path.join(raw_images_directory, file_name), image_opencv)

            for detection in tracker_results:
                # 'Date', 'Timestamp', 'ID', 'Filename',
                # 'TopLeftX', 'TopLeftY', 'BottomRightX', 'BottomRightY', 'Confidence'
                #print([datetime.date.strftime(datetime.datetime.now(),'%Y-%m-%d'),'2908-04-02 ' + datetime.date.strftime(datetime.datetime.now(), '%H:%M:%S'),detection[5],file_name,
                #                                               detection[0], detection[1], detection[2], detection[3],
                #                                               detection[4]]) 
                #print(raw_detections.shape)
                raw_detections.loc[raw_detections.shape[0]] = [datetime.date.strftime(datetime.datetime.now(),'%Y-%m-%d'),'2908-04-02 ' + datetime.date.strftime(datetime.datetime.now(), '%H-%M-%S'),detection[5],file_name,
                                                               int(detection[0][0]), int(detection[1][0]), int(detection[2][0]), int(detection[3][0]),
                                                               detection[4]]

        for dismissed_id in recently_dismissed_ids:
            #print('id: ' + str(dismissed_id))
            raw_indices_for_the_id = raw_detections[raw_detections['ID'] == dismissed_id].index
            #print('number of frames with an object: ' + str(len(raw_indices_for_the_id)))
            detections_of_interest = raw_detections.loc[raw_indices_for_the_id,:]
            #print('number of detections : ' + str(detections_of_interest.shape[0]))

            images_for_gif = [None] * detections_of_interest.shape[0]
            idx = 0
            for _, row in detections_of_interest.iterrows():
                image = imageio.imread(os.path.join(raw_images_directory, row['Filename']))
                cv2.rectangle(image, (row['TopLeftX'], row['TopLeftY']),
                              (row['BottomRightX'], row['TopLeftY'] + 20), (125, 125, 125), -1)
                cv2.rectangle(image, (row['TopLeftX'], row['TopLeftY']),
                              (row['BottomRightX'], row['BottomRightY']), (0,255,0), 2)
                cv2.putText(image, '%d: %.2f' % (row['ID'], row['Confidence']),
                            (row['TopLeftX'] + 5, row['TopLeftY'] + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                #print(str(idx))
                images_for_gif[idx] = image
                idx += 1
                # images_for_gif[idx] = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            gif_file_name = str(detections_of_interest['Date'].iloc[0]) + ' ' + str(detections_of_interest['Timestamp'].iloc[0]) + '.gif'
            imageio.mimsave(os.path.join(gifs_directory, gif_file_name), images_for_gif)

            start_time = datetime.datetime.strptime(detections_of_interest['Timestamp'].iloc[0], '%Y-%m-%d %H-%M-%S')
            end_time = datetime.datetime.strptime(detections_of_interest['Timestamp'].iloc[-1], '%Y-%m-%d %H-%M-%S')
            duration_in_seconds = (end_time - start_time).total_seconds()

            # writing results to a csv file with a header 'Day,Hour,Min,Date,Timestamp,ID,Duration,Filename'
            with open(detections_info_file, 'a') as output_file:
                starting_row = detections_of_interest.iloc[0,:]
                output_file.write(f"{starting_row['Date']},{starting_row['Timestamp']},{starting_row['ID']},"
                                  f"{duration_in_seconds},{gif_file_name}\n")
            raw_detections = raw_detections.drop(raw_indices_for_the_id)
            #print('number of raw detections after: ' + str(raw_detections.shape[0]))
        number_of_processed_images += 1
        if number_of_processed_images % 100 == 0:
            # elapsed_time = millis()
            # average_time_per_frame = elapsed_time / number_of_processed_images
            average_time_per_frame = sum(times_detection) / len(times_detection)
            print('Average time per processed frame (the whole pipeline) : ' + str(average_time_per_frame) + 'ms.')
            print('Elapsed time: ', elapsed_time )


if __name__ == '__main__':
    main()
