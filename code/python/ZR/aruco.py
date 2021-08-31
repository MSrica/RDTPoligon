import cv2

import constants

# nalazenje markera na slici
def findArucoMarkers(image, cameraMatrix, cameraDistortionCoefficients):
	arucoDictionary = cv2.aruco.Dictionary_get(constants.arucoType)
	arucoParameters = cv2.aruco.DetectorParameters_create()
	(markerCorners, ids, _) = cv2.aruco.detectMarkers(image, arucoDictionary, parameters=arucoParameters)
	rotationVectors, translationVectors, _ = cv2.aruco.estimatePoseSingleMarkers(markerCorners, constants.markerSideLength, cameraMatrix, cameraDistortionCoefficients)
	return markerCorners, ids, rotationVectors, translationVectors