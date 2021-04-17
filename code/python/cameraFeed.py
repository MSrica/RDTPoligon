# libraries
# ----------------------------------------------------------------------------------------------------------------------------
import pyrealsense2 as rs
import numpy as np
import imutils
import cv2

# constants
# ----------------------------------------------------------------------------------------------------------------------------
arucoType = cv2.aruco.DICT_4X4_1000

# camera
# ----------------------------------------------------------------------------------------------------------------------------
def pipelineInitilazation():
	pipeline = rs.pipeline()
	config = rs.config()
	config.enable_stream(rs.stream.color, 1920, 1080, rs.format.bgr8, 30)
	pipeline.start(config)

	return pipeline
def pipelineToImage(pipeline):
	frames = pipeline.wait_for_frames()
	colorFrame = frames.get_color_frame()
	colorImage = np.asanyarray(colorFrame.get_data())
	colorImage = imutils.resize(colorImage, width=600)
	
	return colorImage

# aruco
# ----------------------------------------------------------------------------------------------------------------------------
def arucoFind(image):
	arucoDictionary = cv2.aruco.Dictionary_get(arucoType)
	arucoParameters = cv2.aruco.DetectorParameters_create()
	(corners, ids, _) = cv2.aruco.detectMarkers(image, arucoDictionary, parameters=arucoParameters)
	return corners, ids

# variable manipulation
# ----------------------------------------------------------------------------------------------------------------------------
def getCoordinates(corners):
	(topLeft, topRight, bottomRight, bottomLeft) = corners
	topRight = (int(topRight[0]), int(topRight[1]))
	bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
	bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
	topLeft = (int(topLeft[0]), int(topLeft[1]))

	centerX = int((topLeft[0] + bottomRight[0]) / 2.0)
	centerY = int((topLeft[1] + bottomRight[1]) / 2.0)

	return topLeft, topRight, bottomRight, bottomLeft, centerX, centerY

# visual representation
# ----------------------------------------------------------------------------------------------------------------------------
def drawMarker(image, topLeft, topRight, bottomRight, bottomLeft, centerX, centerY):
	cv2.line(image, topLeft, topRight, (0, 255, 0), 2)
	cv2.line(image, topRight, bottomRight, (0, 255, 0), 2)
	cv2.line(image, bottomRight, bottomLeft, (0, 255, 0), 2)
	cv2.line(image, bottomLeft, topLeft, (0, 255, 0), 2)
	cv2.circle(image, (centerX, centerY), 4, (0, 0, 255), -1)

# main program
# ----------------------------------------------------------------------------------------------------------------------------
def mainLoop(pipeline):
	corner1x = corner1y = corner2x = corner2y = 0

	while True:
		# get frames from camera and convert to image
		image = pipelineToImage(pipeline)

		# find ArUco markers on the image
		corners, ids = arucoFind(image)

		# one or more markers found
		if len(corners):
			ids = ids.flatten()
			
			# cycling through all markers
			for (markerCorner, markerID) in zip(corners, ids):
				corners = markerCorner.reshape((4, 2))
				# getting coordinates of corners and centers of markers
				topLeft, topRight, bottomRight, bottomLeft, centerX, centerY = getCoordinates(corners)

				# drawing boundaries a marker
				drawMarker(image, topLeft, topRight, bottomRight, bottomLeft, centerX, centerY)

				# track limits are defined
				if 0 in ids and 1 in ids:
					if markerID == 0:
						corner1x = centerX
						corner1y = centerY
					if markerID == 1:
						corner2x = centerX
						corner2y = centerY

					# drawing limits of track
					cv2.rectangle(image, (corner1x, corner1y), (corner2x, corner2y), (0,255,0), 3)

					# printing markers inside boudaries
					if(((centerX > corner1x and centerX < corner2x) or (centerX < corner1x and centerX > corner2x)) and ((centerY > corner1y and centerY < corner2y) or (centerY < corner1y and centerY > corner2y))):
						noBoundariesIds = list(ids)
						noBoundariesIds.remove(0)
						noBoundariesIds.remove(1)
						print(noBoundariesIds, "is inside the boudaries")

		cv2.imshow('Gate setup', image)
		if cv2.waitKey(5) & 0xFF == ord('q'):
			break
def main():
	# D435i camera setup
	pipeline = pipelineInitilazation()

	# main loop
	mainLoop(pipeline)

	# stop receiving camera data
	pipeline.stop()
if __name__ == "__main__":
	main()