import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    frame = cv2.bilateralFilter(frame, 9, 75, 75)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gr = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    bl = cv2.medianBlur(gr, 5)
    canny = cv2.Canny(bl, 10, 250)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    kernal = np.ones((5, 5), "uint8")
    closed = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel)

    blue_lower = np.array([94, 80, 2], np.uint8)
    blue_upper = np.array([120, 255, 255], np.uint8)
    blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)

    blue_mask = cv2.dilate(blue_mask, kernal)
    res_blue = cv2.bitwise_and(frame, frame,
                               mask=blue_mask)

    contours = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]

    for cont in contours:
        sm = cv2.arcLength(cont, True)
        apd = cv2.approxPolyDP(cont, 0.02 * sm, True)

        if len(apd) == 4:
            cv2.drawContours(frame, [apd], -1, (0, 255, 0), 4)

    cv2.imshow("Blue Square Detection", frame)

    if cv2.waitKey(1) & 0xff == 27:
        break

cap.release()
cv2.destroyAllWindows()