# TODO

# pretvoriti konstante u izmjenjive varijable (sirine linija itd.)
# constants to json

# export functions to other files
# translate and refactor to english
# GUI for some constants


# LIBRARIES
# ----------------------------------------------------------------------------------------------------------------------------
# external
import numpy as np
import cv2
import math
import json
import os

# files
import constants
import camera
import aruco

# ----------------------------------------------------------------------------------------------------------------------------
# GLOBAL VARIABLES
# ----------------------------------------------------------------------------------------------------------------------------
#				 X, Y
trackCorners = [[0, 0],	# ID0, measuring
				[0, 0],	# ID1
				[0, 0],	# ID2
				[0, 0],	# calculated3
				[0, 0], # calculated4
				[0, 0]]	# calculated5 - point on the 0-1 line
#		  X, Y,IN,D1,D2 
gates = [[0, 0, 0, 0, 0],	# ID3
		 [0, 0, 0, 0, 0],	# ID4
		 [0, 0, 0, 0, 0]]	# ID5

loadedTrackCorners = [[0, 0],	# pt0
					  [0, 0],	# pt1
					  [0, 0],	# pt2
					  [0, 0]]	# pt3

loadedGates = [[0, 0, 0, 0, 0],	# ID3
			   [0, 0, 0, 0, 0],	# ID4
			   [0, 0, 0, 0, 0]]	# ID5

centimeterToPixelRatio = 0
numberOfGates = 0
lockedBoundaries = False

# ----------------------------------------------------------------------------------------------------------------------------
# FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------------
# calculations

def getMarkerCoordinates(aCorner):
	(topLeft, topRight, bottomRight, bottomLeft) = aCorner
	topRight = (int(topRight[0]), int(topRight[1]))
	bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
	bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
	topLeft = (int(topLeft[0]), int(topLeft[1]))

	centerX = int((topLeft[0] + bottomRight[0]) / 2.0)
	centerY = int((topLeft[1] + bottomRight[1]) / 2.0)

	return topLeft, topRight, bottomRight, bottomLeft, centerX, centerY

def setTrackMarkers(markerID, centerX, centerY):
	global trackCorners, gates, numberOfGates

	if markerID == constants.corner1ID:
		trackCorners[0][0] = centerX
		trackCorners[0][1] = centerY
	elif markerID == constants.corner2ID:
		trackCorners[1][0] = centerX
		trackCorners[1][1] = centerY
	elif markerID == constants.corner3ID:
		trackCorners[2][0] = centerX
		trackCorners[2][1] = centerY

	elif markerID == constants.gate1ID:
		gates[0][0] = centerX
		gates[0][1] = centerY
	elif markerID == constants.gate2ID:
		gates[1][0] = centerX
		gates[1][1] = centerY
	elif markerID == constants.gate3ID:
		gates[2][0] = centerX
		gates[2][1] = centerY

def getFocusedTrackCoordinates(maxX, maxY):
	minCornerX = min(trackCorners[0][0], trackCorners[1][0], trackCorners[2][0], trackCorners[3][0], trackCorners[4][0]) - constants.focusedTrackScreenMargin
	minCornerY = min(trackCorners[0][1], trackCorners[1][1], trackCorners[2][1], trackCorners[3][1], trackCorners[4][1]) - constants.focusedTrackScreenMargin
	maxCornerX = max(trackCorners[0][0], trackCorners[1][0], trackCorners[2][0], trackCorners[3][0], trackCorners[4][0]) + constants.focusedTrackScreenMargin
	maxCornerY = max(trackCorners[0][1], trackCorners[1][1], trackCorners[2][1], trackCorners[3][1], trackCorners[4][1]) + constants.focusedTrackScreenMargin

	if minCornerX < 0: minCornerX = 1
	if minCornerY < 0: minCornerY = 1
	if maxCornerX > maxX: maxCornerX = maxX
	if maxCornerY > maxY: maxCornerY = maxY

	return minCornerX, minCornerY, maxCornerX, maxCornerY

