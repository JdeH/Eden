import ctypes as ct
import numpy as np

import OpenGL.GL as gl

class Shader:
	shaderTypesGl = {'vertex': gl.GL_VERTEX_SHADER, 'fragment': gl.GL_FRAGMENT_SHADER}
	
	def __init__ (self, aType, code):
		self.aType = aType
		self.code = code
		
		self.shaderGl = gl.glCreateShader (self.shaderTypesGl [self.aType])
		gl.glShaderSource (self.shaderGl, self.code)
		gl.glCompileShader (self.shaderGl)
		
class Program:
	dataTypesGl = {'float32': gl.GL_FLOAT}
	
	def __init__ (self, *shaders):
		self.testShaders = shaders
	
		self.programGl = gl.glCreateProgram ()
		
		for shader in shaders:					
			gl.glAttachShader (self.programGl, shader.shaderGl)
			
		gl.glLinkProgram (self.programGl)
		
		for shader in shaders:
			gl.glDetachShader (self.programGl, shader.shaderGl)
			
		gl.glUseProgram (self.programGl)
		
	def setUniform (self, name, value):
		location = gl.glGetUniformLocation (self.programGl, name)	# Reference to 'aspect' field in program
		if isinstance (value, np.matrix):
			if value.shape == (4, 4):
				gl.glUniformMatrix4fv (location, 1, gl.GL_FALSE, value.T.tolist ())
			elif value.shape == (4, 1):
				gl.glUniform4fv (location, 1, value.tolist ())
			else:
				raise Exception ('Invalid shape')
		else:
			gl.glUniform1f (location, value)
			
	def setAttributes (self, vertices):
		buffer = gl.glGenBuffers (1)	# Get empty buffer
		gl.glBindBuffer (gl.GL_ARRAY_BUFFER, buffer)	# Make buffer current
		gl.glBufferData (gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_DYNAMIC_DRAW)	# Copy data to buffer
	
		stride = vertices.dtype.itemsize	
		offset = 0
		
		for attributeName in vertices.dtype.names:
			location = gl.glGetAttribLocation (self.programGl, attributeName)	# Get meta-info object of attribute
			attribute = vertices.dtype [attributeName]
			dimension = attribute.shape [0]
			typeName = attribute.subdtype [0] .name
			gl.glEnableVertexAttribArray (location)	# Make attribute accessible in vertex attribute array
			gl.glVertexAttribPointer (location, dimension, self.dataTypesGl [typeName], False, stride, ct.c_void_p (offset))	# Connect vertex attribute array to the right places the in already filled buffer
			offset += attribute.itemsize
			
			
			