# libraries
# ----------------------------------------------------------------------------------------------------------------------------
import pyrealsense2 as rs
import numpy as np
import imutils
import cv2


# constants
# ----------------------------------------------------------------------------------------------------------------------------
cameraCaptureResolutionX = 1920
cameraCaptureResolutionY = 1080
cameraCaptureFps = 30
windowWidth = 700

arucoType = cv2.aruco.DICT_4X4_1000
markerLength = 0.03
markerOrientationLength = 0.2

lineWidth = 2
circleWidth = -1
circleRadius = 4
green = (0, 255, 0)
red = (0, 0, 255)

croppedScreenMargin = 40

corner1ID = 0
corner2ID = 1
corner3ID = 2
corner4ID = 3


# global variables
# ----------------------------------------------------------------------------------------------------------------------------
corner1X = corner1Y = corner2X = corner2Y = corner3X = corner3Y = corner4X = corner4Y = 0

cameraMatrix = []
cameraDistortionCoefficients = []


# camera
# ----------------------------------------------------------------------------------------------------------------------------
def pipelineInitilazation():
	pipeline = rs.pipeline()
	config = rs.config()
	config.enable_stream(rs.stream.color, cameraCaptureResolutionX, cameraCaptureResolutionY, rs.format.bgr8, cameraCaptureFps)
	pipeline.start(config)

	return pipeline

def pipelineCalibration(pipeline):
	activeProfile = pipeline.get_active_profile()
	colorProfile = rs.video_stream_profile(activeProfile.get_stream(rs.stream.color))
	colorIntrinsics = colorProfile.get_intrinsics()
	cameraMatrix = [[colorIntrinsics.fx, 0, colorIntrinsics.ppx], [0, colorIntrinsics.fy, colorIntrinsics.ppy], [0, 0, 1]]
	return np.float32(cameraMatrix), np.float32(colorIntrinsics.coeffs)

def pipelineToImage(pipeline):
	frames = pipeline.wait_for_frames()
	colorFrame = frames.get_color_frame()
	colorImage = np.asanyarray(colorFrame.get_data())
	colorImage = imutils.resize(colorImage, width=windowWidth)
	
	return colorImage


# aruco
# ----------------------------------------------------------------------------------------------------------------------------
def arucoFind(image):
	arucoDictionary = cv2.aruco.Dictionary_get(arucoType)
	arucoParameters = cv2.aruco.DetectorParameters_create()
	(corners, ids, _) = cv2.aruco.detectMarkers(image, arucoDictionary, parameters=arucoParameters)
	rotationVector, translationVector, _ = cv2.aruco.estimatePoseSingleMarkers(corners, markerLength, cameraMatrix, cameraDistortionCoefficients)
	return corners, ids, rotationVector, translationVector


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

def getCorners(markerID, centerX, centerY):
	global corner1X, corner1Y, corner2X, corner2Y, corner3X, corner3Y, corner4X, corner4Y

	if markerID == corner1ID:
		corner1X = centerX
		corner1Y = centerY
	if markerID == corner2ID:
		corner2X = centerX
		corner2Y = centerY
	if markerID == corner3ID:
		corner3X = centerX
		corner3Y = centerY
	if markerID == corner4ID:
		corner4X = centerX
		corner4Y = centerY

def getCroppedCoordinates(maxX, maxY):
	minCornerX = min(corner1X, corner2X, corner3X, corner4X) - croppedScreenMargin
	minCornerY = min(corner1Y, corner2Y, corner3Y, corner4Y) - croppedScreenMargin
	maxCornerX = max(corner1X, corner2X, corner3X, corner4X) + croppedScreenMargin
	maxCornerY = max(corner1Y, corner2Y, corner3Y, corner4Y) + croppedScreenMargin

	if minCornerX < 0: minCornerX = 1
	if minCornerY < 0: minCornerY = 1
	if maxCornerX > maxX: maxCornerX = maxX
	if maxCornerY > maxY: maxCornerY = maxY

	return minCornerX, minCornerY, maxCornerX, maxCornerY