# TODO split up
def setImaginaryBoundaries():
	global trackCorners, numberOfGates

	# udaljenost izmedu linije i tocke 3
	realMarker1 = np.array([trackCorners[0][0], trackCorners[0][1]])
	realMarker2 = np.array([trackCorners[1][0], trackCorners[1][1]])
	realMarker3 = np.array([trackCorners[2][0], trackCorners[2][1]])
	corner3DistanceToLine = np.abs(np.cross(realMarker2 - realMarker1, realMarker1 - realMarker3)) / np.linalg.norm(realMarker2 - realMarker1)

	# vektor izmedu tocaka
	lineVector = list((trackCorners[1][0] - trackCorners[0][0], trackCorners[1][1] - trackCorners[0][1]))

	# vektor izmedu c3 i c2
	dotVector = (trackCorners[2][0] - trackCorners[1][0], trackCorners[2][1] - trackCorners[1][1])
	
	# umnozak vektora za izracun orijentacije pravokutnika
	crossProduct = lineVector[0]*dotVector[1] - lineVector[1]*dotVector[0]
	rectangleOrientation = -1 if crossProduct < 0 else 1

	# normalizacija vektora
	lineLength = math.sqrt(lineVector[0]*lineVector[0] + lineVector[1]*lineVector[1])
	lineVector[0] = lineVector[0] / lineLength
	lineVector[1] = lineVector[1] / lineLength

	# rotacija vektora za 90 stupnjeva
	rotatingTemp = lineVector[0]
	lineVector[0] = -lineVector[1]
	lineVector[1] = rotatingTemp

	# tocka na liniji okomita na corner3
	trackCorners[5][0] = (int)(trackCorners[2][0] + lineVector[0] * corner3DistanceToLine)
	trackCorners[5][1] = (int)(trackCorners[2][1] + lineVector[1] * corner3DistanceToLine)

	trackCorners[3][0] = (int)(trackCorners[1][0] + rectangleOrientation * lineVector[0] * corner3DistanceToLine)
	trackCorners[3][1] = (int)(trackCorners[1][1] + rectangleOrientation * lineVector[1] * corner3DistanceToLine)

	trackCorners[4][0] = (int)(trackCorners[0][0] + rectangleOrientation * lineVector[0] * corner3DistanceToLine)
	trackCorners[4][1] = (int)(trackCorners[0][1] + rectangleOrientation * lineVector[1] * corner3DistanceToLine)

	setNumberOfGates(rectangleOrientation)

# TODO make pretty
def setNumberOfGates(rectangleOrientation):
	global numberOfGates

	for index in range(constants.maxGateNumber):
		# 2-1
		crossProduct1 = round((trackCorners[0][0] - trackCorners[1][0])*(gates[index][1] - trackCorners[0][1]) - (trackCorners[0][1] - trackCorners[1][1])*(gates[index][0] - trackCorners[0][0]), 0)
		# 1-4 
		crossProduct4 = round((trackCorners[4][0] - trackCorners[0][0])*(gates[index][1] - trackCorners[4][1]) - (trackCorners[4][1] - trackCorners[0][1])*(gates[index][0] - trackCorners[4][0]), 0)
		# 4-3
		crossProduct3 = round((trackCorners[3][0] - trackCorners[4][0])*(gates[index][1] - trackCorners[3][1]) - (trackCorners[3][1] - trackCorners[4][1])*(gates[index][0] - trackCorners[3][0]), 0)
		# 3-2
		crossProduct2 = round((trackCorners[1][0] - trackCorners[3][0])*(gates[index][1] - trackCorners[1][1]) - (trackCorners[1][1] - trackCorners[3][1])*(gates[index][0] - trackCorners[1][0]), 0)

		if rectangleOrientation == -1:
			if crossProduct1 > 0 and crossProduct2 > 0 and crossProduct3 > 0 and crossProduct4 > 0 and trackCorners[2][0] != 0 and trackCorners[2][1] != 0:  
				if gates[index-1][2] == 1 or index == 0:
					gates[index][2] = 1
					gates[index][3] = distanceBetweenTwoPoints((gates[index][0], gates[index][1]), (trackCorners[0][0], trackCorners[0][1]))
					gates[index][4] = distanceBetweenTwoPoints((gates[index][0], gates[index][1]), (trackCorners[1][0], trackCorners[1][1]))
				else: gates[index][2] = 0
			else: gates[index][2] = 0
		else:
			if crossProduct1 < 0 and crossProduct2 < 0 and crossProduct3 < 0 and crossProduct4 < 0 and trackCorners[2][0] != 0 and trackCorners[2][1] != 0:
				if gates[index-1][2] == 1 or index == 0:	 
					gates[index][2] = 1
					gates[index][3] = distanceBetweenTwoPoints((gates[index][0], gates[index][1]), (trackCorners[0][0], trackCorners[0][1]))
					gates[index][4] = distanceBetweenTwoPoints((gates[index][0], gates[index][1]), (trackCorners[1][0], trackCorners[1][1]))
				else: gates[index][2] = 0
			else: gates[index][2] = 0

	currentNumberOfGates = 0
	for index in range(constants.maxGateNumber):
		if gates[index][2] == 1: currentNumberOfGates += 1

	numberOfGates = currentNumberOfGates

