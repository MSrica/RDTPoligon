"""
Links
CV2 video - https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html
OpenCV - https://opencv-python-tutroals.readthedocs.io/en/latest/index.html
"""

# libraries
import numpy as np
import cv2

cameraPort = 1
camera = cv2.VideoCapture(cameraPort, cv2.CAP_DSHOW)

def main():
	while True:
		# Capture frame-by-frame
		ret, frame = camera.read()

		# Display the resulting frame
		cv2.imshow('image', frame)
		if cv2.waitKey(10) & 0xFF == ord('q'):
			break

if __name__ == "__main__":
	main()

# When everything done, release the camera
camera.release()
cv2.destroyAllWindows()
