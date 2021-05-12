# TODO
# convert drawCenterMeasuringSquare to drawCenterMeasuringCircle
# create a constant.py - https://www.programiz.com/python-programming/variables-constants-literals

# libraries
# ----------------------------------------------------------------------------------------------------------------------------
import pyrealsense2 as rs
import numpy as np
import imutils
import cv2
import math


# constants
# ----------------------------------------------------------------------------------------------------------------------------
# when connected to USB 3.0
"""
cameraCaptureResolutionX = 1920
cameraCaptureResolutionY = 1080
cameraCaptureFps = 30
"""

# when connected to USB 2.1
cameraCaptureResolutionX = 1280
cameraCaptureResolutionY = 720
cameraCaptureFps = 15
windowWidth = 800

arucoType = cv2.aruco.DICT_4X4_1000
markerSideLength = 0.03
markerDiagonalLength = round(math.sqrt((markerSideLength ** 2) * 2), 4)
markerOrientationLength = 0.015

lineWidth = 2
circleWidth = -1
circleRadius = 4
borderCircleWidth = 2
borderCircleRadius = 5

blue = (255, 0, 0)
green = (0, 255, 0)
red = (0, 0, 255)

focusedTrackScreenMargin = 40
centerSquareSideLength = 15

measuringMarkerID = 0
corner1ID = 1
corner2ID = 2
corner3ID = 3
corner4ID = 4


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
def findArucoMarkers(image):
	arucoDictionary = cv2.aruco.Dictionary_get(arucoType)
	arucoParameters = cv2.aruco.DetectorParameters_create()
	(corners, ids, _) = cv2.aruco.detectMarkers(image, arucoDictionary, parameters=arucoParameters)
	rotationVector, translationVector, _ = cv2.aruco.estimatePoseSingleMarkers(corners, markerSideLength, cameraMatrix, cameraDistortionCoefficients)
	return corners, ids, rotationVector, translationVector


# variable manipulation
# ----------------------------------------------------------------------------------------------------------------------------
def getMarkerCoordinates(corners):
	(topLeft, topRight, bottomRight, bottomLeft) = corners
	topRight = (int(topRight[0]), int(topRight[1]))
	bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
	bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
	topLeft = (int(topLeft[0]), int(topLeft[1]))

	centerX = int((topLeft[0] + bottomRight[0]) / 2.0)
	centerY = int((topLeft[1] + bottomRight[1]) / 2.0)

	return topLeft, topRight, bottomRight, bottomLeft, centerX, centerY

def setTrackCorners(markerID, centerX, centerY):
	global corner1X, corner1Y, corner2X, corner2Y, corner3X, corner3Y, corner4X, corner4Y

	if markerID == corner1ID:
		corner1X = centerX
		corner1Y = centerY
	elif markerID == corner2ID:
		corner2X = centerX
		corner2Y = centerY
	elif markerID == corner3ID:
		corner3X = centerX
		corner3Y = centerY
	elif markerID == corner4ID:
		corner4X = centerX
		corner4Y = centerY

def getFocusedTrackCoordinates(maxX, maxY):
	minCornerX = min(corner1X, corner2X, corner3X, corner4X) - focusedTrackScreenMargin
	minCornerY = min(corner1Y, corner2Y, corner3Y, corner4Y) - focusedTrackScreenMargin
	maxCornerX = max(corner1X, corner2X, corner3X, corner4X) + focusedTrackScreenMargin
	maxCornerY = max(corner1Y, corner2Y, corner3Y, corner4Y) + focusedTrackScreenMargin

	if minCornerX < 0: minCornerX = 1
	if minCornerY < 0: minCornerY = 1
	if maxCornerX > maxX: maxCornerX = maxX
	if maxCornerY > maxY: maxCornerY = maxY

	return minCornerX, minCornerY, maxCornerX, maxCornerY

def getWindowCenterSquareCoordinates(image):
	generalXLow = (int)(((image.shape[1]-1) / 2) - centerSquareSideLength)
	generalYLow = (int)(((image.shape[0]-1) / 2) - centerSquareSideLength)
	generalXHigh = (int)(((image.shape[1]-1) / 2) + centerSquareSideLength)
	generalYHigh = (int)(((image.shape[0]-1) / 2) + centerSquareSideLength)

	return generalXLow, generalYLow, generalXHigh, generalYHigh

def checkMeasuringMarkerPosition(image, centerX, centerY):
	generalXLow, generalYLow, generalXHigh, generalYHigh = getWindowCenterSquareCoordinates(image)
	if centerX > generalXLow and centerX < generalXHigh and centerY > generalYLow and centerY < generalYHigh:
		return True

def distanceBetweenTwoPoints(p0, p1):
	return (int)(math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2))


# visual representation
# ----------------------------------------------------------------------------------------------------------------------------
def refreshWindows(image, focusedTrackImage):
	cv2.imshow('Gate setup', image)
	cv2.imshow('Focused track', focusedTrackImage)

	if cv2.waitKey(3) & 0xFF == ord('q'):
		return False
	return True

