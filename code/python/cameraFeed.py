"""
Links
CV2 video - https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html
OpenCV - https://opencv-python-tutroals.readthedocs.io/en/latest/index.html
Intel RealSense - https://dev.intelrealsense.com/docs
"""

# libraries
import pyrealsense2 as rs
import numpy as np
import imutils
import cv2
import math

hsvLower = [0]
hsvUpper = [0]
contours = [0]

arucoType = cv2.aruco.DICT_4X4_1000

corner1x = corner1y = corner2x = corner2y = numberOfCorners = 0

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 1920, 1080, rs.format.bgr8, 30)
pipeline.start(config)

def main():
	while True:
		frames = pipeline.wait_for_frames()
		colorFrame = frames.get_color_frame()
		colorImage = np.asanyarray(colorFrame.get_data())
		colorImage = imutils.resize(colorImage, width=600)

		arucoDictionary = cv2.aruco.Dictionary_get(arucoType)
		arucoParameters = cv2.aruco.DetectorParameters_create()
		(corners, ids, rejected) = cv2.aruco.detectMarkers(colorImage, arucoDictionary, parameters=arucoParameters)

		if len(corners) > 0:
			ids = ids.flatten()
			numberOfCorners = 0
			for (markerCorner, markerID) in zip(corners, ids):
				if markerID == 0 or markerID == 1: numberOfCorners += 1

				corners = markerCorner.reshape((4, 2))

				(topLeft, topRight, bottomRight, bottomLeft) = corners
				topRight = (int(topRight[0]), int(topRight[1]))
				bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
				bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
				topLeft = (int(topLeft[0]), int(topLeft[1]))

				cv2.line(colorImage, topLeft, topRight, (0, 255, 0), 2)
				cv2.line(colorImage, topRight, bottomRight, (0, 255, 0), 2)
				cv2.line(colorImage, bottomRight, bottomLeft, (0, 255, 0), 2)
				cv2.line(colorImage, bottomLeft, topLeft, (0, 255, 0), 2)

				centerX = int((topLeft[0] + bottomRight[0]) / 2.0)
				centerY = int((topLeft[1] + bottomRight[1]) / 2.0)
				if markerID == 0:
					corner1x = centerX
					corner1y = centerY
				if markerID == 1:
					corner2x = centerX
					corner2y = centerY
				cv2.circle(colorImage, (centerX, centerY), 4, (0, 0, 255), -2)

			if numberOfCorners == 2: cv2.rectangle(colorImage, (corner1x, corner1y), (corner2x, corner2y), (0,255,0), 3)

		cv2.imshow('Gate setup', colorImage)
		if cv2.waitKey(5) & 0xFF == ord('q'):
			break

	pipeline.stop()

if __name__ == "__main__":
	main()