import cv2 as cv

cam = cv.VideoCapture(0)
if cam.isOpened():
	print('Camera is open')
else:
	raise RuntimeError('Camera is off')

def read_frame():
	ret, frame = cam.read()
	return frame if ret else None

#frame = read_frame()
#cv.imwrite('test.png', frame)
