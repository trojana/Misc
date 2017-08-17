from net.build import TFNet
import cv2
import os

options = {"model": "C:\\Users\\H184146\\darknet\\cfg\\yolo.2.0.cfg", "load": "C:\\Users\\H184146\\darknet\\cfg\\yolo.2.0.weights", "threshold": 0.1}
output_file_name = 'YOLOv2_labels_0.1.csv'
directory = 'W:\\ObjectClassification\\CAMERA DATA'

tfnet = TFNet(options)

def traverse_dir(directory):
    files_in_directory = [x for x in os.listdir(directory) if os.path.join(directory, x) not in ['Z:\\OC_RESINET\\process\\ResiIndoor02-TB', 'Z:\\OC_RESINET\\process\\ResiIndoor03-YT',
                                                                        'Z:\\OC_RESINET\\process\\ResiIndoor04-JT', 'Z:\\OC_RESINET\\process\\ResiIndoor05-Pond5\\front_door_002',
                                                                        'Z:\\OC_RESINET\\process\\ResiIndoor05-Pond5\\front_door_005',
                                                                        'Z:\\OC_RESINET\\process\\ResiIndoor05-Pond5\\front_door_016',
                                                                        'Z:\\OC_RESINET\\process\\ResiIndoor05-Pond5\\indoor_003',
                                                                        'Z:\\OC_RESINET\\process\\ResiIndoor05-Pond5\\indoor_012',
                                                                        'Z:\\OC_RESINET\\process\\ResiIndoor05-Pond5\\indoor_016',
                                                                        'Z:\\OC_RESINET\\process\\ResiIndoor05-Pond5\\indoor_017',
                                                                        'Z:\\OC_RESINET\\process\\ResiIndoor05-Pond5\\indoor_020',
                                                                        'Z:\\OC_RESINET\\process\\ResiIndoor05-Pond5\\indoor_031',
                                                                        'Z:\\OC_RESINET\\process\\ResiIndoor05-Pond5\\indoor_033',
                                                                        'Z:\\OC_RESINET\\process\\ResiIndoor05-Pond5\\indoor_034',
                                                                        'Z:\\OC_RESINET\\process\\ResiIndoor05-Pond5\\indoor_037',
                                                                        'Z:\\OC_RESINET\\process\\ResiIndoor05-Pond5\\indoor_038',
                                                                        'Z:\\OC_RESINET\\process\\ResiIndoor05-Pond5\\indoor_045',
                                                                        'Z:\\OC_RESINET\\process\\ResiIndoor05-Pond5\\indoor_046',
                                                                        'Z:\\OC_RESINET\\process\\ResiIndoor05-Pond5\\indoor_050',
                                                                        'Z:\\OC_RESINET\\process\\ResiIndoor05-Pond5\\indoor_051',
                                                                        'Z:\\OC_RESINET\\process\\ResiIndoor05-Pond5\\indoor_052']]

    home_dir = os.getcwd()
    os.chdir(directory)
    print(directory)
    open(output_file_name, 'w').close()
    results_dir = os.path.join(directory, 'yolo_results_visual')
    if not os.path.exists(results_dir):
        os.mkdir(results_dir)

    for file_name in files_in_directory:
        if os.path.splitext(file_name)[1].lower() in ('.jpg', '.jpeg'):
            imgcv = cv2.imread(file_name)
            result = tfnet.return_predict(imgcv)
            for detection in result:
                if detection['label'] == 'person' or detection['label'] == 'dog' or detection['label'] == 'cat':
                    with open(output_file_name, 'a') as output_file:
                        output_file.write(file_name + ',' + str(detection['topleft']['x']) + ',' + str(detection['topleft']['y']) + ',' + str(detection['bottomright']['x']) + ',' + str(detection['bottomright']['y']) +',' +detection['label'] +',' + str(detection['confidence']) + ',0,0,0,0\n')
                    cv2.rectangle(imgcv, (detection['topleft']['x'], detection['topleft']['y']), (detection['bottomright']['x'], detection['bottomright']['y']), (0, 255, 0), 2)

                    cv2.rectangle(imgcv, (detection['topleft']['x'], detection['topleft']['y'] - 20), (detection['bottomright']['x'], detection['topleft']['y']), (125, 125, 125), -1)

                    cv2.putText(imgcv, detection['label'] + ' : %.2f' % detection['confidence'], (detection['topleft']['x'] + 5, detection['topleft']['y'] - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

                cv2.imwrite(os.path.join(results_dir, file_name), imgcv)

        elif os.path.isdir(file_name) and file_name[0] != '_' and file_name[:8] != 'synopses':
            traverse_dir(os.path.join(directory, file_name))

    os.chdir(home_dir)


traverse_dir(directory)