def getWindowCenterCircleCoordinates(image):
	circleCenterX = (int)((image.shape[1]-1) / 2)
	circleCenterY = (int)((image.shape[0]-1) / 2)

	return circleCenterX, circleCenterY, constants.centerCircleRadius

def checkMeasuringMarkerPosition(image, centerX, centerY):
	circleCenterX, circleCenterY, radius = getWindowCenterCircleCoordinates(image)
	if (circleCenterX < centerX + radius and circleCenterX > centerX - radius) and (circleCenterY < centerY + radius and circleCenterY > centerY - radius): return True

def distanceBetweenTwoPoints(p0, p1):
	return (int)(math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2))

def getWidthHeight():
	print("width", end = " ")
	print(distanceBetweenTwoPoints((trackCorners[0][0], trackCorners[0][1]), (trackCorners[1][0], trackCorners[1][1])) * centimeterToPixelRatio)
	print("height", end = " ")
	print(distanceBetweenTwoPoints((trackCorners[0][0], trackCorners[0][1]), (trackCorners[5][0], trackCorners[5][1])) * centimeterToPixelRatio)

def getIntersections(x0, y0, r0, x1, y1, r1):
    # circle 1: (x0, y0), radius r0
    # circle 2: (x1, y1), radius r1

	d=math.sqrt((x1-x0)**2 + (y1-y0)**2)
    
	# non intersecting
	if d > r0 + r1:
		print("non intersecting")
		return None
    # One circle within other
	if d < abs(r0-r1):
		print("within")
		return None
	# coincident circles
	if d == 0 and r0 == r1:
		print("coincident")
		return None
	else:
		print("good")
		a=(r0**2-r1**2+d**2)/(2*d)
		h=math.sqrt(r0**2-a**2)
		x2=x0+a*(x1-x0)/d   
		y2=y0+a*(y1-y0)/d   
		x3=x2+h*(y1-y0)/d     
		y3=y2-h*(x1-x0)/d 

		x4=x2-h*(y1-y0)/d
		y4=y2+h*(x1-x0)/d

		return (int(x3), int(y3), int(x4), int(y4))

# TODO are you sure window and all data displayed, name	
def saveTrack():
	trackId = 0
	gate = ["" for x in range(3)]

	# first pull to check id
	fileName = os.path.dirname(os.path.realpath(__file__)) + '/' + constants.jsonTracksFileName
	jsonFile = open(fileName,)
	
	try:
		data = json.load(jsonFile)
		for i in data['test_tracks']:
			trackId = trackId + 1
	except:
		print("empty file")
	finally:
		jsonFile.close()

	from gui import trackNamePopup
	trackName = trackNamePopup()

	# ratio not needed?

	width = distanceBetweenTwoPoints((trackCorners[0][0], trackCorners[0][1]), (trackCorners[1][0], trackCorners[1][1]))
	height = distanceBetweenTwoPoints((trackCorners[0][0], trackCorners[0][1]), (trackCorners[4][0], trackCorners[4][1]))

	dictionary = {
		"id": trackId,
		"track_name": trackName,
		"ratio": centimeterToPixelRatio,
		"width_distance":  width * centimeterToPixelRatio,
		"height_distance": height * centimeterToPixelRatio,
		"width_pixels":  width,
		"height_pixels": height,
		"number_of_gates": numberOfGates
	}

	for x in range(constants.maxGateNumber):
		if gates[x][2] == 1:
			gate[x] = "gate_" + str(x+1)
			dictionary[gate[x]] = []
			dictionary[gate[x]].append({"pixels_from_0": gates[x][3], "pixels_from_1": gates[x][4]})

	with open(fileName) as fd:
	    dest = json.load(fd)
	    dest["test_tracks"].append(dictionary)
	with open(fileName, 'w') as fd:
	    json.dump(dest, fd)

	with open(fileName, 'r') as handle:
		parsed = json.load(handle)
		actuallyParsed = json.dumps(parsed, indent=4, sort_keys=True)
		print(actuallyParsed)

