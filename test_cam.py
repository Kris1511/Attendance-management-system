# import cv2

# cap = cv2.VideoCapture(0)

# while True:
#     ret, frame = cap.read()
    
#     if not ret:
#         print("Camera not working")
#         break

#     cv2.imshow("Test Camera", frame)

#     if cv2.waitKey(1) == 27:
#         break

# cap.release()
# cv2.destroyAllWindows()

import cv2

for i in range(5):
    cap = cv2.VideoCapture(i)
    ret, frame = cap.read()

    if ret:
        print(f"Camera working at index: {i}")
        cv2.imshow(f"Camera {i}", frame)
        cv2.waitKey(2000)
        cv2.destroyAllWindows()
    else:
        print(f"Camera NOT working at index: {i}")

    cap.release()