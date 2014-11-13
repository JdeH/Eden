# Copyright (C) 2005, 2006 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

codedSpace = '~'

class XmlReader:
	def __init__ (self, optional = False):
		self.optional = optional
	
	def open (self, fileName):
		self.fileName = fileName
		self.tagNameStack = []
		
		file = open (self.fileName, 'r')
		self.words = file.read () .split ()
		
		file.close ()
			
		self.wordIndex = 0
		self.skipComment ()

	def close (self):
		pass

	def readOpenTag (self, tagName, optional = None):
		ok =  self.words [self.wordIndex] == '<' + tagName + '>'

		if ok:
			self.tagNameStack.append (tagName)
			self.wordIndex += 1
			self.skipComment ()
		elif (optional is None and not self.optional) or (optional is not None and not optional):
			raise Error ('File ' + self.fileName + ' corrupt, expected = <' + tagName + '>, found = ' + self.words [self.wordIndex])
			
		return ok
	
	def readCloseTag (self, tagName = None):
		openTagName = self.tagNameStack.pop ()
		
		if tagName and tagName != openTagName:
			raise Error ('File ' + self.fileName + ' corrupt, openTagName = ' + openTagName + ', closeTagName = ' + tagName)
		
		ok = self.words [self.wordIndex] == '</' + openTagName + '>'
		
		if ok:
			self.wordIndex += 1
			try:
				self.skipComment ()
			except:	# End of file
				pass
		else:
			raise Error ('File ' + self.fileName + ' corrupt, expected = </' + openTagName + '>, found = ' + self.words [self.wordIndex])
			
		return ok
			
	def readClause (self, tagName, optional = None):
		if not self.readOpenTag (tagName, optional):
			return False
			
		targetField = self.readTargetField ()
		self.readCloseTag ()
		return targetField

	def assignClause (self, tagName, targetObject, targetAttributeName, converter = None, optional = None):
		result = self.readClause (tagName, optional)
		
		if result:
			if converter:
				setattr (targetObject, targetAttributeName, converter (result))
			else:
				setattr (targetObject, targetAttributeName, result)

	def enterClause (self, tagName, targetAggregate, targetIndex, converter = None, optional = None):
		result = self.readClause (tagName, optional)
		
		if result:
			if converter:
				targetAggregate [targetIndex] = converter (result)
			else:
				targetAggregate [targetIndex] = result

	def readTargetField (self):
		targetField = self.decode (self.words [self.wordIndex])
		self.wordIndex += 1
		self.skipComment ()
		return targetField
		
	def decode (self, string):
		return string.replace (codedSpace, ' ')
		
	def skipComment (self):
		if self.words [self.wordIndex] == '<comment>':
			self.wordIndex += 1
			while self.words [self.wordIndex] != '</comment>':
				self.wordIndex += 1
			self.wordIndex += 1
	
class XmlWriter:
	def open (self, fileName = ''):
		self.tagNameStack = []
		self.fileName = fileName
		self.lines = []
		self.nrOfTabs = 0

	def close (self):
		self.lines.append ('')
	
		if self.fileName:
			file = open (self.fileName, 'w')
			file.write ('\n'.join (self.lines))
			file.close ()
			
		return self.lines

	def writeOpenTag (self, tagName):
		self.tagNameStack.append (tagName)
		self.lines.append (self.getTabs () + '<' + tagName + '>')
		self.nrOfTabs += 1
		return True
	
	def writeCloseTag (self, tagName = None):
		self.nrOfTabs -= 1
		openTagName = self.tagNameStack.pop ()
		
		if tagName and tagName != openTagName:
			raise Error ('XmlWriter for file ' + self.fileName + ' inconsistent, openTagName = ' + openTagName + ', closeTagName = ' + tagName)
			
		self.lines.append (self.getTabs () + '</' + openTagName + '>')
		
	def writeField (self, sourceField, coderActive = True):
		self.lines.append (self.getTabs () + self.encode (self.canonize (sourceField), coderActive))
		
	def writeClause (self, tagName, sourceField, coderActive = True):
		self.lines.append (self.getTabs () + '<' + tagName + '> ' + self.encode (self.canonize (sourceField), coderActive) + ' </' + tagName + '>')
		
	def canonize (self, field):
		if field.__class__ == str:
			return field
		else:
			return repr (field)		
		
	def encode (self, string, coderActive = True):
		if coderActive:
			return string.replace (' ', codedSpace)
		else:
			return string
		
	def getTabs (self):
		return ''.join (['\t' for tabIndex in range (self.nrOfTabs)])
		
def readXmlDict (fileName):
	file = open (fileName, 'r')
	words = file.read () .split ()
	file.close ()
	
	xmlDict = {}
	inClause = False
	
	for word in words [1:-1]:
		if inClause:
			if word [0] == '<':
				xmlDict [tag] = body
				inClause = False
			else:
				body.append (word)
		else:
			tag = word [1:-1]
			body = []
			inClause = True
			
	return xmlDict
