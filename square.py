import cv2

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    frame = cv2.bilateralFilter(frame, 9, 75, 75)
    gr = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    bl = cv2.medianBlur(gr, 5)
    canny = cv2.Canny(bl, 10, 250)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    closed = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel)
    contours = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    for cont in contours:
        sm = cv2.arcLength(cont, True)
        apd = cv2.approxPolyDP(cont, 0.02 * sm, True)

        if len(apd) == 4:
            cv2.drawContours(frame, [apd], -1, (0, 255, 0), 4)

    cv2.imshow("Square Detection", frame)

    if cv2.waitKey(1) & 0xff == 27:
        break

cap.release()
cv2.destroyAllWindows()