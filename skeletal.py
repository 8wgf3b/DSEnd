import cv2

def main():
    cv2.namedWindow('Basic')
    cap = cv2.VideoCapture(0)

    if cap.isOpened():
        ret, frame = cap.read()
    else:
        ret = False

    while ret:
        ret, frame = cap.read()
        cv2.imshow('Basic', frame)
        if cv2.waitKey(1) == 27:
            break

    cv2.destroyAllWindows()    
    cap.release()

if __name__ == "__main__":
    main()