def loadTrack(image):
	global trackCorners, gates, centimeterToPixelRatio, loadedGates, numberOfGates
	goodTracks = ["" for x in range(50)]
	dataIndex = 0

	fileName = os.path.dirname(os.path.realpath(__file__)) + '/' + constants.jsonTracksFileName

	w = distanceBetweenTwoPoints((trackCorners[0][0], trackCorners[0][1]), (trackCorners[1][0], trackCorners[1][1])) * centimeterToPixelRatio
	h = distanceBetweenTwoPoints((trackCorners[0][0], trackCorners[0][1]), (trackCorners[4][0], trackCorners[4][1])) * centimeterToPixelRatio

	file = open(fileName,)
	data = json.load(file)
	for layout in data['test_tracks']:
	    if h >= layout['height_distance'] and w >= layout['width_distance'] and numberOfGates >= layout['number_of_gates']:
	    	goodTracks[dataIndex] = layout
	    	dataIndex += 1

	for i in range(dataIndex):
		print(goodTracks[i])

	import secondGui
	selectedTrack = secondGui.trackSelectionPopup(goodTracks, dataIndex)
	print(selectedTrack)

	loadedWidthDistance = loadedHeightDistance = loadedNumberOfGates = 0
	loadedRatio = loadedWidthPixels = loadedHeightPixels = 0

	for layout in data['test_tracks']:
		if selectedTrack == layout['track_name']:
			loadedRatio = layout['ratio']
			#loadedWidthPixels = layout['width_pixels']
			#loadedHeightPixels = layout['height_pixels']
			loadedWidthDistance = layout['width_distance']
			loadedHeightDistance = layout['height_distance']
			loadedNumberOfGates = layout['number_of_gates']
			for index in range(loadedNumberOfGates):
				gateNr = 'gate_' + str(index + 1)
				for dist in layout[gateNr]:
					loadedGates[index][3] = dist['pixels_from_0']
					loadedGates[index][4] = dist['pixels_from_1']
			break

	if loadedHeightDistance == 0 and loadedWidthDistance == 0:
		return

	loadedTrackCorners[0][0] = trackCorners[0][0]
	loadedTrackCorners[0][1] = trackCorners[0][1]
	
	widthRatio = loadedWidthDistance / w
	loadedTrackCorners[1][0] = int(widthRatio * trackCorners[1][0] + (1 - widthRatio) * trackCorners[0][0])
	loadedTrackCorners[1][1] = int(widthRatio * trackCorners[1][1] + (1 - widthRatio) * trackCorners[0][1])	

	heightRatio = loadedHeightDistance / h	
	loadedTrackCorners[3][0] = int(heightRatio * trackCorners[4][0] + (1 - heightRatio) * trackCorners[0][0])
	loadedTrackCorners[3][1] = int(heightRatio * trackCorners[4][1] + (1 - heightRatio) * trackCorners[0][1])

	p0Top1Diff = (loadedTrackCorners[1][0] - loadedTrackCorners[0][0]), (loadedTrackCorners[1][1] - loadedTrackCorners[0][1])

	loadedTrackCorners[2][0] = int(loadedTrackCorners[3][0] + p0Top1Diff[0])
	loadedTrackCorners[2][1] = int(loadedTrackCorners[3][1] + p0Top1Diff[1])

	for index in range(loadedNumberOfGates):
		(x3, y3, x4, y4) = getIntersections(loadedTrackCorners[0][0], loadedTrackCorners[0][1], loadedGates[index][3], loadedTrackCorners[1][0], loadedTrackCorners[1][1], loadedGates[index][4])

		# 2-1
		crossProduct1 = round((loadedTrackCorners[0][0] - loadedTrackCorners[1][0])*(y3 - loadedTrackCorners[0][1]) - (loadedTrackCorners[0][1] - loadedTrackCorners[1][1])*(x3 - loadedTrackCorners[0][0]), 0)
		# 1-4 
		crossProduct4 = round((loadedTrackCorners[3][0] - loadedTrackCorners[0][0])*(y3 - loadedTrackCorners[3][1]) - (loadedTrackCorners[3][1] - loadedTrackCorners[0][1])*(x3 - loadedTrackCorners[3][0]), 0)
		# 4-3
		crossProduct3 = round((loadedTrackCorners[2][0] - loadedTrackCorners[3][0])*(y3 - loadedTrackCorners[2][1]) - (loadedTrackCorners[2][1] - loadedTrackCorners[3][1])*(x3 - loadedTrackCorners[2][0]), 0)
		# 3-2
		crossProduct2 = round((loadedTrackCorners[1][0] - loadedTrackCorners[2][0])*(y3 - loadedTrackCorners[1][1]) - (loadedTrackCorners[1][1] - loadedTrackCorners[2][1])*(x3 - loadedTrackCorners[1][0]), 0)

		if crossProduct1 < 0 and crossProduct2 < 0 and crossProduct3 < 0 and crossProduct4 < 0:  
			loadedGates[index][0] = x3
			loadedGates[index][1] = y3
		else:
			loadedGates[index][0] = x4
			loadedGates[index][1] = y4
		

