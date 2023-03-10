import cv2
from cv_bridge import CvBridge
import rospy
import math
import pyzbar
import clover

qr = ""
color = "undefined"

def image_callback(data):
    global qr, color
    cv_image = bridge.imgmsg_to_cv2(data, "bgr8")
    img_hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2_HSV)[119:120, 159:160]
    print(img_hsv[119][159])

    red_low1 = (0, 50, 50)
    red_high1 = (15, 255, 255)

    red_low2 = (165, 50, 50)
    red_high2 = (180, 255, 255)

    yellow_low = (16, 50, 50)
    yellow_high = (45, 255, 255)

    red_thresh1 = cv2.inRange(img_hsv, red_low1, red_high1)
    red_thresh2 = cv2.inRange(img_hsv, red_low2, red_high2)
    red_thresh = cv2.bitwise_or(red_thresh1, red_thresh2)
    yellow_thresh = cv2.inRange(img_hsv, yellow_low, yellow_high)

    if red_thresh[0][0] == 255:
        color = "red"
    elif yellow_thresh[0][0] == 255:
        color = "yellow"
    else:
        color = "undefined"

    barcodes = pyzbar.decode(cv_image)
    for barcode in barcodes:
        qr = barcode.data.encode("utf-8")

def navigate_wait (x = 0, y = 0, z = 1.5, yaw = 0, speed = 1, frame_id = "aruco_map", auto_arm = False, tolerance = 0.2):
    navigate(x=x, y=y, z=z, yaw=yaw, speed=speed, frame_id=frame_id)

    while not rospy.is_shutdown():
        telem = get_telemetry(frame_id = "navigate_target")
        if math.sqrt(telem.x ** 2 + telem.y ** 2 + telem.z ** 2) < tolerance:
            break
        rospy.sleep(0.2)

image_sub = rospy.Subscriber("main_camera/image_raw_throttled", Image, image_callback, queue_size = 1)

navigate_wait(frame_id="body", auto_arm=True)
navigate_wait(1, 0, 1.5)
navigate_wait(1, 0, 0.8)

while not rospy.is_shutdown() and qr == "":
    rospy.sleep(0.2)

print(qr)
qr2 = qr.split()

final_color = qr2[0]
path = map(float, qr2[1:])
landing_point = [0, 0]

for i in range(0, len(path), 2):
    navigate_wait(path[i], path[i+1])
    rospy.sleep(2)
    print(color)
    if color[0] == final_color:
        landing_point = [path[i], path[i+1]]

navigate_wait(landing_point)
land()