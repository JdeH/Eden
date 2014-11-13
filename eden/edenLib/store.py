# Copyright (C) 2005, 2006 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

from cPickle import *
from eden.edenLib.base import *
from eden.edenLib.util import *
from eden.edenLib.node import *

class Store:
	def __init__ (self):
		self.storeDictionary = {}
		self.keyList = []
		self.autoKey = UniqueNumber ()
		self.afterLoadActionNode = Node (None)
		
	def name (self, fileName):
		self.fileName = fileName

	def setStoreFromList (self, storeList, sourceDescription):
		for item in storeList:
			try:
				self.storeDictionary [item [0]] .state = item [1]
			except Exception, exception:
				problem = (
					'Can not restore item ' + str (item [0]) +
					' with value ' + str (item [1]) +
					' from ' + sourceDescription + ', '
				)

				handleNotification (Remark (problem + exMessage (exception), report = problem + exReport (exception)))
				
		self.afterLoadActionNode.change (None, True)
	
	def getStoreAsList (self):
		storeList = []
	
		for key in self.keyList:
			try:
				storeList.append ((key, self.storeDictionary [key] .state))
			except:	# The object belonging to key may not yet have a valid state
				pass
				
		return storeList

	def load (self, fileName = None):
		if fileName:
			self.fileName = fileName
	
		try:
			file = open (self.fileName, 'r')
			storeList = load (file)
			file.close ()
			self.loaded = True
		except:
			storeList = []
			self.loaded = False

		self.setStoreFromList (storeList, 'file ' + self.fileName)
				
	def save (self, fileName = None):
		if fileName:
			self.fileName = fileName
	
		file = open (self.fileName, 'w')
		dump (self.getStoreAsList (), file)
		file.close ()

	def loadString (self, aString, sourceDescription = 'string'):
		self.setStoreFromList (loads (aString), sourceDescription)

	def saveString (self):
		return dumps (self.getStoreAsList ())

	def add (self, item, key = None):
		if key == None:
			key = self.autoKey.getNext ()
		
		self.keyList.append (key)
		self.storeDictionary [key] = item
		
		return item
	
#	def remove (self, item, key):
#		del self.storeDictionary [key]

	def getNewestVersion (self):
		newestVersion = 0
		
		for key in self.keyList:
			itemVersion = self.storeDictionary [key] .version
			
			if itemVersion > newestVersion:
				newestVersion = itemVersion
				
		return newestVersion
