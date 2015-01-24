import math as mt
import numpy as np

def getTranslMat (translVec):	
	return np.matrix (
		[
			[1, 0, 0, translVec [0]],
			[0, 1, 0, translVec [1]],
			[0, 0, 1, translVec [2]],
			[0, 0, 0, 1],
		],
		dtype = np.float32
	)

def getScalMat (scalVec):
	return np.matrix (
		[
			[scalVec [0], 0, 0, 0],
			[0, scalVec [1], 0, 0],
			[0, 0, scalVec [2], 0],
			[0, 0, 0, 1],
		],
		dtype = np.float32
	)

def getRotXMat (angle):
	c = mt.cos (angle)
	s = mt.sin (angle)
	return np.matrix (
		[
			[1, 0, 0, 0],
			[0, c, -s, 0],
			[0, s, c, 0],
			[0, 0, 0, 1]
		],
		dtype = np.float32
	)

def getRotYMat (angle):
	c = mt.cos (angle)
	s = mt.sin (angle)
	return np.matrix (
		[
			[c, 0, s, 0],
			[0, 1, 0, 0],
			[-s, 0, c, 0],
			[0, 0, 0, 1]
		],
		dtype = np.float32
	)

def getRotZMat (angle):
	c = mt.cos (angle)
	s = mt.sin (angle)
	return np.matrix (
		[
			[c, -s, 0, 0],
			[s, c, 0, 0],
			[0, 0, 1, 0],
			[0, 0, 0, 1]
		],
		dtype = np.float32
	)
	
def getRotXYZMat (angleVec):	# Z rotation first
	return (
		getRotXMat (angleVec [2]) *
		getRotYMat (angleVec [1]) *
		getRotzMat (angleVec [0])
	)

def getRotXZYMat (angleVec):
	return (
		getRotXMat (angleVec [2]) *
		getRotZMat (angleVec [1]) *
		getRotYMat (angleVec [0])
	)

def getRotYXZMat (angleVec):
	return (
		getRotYMat (angleVec [2]) *
		getRotXMat (angleVec [1]) *
		getRotZMat (angleVec [0])
	)

def getRotYZXMat (angleVec):
	return (
		getRotYMat (angleVec [2]) *
		getRotZMat (angleVec [1]) *
		getRotXMat (angleVec [0])
	)

def getRotZXYMat (angleVec):
	return (
		getRotZMat (angleVec [2]) *
		getRotXMat (angleVec [1]) *
		getRotYMat (angleVec [0])
	)

def getRotZYXMat (angleVec):
	return (
		getRotZMat (angleVec [2]) *
		getRotYMat (angleVec [1]) *
		getRotXMat (angleVec [0])
	)
	
'''
    float f = 1.0f/float(tan(fov / 2.0f * (M_PI / 180.0f)));

    a[0 + 4 * 0] = f / aspect;
    a[1 + 4 * 1] = f;
    a[2 + 4 * 2] = (zNear + zFar) / (zNear - zFar);
    a[2 + 4 * 3] = 2.0f * zNear *+ zFar / (zNear - zFar);
    a[3 + 4 * 2] = -1.0f
'''	
	
def getPerspMat (fieldOfViewY, aspectRatio, zNearFarVec):	# Camera at (0, 0, 0), looking at (0, 0, -1)	
	cotan = 1. / mt.tan (fieldOfViewY / 2.)
	zN = float (zNearFarVec [0])
	zF = float (zNearFarVec [1])
	
	return np.matrix (
		[
			[cotan / aspectRatio, 0, 0, 0],
			[0, cotan, 0, 0],
			[0, 0, (zN + zF) / (zN - zF), 2. * zN * zF / (zN - zF)],
			[0, 0, -1., 0]
		],
		dtype = np.float32
	)
	
