image = cv2.imread('images/128491_01', -1)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

retval, dst = cv2.threshold(src, thresh, maxval, type)

cv2.namedWindow('Image', cv2.WINDOW_NORMAL)

cv2.resizeWinow('Image', 500, 400)

cv2.imshow('Image', image)
cv2.waitKey(0)
cv2.destroyAllWindows()