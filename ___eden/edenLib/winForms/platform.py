# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# import sys

import clr
import os

clr.AddReference ('System.Windows.Forms')

from System.Windows import Forms

def getStackTrace (exception):
	return exception.clsException.StackTrace.replace ('\r\n', '\n')

class IntervalTimer:
	def __init__ (self):
		self.callBacks = []
		self.intervals = []
		self.timesLeft = []
	
		self.timer = Forms.Timer ()
		self.timer.Interval = 100	# ms
		self.timer.Tick += self.tick
		self.timer.Start ()
		
	def addCallBack (self, intervalSeconds, callBack):
		self.intervals.append (int (10 * intervalSeconds))
		self.timesLeft.append (0)
		self.callBacks.append (callBack)
	
	def tick (self, sender, event):
		for index, callBack in enumerate (self.callBacks):
			if not self.timesLeft [index]:
				callBack ()
				self.timesLeft [index] = self.intervals [index]
				
			self.timesLeft [index] -= 1			
	
# Example: types = [('Text files (*.txt)', '.txt'), ('Document files (*.doc)', '.doc')]	
