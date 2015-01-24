#!/usr/bin/env python

import sys
import ctypes as ct
import numpy as np
import math
import OpenGL.GL as gl
import OpenGL.GLUT as glut

windowSize = 400
nrOfTriangles = 6
framesPerSecond = 24
milliSecondsPerFrame = 1000 / framesPerSecond	# Must be integer

# === Shader source code

vertexSource = '''
	uniform vec2 aspect;
	uniform float zoom;
	uniform float angle;
	uniform float s;
	uniform float c;
	uniform mat2 rotation;
	attribute vec2 position;
	attribute vec4 color;
	varying vec4 varyingColor;
	void main () {
		s = sin (angle);
		c = cos (angle);
		rotation = mat2 (
			c, -s,
			s, c
		);
		gl_Position = vec4 (aspect * (zoom * rotation * position), 0.0, 1.0);
		varyingColor = color;
	}
'''

fragmentSource = '''
	varying vec4 varyingColor;
	void main () {
		gl_FragColor = varyingColor;
	}
'''

# === GLUT initialisation
	
def display ():
	gl.glClear (gl.GL_COLOR_BUFFER_BIT)
	gl.glDrawArrays (gl.GL_TRIANGLE_FAN, 0, nrOfTriangles)
	glut.glutSwapBuffers ()

def reshape (width, height):
	aspect = gl.glGetUniformLocation (program, 'aspect')
	theaspect = (float (height) / width, 1) if width > height else (1, float (width) / height)
	gl.glProgramUniform2f (program, aspect, theaspect [0], theaspect [1])

	gl.glViewport (0, 0, width, height)

def keyboard (key, x, y):
	sys.exit ()
	
def timer (dummy):
	timer.angle += 2 * math.pi / framesPerSecond	# So 1 rotation per second
	if timer.angle > 2 * math.pi * timer.maxGear:
		timer.angle = 0
	
	zoom = gl.glGetUniformLocation (program, 'zoom')
	gl.glProgramUniform1f (program, zoom, 0.75 + 0.25 * math.cos (timer.angle))
	
	angle = gl.glGetUniformLocation (program, 'angle')
	gl.glProgramUniform1f (program, angle, timer.angle / timer.maxGear)
	
	glut.glutTimerFunc (milliSecondsPerFrame, timer, None)
	glut.glutPostRedisplay ()
	
timer.angle = 0
timer.maxGear = 10
	
glut.glutInit ()
glut.glutInitDisplayMode (glut.GLUT_DOUBLE | glut.GLUT_RGBA)
glut.glutCreateWindow ('Vertex and fragment shaders')
glut.glutReshapeWindow (windowSize, windowSize)
glut.glutReshapeFunc (reshape)
glut.glutDisplayFunc (display)
glut.glutKeyboardFunc (keyboard)
glut.glutTimerFunc (0, timer, None)

	
# === Fill numpy data arrays

data = np.zeros (nrOfTriangles, dtype = [('position', np.float32, 2), ('color', np.float32, 3)])
data ['position'] = [(0, 0), (-1, -1), (-1, 1), (1, 1), (1, -1), (-1, -1)]
data ['color'] = [(1, 1, 1), (1, 1, 0), (1 , 0, 0), (0, 1 , 0), (0 , 0, 1), (1, 1, 0)]

# === Prepare program

# Get empty program and shaders
program	 = gl.glCreateProgram ()
vertexShader = gl.glCreateShader (gl.GL_VERTEX_SHADER)
fragmentShader = gl.glCreateShader (gl.GL_FRAGMENT_SHADER)

# Set shaders source code
gl.glShaderSource (vertexShader, vertexSource)
gl.glShaderSource (fragmentShader, fragmentSource)

# Compile shaders


gl.glCompileShader (vertexShader)
gl.glCompileShader (fragmentShader)

# Attach shaders to the program
gl.glAttachShader (program, vertexShader)
gl.glAttachShader (program, fragmentShader)

# Link program
gl.glLinkProgram (program)

# Remove shaders from program
gl.glDetachShader (program, vertexShader)
gl.glDetachShader (program, fragmentShader)

# Make this program the current one
try:
	gl.glUseProgram (program)
except:
	pass

# === Copy numpy data to OpenGL buffer and set format

# Get empty buffer
buffer = gl.glGenBuffers (1)

# Make this buffer the current one
gl.glBindBuffer (gl.GL_ARRAY_BUFFER, buffer)

# Copy data to buffer
gl.glBufferData (gl.GL_ARRAY_BUFFER, data.nbytes, data, gl.GL_DYNAMIC_DRAW)

# Tell OpenGL layout of buffer content
stride = data.strides [0]	# Size of 1 position item + size of 1 color item

offset = ct.c_void_p (0)	# C void pointer holding 0
# So pointing to first byte of first position in numpy array

attribute = gl.glGetAttribLocation (program, 'position')	# Reference to 'position' field in program
gl.glEnableVertexAttribArray (attribute)	# Make positions in buffer accessible
gl.glVertexAttribPointer (attribute, 2, gl.GL_FLOAT, False, stride, offset)	# 2 coordinates per vertex

offset = ct.c_void_p (data.dtype ['position'] .itemsize)	# C void pointer holding data.dtype ['position'] .itemsize
# So pointing to first byte of first color in numpy array

attribute = gl.glGetAttribLocation (program, 'color')	# Reference to 'color' field in program
gl.glEnableVertexAttribArray (attribute)	# Make colors in buffer accessible
gl.glVertexAttribPointer (attribute, 3, gl.GL_FLOAT, False, stride, offset)	# 3 color components per vertex and per pixel

# === Set uniforms

aspect = gl.glGetUniformLocation (program, 'aspect')	# Reference to 'aspect' field in program
gl.glUniform2f (aspect, 1., 1.)

zoom = gl.glGetUniformLocation (program, 'zoom')	# Reference to 'zoom' field in program
gl.glUniform1f (zoom, 1.)

angle = gl.glGetUniformLocation (program, 'angle')	# Reference to 'angle' field in program
gl.glUniform1f (angle, 0.)

# === Program entry point

glut.glutMainLoop ()

