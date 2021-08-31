

import pyrealsense2 as rs
import numpy as np
import imutils

import constants

# pokretanje prijenosa podataka kamere
def pipelineInitilazation():
	pipeline = rs.pipeline()
	config = rs.config()
	config.enable_stream(rs.stream.color, constants.cameraCaptureResolutionX, constants.cameraCaptureResolutionY, rs.format.bgr8, constants.cameraCaptureFps)
	pipeline.start(config)
	return pipeline

# kalibracija kamere
def pipelineCalibration(pipeline):
	activeProfile = pipeline.get_active_profile()
	colorProfile = rs.video_stream_profile(activeProfile.get_stream(rs.stream.color))
	colorIntrinsics = colorProfile.get_intrinsics()
	cameraMatrix = [[colorIntrinsics.fx, 0, colorIntrinsics.ppx], [0, colorIntrinsics.fy, colorIntrinsics.ppy], [0, 0, 1]]
	return np.float32(cameraMatrix), np.float32(colorIntrinsics.coeffs)

# prijenos podataka u sliku
def pipelineToImage(pipeline):
	frames = pipeline.wait_for_frames()
	colorFrame = frames.get_color_frame()
	colorImage = np.asanyarray(colorFrame.get_data())
	colorImage = imutils.resize(colorImage, width=constants.windowWidth)
	return colorImage