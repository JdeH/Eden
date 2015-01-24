#!/usr/bin/env python

import sys
import ctypes as ct
import math as mt
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut

import openGLDebug as dbg
import transformations as trf
import mover3D as m3d

# gl.FULL_LOGGING = True

class Cube3D (m3d.Mover3D):
	nrOfCubeVertices = 8
	cubeVertices = np.zeros (nrOfCubeVertices, [('position', np.float32, 3), ('color', np.float32, 4)])

	cubeVertices ['position'] = [
		[1, 1, 1],
		[-1, 1, 1],
		[-1, -1, 1],
		[1, -1, 1],
		
		[1, 1, -1],
		[-1, 1, -1],
		[-1, -1, -1],
		[1, -1, -1]
	]

	cubeVertices ['color'] = [
		# Front is greenish
		[1, 0, 0, 1],
		[0, 1, 0, 1],
		[0, 0, 1, 1],
		[0, 1, 1, 1],
		
		# Rear is redish
		[1, 1, 0, 1],
		[0, 1, 1, 1],
		[1, 0, 1, 1],
		[0, 0, 0, 1]
	]

	cubeVertexIndices = [
		0, 1, 3, 3, 2, 1,	# Front
		4, 7, 6, 6, 5, 4,	# Rear
		0, 3, 7, 7, 4, 0,	# Right
		1, 5, 6, 6, 2, 1,	# Left
		0, 4, 5, 5, 1, 0,	# Top
		2, 6, 7, 7, 3, 2	# Bottom
	]	
	
	nrOfSubjectVertices = len (cubeVertexIndices)

	subjectVertices = np.zeros (nrOfSubjectVertices, m3d.Mover3D.fieldList)
	for attributeName in subjectVertices.dtype.names:
		subjectVertices [attributeName] = [cubeVertices [attributeName][cubeVertexIndices [subjectVertexIndex]] for subjectVertexIndex in range (nrOfSubjectVertices)]
		
	translVec = np.matrix ([0, 0, -4]).T
	
	def getPositionMat (self):
		rawAngle = 2 * mt.pi * self.getElapsedTime ()
		rotVec = rawAngle * np.matrix ([0.13, 0.17, 0.23]).T
		return trf.getTranslMat (self.translVec) * trf.getRotZYXMat (rotVec)
		
Cube3D ()
		