# ----------------------------------------------------------------------------------------------------------------------------
# display

# windows display
def refreshWindows(image, focusedTrackImage):
	global lockedBoundaries

	cv2.line(image, (loadedTrackCorners[0][0], loadedTrackCorners[0][1]), (loadedTrackCorners[1][0], loadedTrackCorners[1][1]), constants.green, constants.lineWidth)
	cv2.line(image, (loadedTrackCorners[3][0], loadedTrackCorners[3][1]), (loadedTrackCorners[0][0], loadedTrackCorners[0][1]), constants.green, constants.lineWidth)

	cv2.line(image, (loadedTrackCorners[2][0], loadedTrackCorners[2][1]), (loadedTrackCorners[1][0], loadedTrackCorners[1][1]), constants.green, constants.lineWidth)
	cv2.line(image, (loadedTrackCorners[2][0], loadedTrackCorners[2][1]), (loadedTrackCorners[3][0], loadedTrackCorners[3][1]), constants.green, constants.lineWidth)

	for index in range(numberOfGates):
		if (gates[index][0] < loadedGates[index][0] + int(constants.borderCircleRadius/4) and gates[index][0] > loadedGates[index][0] - int(constants.borderCircleRadius/4)) and (gates[index][1] < loadedGates[index][1] + int(constants.borderCircleRadius/4) and gates[index][1] > loadedGates[index][1] - int(constants.borderCircleRadius/4)): 
			loadedGates[index][2] = 1
		else:
			loadedGates[index][2] = 0

		if loadedGates[index][2] == 0:
			cv2.circle(image, (loadedGates[index][0], loadedGates[index][1]), int(constants.borderCircleRadius/4), constants.yellow, constants.borderCircleWidth)
		else:
			cv2.circle(image, (loadedGates[index][0], loadedGates[index][1]), int(constants.borderCircleRadius/4), constants.green, constants.borderCircleWidth)

	cv2.imshow('Focused track', focusedTrackImage)
	cv2.imshow('Gate setup', image)

	keyPress = cv2.waitKey(33)
	if keyPress == 27:    # Esc key to stop
		cv2.destroyAllWindows()
		return False
	elif keyPress == 97 or keyPress == 65:	# a or A to get track distances
		getWidthHeight()
	elif keyPress == 115 or keyPress == 83:	# s or S to save track
		saveTrack()
	elif keyPress == 108 or keyPress == 76:	# l or L to load track
		loadTrack(image)
	elif keyPress == 107 or keyPress == 75: # k or K to lock boundaries
		lockedBoundaries = not lockedBoundaries
	elif keyPress != -1:
		print(keyPress) # else print its value

	return True

