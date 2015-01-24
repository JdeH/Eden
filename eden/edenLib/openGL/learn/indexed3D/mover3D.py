#!/usr/bin/env python

import sys
import ctypes as ct
import numpy as np
import math as mt
import datetime as dt

import OpenGL.GL as gl
import OpenGL.GLUT as glut

import openGLDebug as dbg
import util as ut
import transformations as trf
import program as prg

# gl.FULL_LOGGING = True

class Mover3D:
	framesPerSecond = 50
	milliSecondsPerFrame = 1000 / framesPerSecond	# Must be integer	
	positionDim = 3
	colorDim = 4
	windowSize = 512
	fieldOfViewY = mt.pi / 3
	zNearFarVec = np.matrix ([1, 10]).T
	fieldList = [('position', np.float32, positionDim), ('color', np.float32, colorDim)]
	
	def __init__ (self):
		self.aspectRatio = 1
		self.angle = 0
		self.startTime = dt.datetime.now ()
	
		# Initialize GLUT
	
		def display ():
			gl.glClear (gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
			gl.glDrawElements (gl.GL_TRIANGLES, self.getSubjectIndices () .shape [0], prg.Program.dataTypesGl ['uint16'], None)
			glut.glutSwapBuffers ()

		def reshape (width, height):
			self.aspectRatio = float (width) / height
			gl.glViewport (0, 0, width, height)

		def keyboard (key, x, y):
			sys.exit ()
			
		def setTransform ():
			self.program.setUniform ('transformation',
				trf.getPerspMat (self.fieldOfViewY, self.aspectRatio, self.zNearFarVec) *
				self.getPositionMat ()
			)
			
		def timer (dummy):
			setTransform ()
			
			glut.glutTimerFunc (self.milliSecondsPerFrame, timer, None)
			glut.glutPostRedisplay ()

		glut.glutInit ()
		glut.glutInitDisplayMode (glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH | glut.GLUT_MULTISAMPLE)			
		glut.glutCreateWindow ('Vertex and fragment shaders')		
		glut.glutReshapeWindow (self.windowSize, self.windowSize)
		glut.glutReshapeFunc (reshape)
		glut.glutDisplayFunc (display)
		glut.glutKeyboardFunc (keyboard)
		glut.glutTimerFunc (0, timer, None)
		
		gl.glClearColor (0.2, 0.2, 0.2, 1)
		gl.glEnable (gl.GL_DEPTH_TEST)
		
		# Initialize shaders
		
		self.program = prg.Program (
			prg.Shader (
				'vertex',
				'''
					uniform mat4 transformation;
					attribute vec3 position;
					attribute vec4 color;
					varying vec4 varyingColor;
					void main () {
						gl_Position = vec4 (transformation * vec4 (position, 1));
						varyingColor = color;
					}		
				'''
			),
			prg.Shader (
				'fragment',
				'''
					varying vec4 varyingColor;
					void main () {
						gl_FragColor = varyingColor;
					}
				'''
			),
		)
		
		# Set subject to be displayed
		
		self.program.setVertices (self.getSubjectVertices ())
		self.program.setIndices (self.getSubjectIndices ())
				
		# Enter GLUT main loop
		
		glut.glutMainLoop ()
		
	def getSubjectVertices (self):	# Default subjectVertices may be class attribute
		return self.subjectVertices
		
	def getSubjectIndices (self):	# Default subjectIndices may be class attribute
		return self.subjectIndices
		
	def getPositionMat (self):	# Default positionMatrix may be class attribute
		return self.positionMatrix
		
	def getElapsedTime (self):
		return (dt.datetime.now () - self.startTime) .total_seconds ()
		