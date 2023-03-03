import cv2

face_cascade = cv2.CascadeClassifier("C:\\Users\\Acer\\Downloads\\opencv-master\\data\\haarcascades\\haarcascade_frontalface_default.xml")
eye_cascade = cv2.CascadeClassifier("C:\\Users\\Acer\\Downloads\\opencv-master\\data\\haarcascades\\haarcascade_eye.xml")

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(img_gray, 1.1, 19)
    for (x,y,w,h) in faces:
        cv2.rectangle(img, (x,y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(img, "Person", (x, y - 5),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, 2)
        img_gray_face = img_gray[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(img_gray_face, 1.1, 19)
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(img, (x+ex, y+ey), (x+ex + ew, y+ey + eh), (255, 0, 0), 2)
        imgRoi = img[y:y + h, x:x + w]
        cv2.imshow("test 2", imgRoi)
        cv2.imshow("test", img)
    if cv2.waitKey(1) & 0xff == 27: #остановка при нажатии ESC
        break

cap.release()
cv2.destroyAllWindows()