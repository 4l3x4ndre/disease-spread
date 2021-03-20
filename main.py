import cv2
from matplotlib import pyplot as plt
from mtcnn.mtcnn import MTCNN
import face_recognition as fr
import numpy as np
import sys
import os
import re

from register import Session


def image_files_in_folder(folder):
    # Alexandre: getting every image (type jpg or jpeg or png)
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]


def scan_known_people(known_people_folder, detector):
    known_names = []
    known_face_encodings = []
    known_images = []

    for file in image_files_in_folder(known_people_folder):
        basename = os.path.splitext(os.path.basename(file))[0]
        img = fr.load_image_file(file)
        result = detector.detect_faces(img)
        list = []
        for i in range(len(result)):
            bounding_box = result[i]['box']
            list.append((bounding_box[1], bounding_box[0] + bounding_box[2], bounding_box[1] + bounding_box[3], bounding_box[0]))
        encodings = fr.face_encodings(img, list)

        if len(encodings) > 1:
            print("WARNING: More than one face found in {}. Only considering the first face.".format(file))

        if len(encodings) == 0:
            print("WARNING: No faces found in {}. Ignoring file.".format(file))
        else:
            known_names.append(basename)
            known_face_encodings.append(encodings[0])
            known_images.append(img)

    return known_names, known_face_encodings, known_images


# Alexandre: Face detector
detector = MTCNN()

# Alexandre: scan people according to the faces stored in the "faces" folder
known_names, known_faces_encs, known_images = scan_known_people("faces", detector)

# Alexandre: starting webcam & error handling
video_capture = cv2.VideoCapture(0)
if not video_capture.isOpened():
    raise Exception("Could not open video device")

# Alexandre: Current people seen
session = Session()

# ---------------------
# ------------------------------

def main():
    while True:
        try:
            indx = 0

            # Alexandre: Getting each frame of the webcam
            ret, frameo = video_capture.read()
            frame = cv2.flip(frameo, 1)
            frameRGB = frame[:, :, ::-1]

            # Alexandre: Getting detected faces from the current frame
            result = detector.detect_faces(frame)

            list = []

            for i in range(len(result)):
                bounding_box = result[i]['box']
                list.append(
                    (bounding_box[1],
                     bounding_box[0] + bounding_box[2], bounding_box[1] + bounding_box[3],
                     bounding_box[0])
                )

            faces_enc = fr.face_encodings(frameRGB, list)

            nbdetectedface = len(list)

            for (top, right, bottom, left), face_enc, res in zip(list, faces_enc, result):
                matches = fr.compare_faces(known_faces_encs, face_enc)

                # Alexandre: By default, the face is unknown
                name = 'Unknown'
                faces_distances = fr.face_distance(known_faces_encs, face_enc)
                best_match_index = np.argmin(faces_distances)

                # Alexandre: if we have a match, then we know this face
                if matches[best_match_index]:
                    name = known_names[best_match_index]
                    if name not in session:
                        session.new_user_joined(name)

                nbknownImage = len(known_names)
                indx= indx + 1

                plt.subplot(nbdetectedface, nbknownImage + 1, indx)
                plt.imshow(frame[top-1:bottom+1, left-1:right+1, ::-1])
                # plt.axis('off');
                # plt.title('Visage detecté')

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

                # Alexandre: followings are visual indicator of keypoints detected in a face
                # keypoints = res['keypoints']
                # cv2.circle(frame,(keypoints['left_eye']), 2, (0,155,255), 2)
                # cv2.circle(frame,(keypoints['right_eye']), 2, (0,155,255), 2)
                # cv2.circle(frame,(keypoints['nose']), 2, (0,155,255), 2)
                # cv2.circle(frame,(keypoints['mouth_left']), 2, (0,155,255), 2)
                # cv2.circle(frame,(keypoints['mouth_right']), 2, (0,155,255), 2)

                index = sorted(range(nbknownImage), key=lambda k: faces_distances[k])

                for i in range(nbknownImage):
                    indx = indx + 1
                    # plt.subplot(nbdetectedface, nbknownImage + 1, indx)
                    plt.imshow(known_images[index[i]])
                    # plt.axis('off')
                    plt.title(known_names[index[i]] + "  " + '{:5.3f}'.format(faces_distances[index[i]]))

            cv2.imshow('Video', frame)
            k = cv2.waitKey(1);
            if k & 0xFF == ord('q'):
                break
            elif k & 0xFF == ord('p'):
                plt.show()
                while cv2.waitKey(1) & 0xFF != ord('c'):
                    pass

        except:
            pass

    video_capture.release()
    cv2.destroyAllWindows()
