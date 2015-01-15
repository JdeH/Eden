# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

import os

class Anything (object):
	pass
	
class Pass (Anything):
	pass
	
class Application (Anything):	
	def setDebug (self, switch):
		self.logNotifications = switch
		self.setDebugExtra (switch)
		
	debug = property (None, setDebug)
		
application = Application ()
app = application

application.edenLibDirectory = os.path.dirname (os.path.abspath (__file__)) .replace ('\\', '/')
application.edenDirectory = '/'.join (application.edenLibDirectory.split ('/')[:-1])

if 'ironpython' in application.edenDirectory.lower ():
	application.platform = ['WinForms']
else:
	application.platform = ['Kivy']
