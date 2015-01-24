# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

from .base import *
from .util import *
import inspect

edenPathMarker = '/org/qquick/'

if 'TkInter' in application.platform:
	from .tkInter.util import *

elif 'WinForms' in application.platform:
	from .winForms.util import *
			
elif 'Kivy' in application.platform:
	from .kivy.util import *
	
def decapitalize (aString):
	return aString [:1] .lower () + aString [1:] if aString else ''
	
def getCaller ():
	callerFrame = inspect.stack () [2]
	fileName = edenPathMarker [1:] + callerFrame [1] .replace ('\\', ('/')) .split (edenPathMarker) [1]
	lineNr = callerFrame [2]
	functionName = callerFrame [3]
	return (fileName, lineNr, functionName)
	
	

