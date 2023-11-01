# UDP running on a thread
import threading
import socket

# Creating the socket

data = 'Nothing received'
UDP_ADDR = '0.0.0.0'
UDP_PORT = 31337
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_ADDR, UDP_PORT))

def rec_UDP():
    while True:
        data, addr = sock.recvfrom(4096)
        print("Echoing " + data.decode('utf-8') + " back to " + str(addr))

# The thread that ables the listen for UDP packets is loaded
listen_UDP = threading.Thread(target=rec_UDP)
listen_UDP.start()

# Model and OpenCV starts

import cv2
import argparse
from ultralytics import YOLO
import supervision as sv
import numpy as np

ZONE_POLYGON = np.array([
    [0, 0],
    [0.5, 0],
    [0.5, 1],
    [0, 1]
])

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Live")
    parser.add_argument(
        "--webcam-resolution", 
        default=[1280, 720], 
        nargs=2, 
        type=int
    )
    parser.add_argument(
        "--model",
        default=["yolov8m.pt"],
        nargs=1
    )
    parser.add_argument(
        "--rtmp",
        default=[0],
        nargs=1
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    frame_width, frame_height = args.webcam_resolution
    rtmpSource = args.rtmp[0]
    modelName = args.model[0]

    print("RTMP Arg", rtmpSource)

    cap = cv2.VideoCapture(rtmpSource)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
    
    model = YOLO(modelName)

    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=2,
        text_scale=1
    )

    zone_polygon = (ZONE_POLYGON * np.array(args.webcam_resolution)).astype(int)
    zone = sv.PolygonZone(polygon=zone_polygon, frame_resolution_wh=tuple(args.webcam_resolution))
    zone_annotator = sv.PolygonZoneAnnotator(
        zone=zone, 
        color=sv.Color.red(),
        thickness=2,
        text_thickness=4,
        text_scale=2
    )

    while True:
        ret, frame = cap.read()

        # result = model(frame, agnostic_nms=True)[0]
        # detections = sv.Detections.from_yolov8(result)
        # labels = [
        #     f"{model.model.names[class_id]} {confidence:0.2f}"
        #     for _, confidence, class_id, _
        #     in detections
        # ]
        # frame = box_annotator.annotate(
        #     scene=frame, 
        #     detections=detections, 
        #     labels=labels
        # )

        # zone.trigger(detections=detections)
        # frame = zone_annotator.annotate(scene=frame)      
        
        # print(result)
        cv2.imshow("Real Time Pothole Detection on Stream", frame)

        if (cv2.waitKey(30) == 27):
            break


if __name__ == "__main__":
    main()