def drawMarker(image, markerID, topLeft, topRight, bottomRight, bottomLeft, centerX, centerY):
	cv2.line(image, topLeft, topRight, green, lineWidth)
	cv2.line(image, topRight, bottomRight, green, lineWidth)
	cv2.line(image, bottomRight, bottomLeft, green, lineWidth)
	cv2.line(image, bottomLeft, topLeft, green, lineWidth)

	if markerID == corner1ID or markerID == corner2ID or markerID == corner3ID or markerID == corner4ID:
		cv2.circle(image, (centerX, centerY), borderCircleRadius, red, borderCircleWidth)
	else:
		cv2.circle(image, (centerX, centerY), circleRadius, red, circleWidth)

def drawFoucusedTrackWindow(image, focusedTrackImage, ids, markerID, centerX, centerY):
	# not all track limits are found
	if corner1ID not in ids and corner2ID not in ids and corner3ID not in ids and corner4ID not in ids:
		return focusedTrackImage

	# get corners and focused track coordinates
	setTrackCorners(markerID, centerX, centerY)
	(minCornerX, minCornerY, maxCornerX, maxCornerY) = getFocusedTrackCoordinates(image.shape[1]-1, image.shape[0]-1)

	# visual representation of the boundaries
	drawTrackBoundaries(image, minCornerX, minCornerY, maxCornerX, maxCornerY)

	# alter focused track image dimensions
	if 0 not in {minCornerX, minCornerY, maxCornerX, maxCornerY}:
		focusedTrackImage = image[minCornerY+circleRadius:maxCornerY-circleRadius, minCornerX+circleRadius:maxCornerX-circleRadius]

	return focusedTrackImage

def drawTrackBoundaries(image, minCornerX, minCornerY, maxCornerX, maxCornerY):
	# lines between corners
	boundaries = np.array([[corner1X, corner1Y], [corner2X, corner2Y], [corner3X, corner3Y], [corner4X, corner4Y]], np.int32)
	boundaries = boundaries.reshape((-1, 1, 2))
	firstToSecondX = corner1X - corner2X
	firstToSecondY = corner1Y - corner2Y
	cv2.polylines(image, [boundaries] , True, green)

	# boundaries of the focused track window
	cv2.circle(image, (minCornerX, minCornerY), circleRadius, red, circleWidth)
	cv2.circle(image, (maxCornerX, maxCornerY), circleRadius, red, circleWidth)

def drawMarkerOrientations(image, rotationVector, translationVector):
	index = -1
	for x in rotationVector:
		index += 1
		rotVector = rotationVector[index]
		transVector = translationVector[index]
		cv2.aruco.drawAxis(image, cameraMatrix, cameraDistortionCoefficients, rotVector, transVector, markerOrientationLength)

def drawCenterMeasuringSquare(image):
	generalXLow, generalYLow, generalXHigh, generalYHigh = getWindowCenterSquareCoordinates(image)
	cv2.rectangle(image ,(generalXLow, generalYLow),(generalXHigh, generalYHigh), red, lineWidth)


# main program
# ----------------------------------------------------------------------------------------------------------------------------
def mainLoop(pipeline):
	global borderCircleRadius

	# local variables 
	calibrationMarkerDiagonalPixels = 0
	pixelToMeterRatio = 0

	looping = True
	measuringMarkerInsideLimits = False
	distanceSet = False

	focusedTrackImage = pipelineToImage(pipeline)

	# loop
	while looping:
		# get frames from camera and convert to image
		image = pipelineToImage(pipeline)

		# find ArUco markers on the image
		corners, ids, rotationVector, translationVector = findArucoMarkers(image)

		# drawing the limits in which the measuring marker must be to get recognized
		if not measuringMarkerInsideLimits:
			drawCenterMeasuringSquare(image)

		# no markers found
		if not len(corners):
			looping = refreshWindows(image, focusedTrackImage)
			continue

		ids = ids.flatten()

		# cycling through all markers
		for (markerCorner, markerID) in zip(corners, ids):
			# condition that distance isn't already calculated and set marker isn't the calibration marker
			if markerID != measuringMarkerID and not measuringMarkerInsideLimits:
				continue

			corners = markerCorner.reshape((4, 2))
			
			# getting coordinates of corners and centers of markers
			topLeft, topRight, bottomRight, bottomLeft, centerX, centerY = getMarkerCoordinates(corners)

			# drawing boundaries of a marker
			drawMarker(image, markerID, topLeft, topRight, bottomRight, bottomLeft, centerX, centerY)

			# checking the position of the measuring marker
			if not measuringMarkerInsideLimits:
				measuringMarkerInsideLimits = checkMeasuringMarkerPosition(image, centerX, centerY)
				if not measuringMarkerInsideLimits:
					break

			# setting starting values of distances
			if not distanceSet and markerID == measuringMarkerID:
				calibrationMarkerDiagonalPixels = distanceBetweenTwoPoints(topLeft, bottomRight)
				borderCircleRadius = (int)(calibrationMarkerDiagonalPixels / 2 + calibrationMarkerDiagonalPixels / 4)
				pixelToMeterRatio = calibrationMarkerDiagonalPixels / markerDiagonalLength
				distanceSet = True
			
			# finding track limits 
			focusedTrackImage = drawFoucusedTrackWindow(image, focusedTrackImage, ids, markerID, centerX, centerY)

		# draw marker orientations
		#drawMarkerOrientations(image, rotationVector, translationVector)

		# display windows
		looping = refreshWindows(image, focusedTrackImage)	

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

if __name__ == "__main__": 
	main()