# crtanje pojedinacnog markera
def drawMarker(image, markerID, aMarker):	
	cv2.circle(image, (aMarker[4], aMarker[5]), constants.circleRadius, constants.red, constants.circleWidth)

# crtanje fokusirane staze
def drawFoucusedTrackWindow(image, focusedTrackImage, ids, markerID, centerX, centerY):
	# ako nisu svi markeri pronadeni izlazi i vraca primljenu sliku (zadnju u nizu)
	if constants.corner1ID not in ids and constants.corner2ID not in ids and constants.corner3ID not in ids: 
		return focusedTrackImage

	# get all gates and trackCorners and focused track coordinates
	setTrackMarkers(markerID, centerX, centerY)
	# get4thCorer(image)
	(minCornerX, minCornerY, maxCornerX, maxCornerY) = getFocusedTrackCoordinates(image.shape[1]-1, image.shape[0]-1)

	# visual representation of the boundaries
	drawTrackBoundaries(image, minCornerX, minCornerY, maxCornerX, maxCornerY)

	# alter focused track image dimensions
	if 0 not in {minCornerX, minCornerY, maxCornerX, maxCornerY}:
		focusedTrackImage = image[minCornerY+constants.circleRadius:maxCornerY-constants.circleRadius, minCornerX+constants.circleRadius:maxCornerX-constants.circleRadius]

	return focusedTrackImage

# crtanje granica
def drawTrackBoundaries(image, minCornerX, minCornerY, maxCornerX, maxCornerY):
	setImaginaryBoundaries()

	# tocke krajnjih granica staze
	cv2.circle(image, (minCornerX, minCornerY), constants.circleRadius, constants.yellow, constants.circleWidth)
	cv2.circle(image, (maxCornerX, maxCornerY), constants.circleRadius, constants.yellow, constants.circleWidth)

	# slucaj kada marker za sirinu nije na ekranu
	if (trackCorners[1][0] == 0 and trackCorners[1][1] == 0) or (trackCorners[2][0] == 0 and trackCorners[2][1] == 0): return 

	# prikaz linija
	# 0-1
	cv2.line(image, (trackCorners[0][0], trackCorners[0][1]), (trackCorners[1][0], trackCorners[1][1]), constants.blue, constants.lineWidth)

	# pravokutnik izracunatih granica
	cv2.line(image, (trackCorners[4][0], trackCorners[4][1]), (trackCorners[0][0], trackCorners[0][1]), constants.blue, constants.lineWidth)
	cv2.line(image, (trackCorners[3][0], trackCorners[3][1]), (trackCorners[1][0], trackCorners[1][1]), constants.blue, constants.lineWidth)
	cv2.line(image, (trackCorners[3][0], trackCorners[3][1]), (trackCorners[4][0], trackCorners[4][1]), constants.blue, constants.lineWidth)

# crtanje sredisnjeg kvadrata
def drawCenterMeasuringCircle(image):
	circleCenterX, circleCenterY, radius = getWindowCenterCircleCoordinates(image)
	cv2.circle(image, (circleCenterX, circleCenterY), radius, constants.red, constants.borderCircleWidth)