# visual representation
# ----------------------------------------------------------------------------------------------------------------------------
def drawMarker(image, topLeft, topRight, bottomRight, bottomLeft, centerX, centerY):
	cv2.line(image, topLeft, topRight, green, lineWidth)
	cv2.line(image, topRight, bottomRight, green, lineWidth)
	cv2.line(image, bottomRight, bottomLeft, green, lineWidth)
	cv2.line(image, bottomLeft, topLeft, green, lineWidth)
	cv2.circle(image, (centerX, centerY), circleRadius, red, circleWidth)

def drawBoundaries(image, minCornerX, minCornerY, maxCornerX, maxCornerY):
	# lines between corners
	boundaries = np.array([[corner1X, corner1Y], [corner2X, corner2Y], [corner3X, corner3Y], [corner4X, corner4Y]], np.int32)
	boundaries = boundaries.reshape((-1, 1, 2))
	cv2.polylines(image, [boundaries] , True, green)

	# boundaries of the cropped screen
	cv2.circle(image, (minCornerX, minCornerY), circleRadius, red, circleWidth)
	cv2.circle(image, (maxCornerX, maxCornerY), circleRadius, red, circleWidth)

def drawMarkerOrientations(image, rotationVector, translationVector):
	index = 0
	for x in rotationVector:
		rvec = rotationVector[index]
		tvec = translationVector[index]
		index += 1
		cv2.aruco.drawAxis(image, cameraMatrix, cameraDistortionCoefficients, rvec, tvec, markerOrientationLength)


# main program
# ----------------------------------------------------------------------------------------------------------------------------
def mainLoop(pipeline):
	cropped = pipelineToImage(pipeline)

	while True:
		# get frames from camera and convert to image
		image = pipelineToImage(pipeline)

		# find ArUco markers on the image
		corners, ids, rotationVector, translationVector = arucoFind(image)

		# one or more markers found
		if len(corners):
			ids = ids.flatten()
			
			# cycling through all markers
			for (markerCorner, markerID) in zip(corners, ids):
				corners = markerCorner.reshape((4, 2))
				# getting coordinates of corners and centers of markers
				topLeft, topRight, bottomRight, bottomLeft, centerX, centerY = getCoordinates(corners)

				# drawing boundaries of a marker
				drawMarker(image, topLeft, topRight, bottomRight, bottomLeft, centerX, centerY)

				# track limits are found
				if corner1ID in ids and corner2ID in ids and corner3ID in ids and corner4ID in ids:
					# get corner and cropped coordinates
					getCorners(markerID, centerX, centerY)
					(minCornerX, minCornerY, maxCornerX, maxCornerY) = getCroppedCoordinates(image.shape[1]-1, image.shape[0]-1)

					# visual representation of the boundaries
					drawBoundaries(image, minCornerX, minCornerY, maxCornerX, maxCornerY)

					if 0 not in {minCornerX, minCornerY, maxCornerX, maxCornerY}:
						cropped = image[minCornerY+circleRadius:maxCornerY-circleRadius, minCornerX+circleRadius:maxCornerX-circleRadius]

			#drawMarkerOrientations(image, rotationVector, translationVector)	

		cv2.imshow('Gate setup', image)
		cv2.imshow('Boundaries', cropped)
		if cv2.waitKey(5) & 0xFF == ord('q'):
			break

def main():
	# D435i camera setup and calibration
	global cameraMatrix
	global cameraDistortionCoefficients
	pipeline = pipelineInitilazation()
	cameraMatrix, cameraDistortionCoefficients = pipelineCalibration(pipeline)

	# main loop
	mainLoop(pipeline)

	# stop receiving camera data
	pipeline.stop()

if __name__ == "__main__": main()