import ctypes as ct
import OpenGL.GL as gl
import OpenGL as ogl

from OpenGL.GL.ARB import debug_output
from OpenGL.extensions import alternate

def getConstant (value, namespace):
	for var in dir (namespace):
		attr = getattr (namespace, var)
		if isinstance (attr, ogl.constant.Constant) and attr == value:
			return var

def getDebugMessages ():
	msgMaxLength = 512
	msgCount = 100

	# ctypes arrays to receive the log data
	msgSources = (ct.c_uint32 * msgCount) ()
	msgTypes = (ct.c_uint32 * msgCount) ()
	msgIds = (ct.c_uint32 * msgCount) ()
	msgSeverities = (ct.c_uint32 * msgCount) ()
	msgLengths = (ct.c_uint32 * msgCount) ()
	msgLog = (ct.c_char * (msgMaxLength * msgCount)) ()

	gl.glGetDebugMessageLog (msgCount, msgMaxLength, msgSources, msgTypes, msgIds, msgSeverities, msgLengths, msgLog)

	offset = 0
	logData = zip (msgSources, msgTypes, msgIds, msgSeverities, msgLengths)
	
	debugMessages = ''
	for msgSource, msgType, msgId, msgSeverity, msgLength in logData:
		msgText = msgLog.raw [offset:offset + msgLength] .decode("ASCII")
		offset += msgLength
		msgSource = getConstant (msgSource, debug_output)
		msgType = getConstant (msgType, debug_output)
		msgSeverity = getConstant (msgSeverity, debug_output)
		
		if True or msgSource:
			debugMessages += 'SOURCE: {0}, TYPE: {1}, ID: {2}, SEVERITY: {3}, MESSAGE: {4}\n'.format (msgSource, msgType, msgId, msgSeverity, msgText)
	else:
		if debugMessages:
			debugMessages += '\n'
			
	return debugMessages
	