# main program
# ----------------------------------------------------------------------------------------------------------------------------
def mainLoop():
	global trackCorners, centimeterToPixelRatio

	# lokalne varijable
	calibrationMarkerDiagonalPixels = 0 	# broj piksela u dijagonali markera koji oznacuje pocetno stanje, koristen za odredivanje udaljenosti
	looping = True 							# ako je false se program prestaje izvrsavati
	measuringMarkerInsideLimits = False		# provjera ako je 0-ti marker unutar granica
	distanceSet = False						# provjera ako je relativna udaljenost odredena

	# D435i setup i kalibracija
	pipeline = camera.pipelineInitilazation()
	cameraMatrix, cameraDistortionCoefficients = camera.pipelineCalibration(pipeline)

	# inicijalizacija razlicitih frameova (okvira) koji se koriste
	focusedTrackImage = camera.pipelineToImage(pipeline)	# granice staze, bez okolnih stvari
	#rotated = camera.pipelineToImage(pipeline)				# prikazana staza u ravnini sa prozorom

	while looping:
		# pretvorba frameova u sliku
		image = camera.pipelineToImage(pipeline)

		if lockedBoundaries:
			looping = refreshWindows(image, focusedTrackImage)
			continue

		# nalazenje markera na slici
		aCorner, ids, rotationVectors, translationVectors = aruco.findArucoMarkers(image, cameraMatrix, cameraDistortionCoefficients) 	

		# crtanje granica u kojima treba biti mjerni marker
		if not measuringMarkerInsideLimits: drawCenterMeasuringCircle(image)

		# ako nije pronasao niti jedan marker, vraca se na pocetak petlje
		if not len(aCorner):
			looping = refreshWindows(image, focusedTrackImage)
			continue

		ids = ids.flatten()		# ([[1,2], [3,4]]) -> ([1, 2, 3, 4])

		zipped = zip(aCorner, ids, rotationVectors, translationVectors)
		zipped = list(zipped)

		zippedSorted = sorted(zipped, key = lambda x: x[1])

		# prolazak kroz sve markere
		for (markerCorner, markerID, rotationVector, translationVector) in zippedSorted:
			if markerID != constants.measuringMarkerID and not measuringMarkerInsideLimits: 
				continue # prolazak po markerima dok se ne pronade mjerni marker, ali samo ako nije unutar granica

			# nije corners nego corner
			aCorner = markerCorner.reshape((4, 2)) 	#promjena matrice u dimenzije 4 para
			aMarker = getMarkerCoordinates(aCorner) 	# koordinate svih tocaka markera - topLeft, topRight, bottomRight, bottomLeft, centerX, centerY
			drawMarker(image, markerID, aMarker)	# crtanje centra svih markera

			# provjera ako je mjerni marker unutar kalibracijskih granica
			if not measuringMarkerInsideLimits:
				measuringMarkerInsideLimits = checkMeasuringMarkerPosition(image, aMarker[4], aMarker[5])
				# ako nakon provjere nije, proces krece ispocetka
				if not measuringMarkerInsideLimits: break

			# odredivanje udaljenosti kada je mjerni marker unutar granica, ali udaljenost nije odredena
			if not distanceSet and markerID == constants.measuringMarkerID:
				calibrationMarkerDiagonalPixels = distanceBetweenTwoPoints(aMarker[0], aMarker[2])
				constants.borderCircleRadius = (int)(3 * calibrationMarkerDiagonalPixels / 4)
				centimeterToPixelRatio = constants.markerDiagonalLength / calibrationMarkerDiagonalPixels
				distanceSet = True
			
			# pocetak programa nakon kalibracije udaljenosti
			# pronalazenje i crtanje vanjskih granica
			focusedTrackImage = drawFoucusedTrackWindow(image, focusedTrackImage, ids, markerID, aMarker[4], aMarker[5])

			# crtanje vektora orijentacije markera
			initialTestRotationVector = np.array([rotationVector[0][0], rotationVector[0][1], rotationVector[0][2]])
			testRotationVector = initialTestRotationVector.astype(float)
			theta = math.sqrt(rotationVector[0][0]*rotationVector[0][0] + rotationVector[0][1]*rotationVector[0][1] + rotationVector[0][2]*rotationVector[0][2])
			rotationAxis = rotationVector / theta
			if markerID == constants.gate1ID or markerID == constants.gate2ID or markerID == constants.gate3ID:
				cv2.aruco.drawAxis(image, cameraMatrix, cameraDistortionCoefficients, rotationVector, translationVector, constants.markerOrientationLength)
				# tocka na kvadratu koja sijece kvadrat i pravac usmjerenja?
				#cv2.line(image, (aMarker[4], aMarker[5]), (int(aMarker[4] * rotationAxis[0][0]), int(aMarker[5] * rotationAxis[0][1])), constants.red, constants.lineWidth)

		# prikaz glavnih prozora
		looping = refreshWindows(image, focusedTrackImage)

	# prestanak primanja podataka od kamera
	pipeline.stop()

if __name__ == '__main__':
	mainLoop()