# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# hexPane.py

from org.qquick.eden import *

class HexPane (Module):
	def __init__ (self):
		Module.__init__ (self)
		
	def defineModules (self):
		pass
		
	def defineNodes (self):
		self.addNode (Node (), 'contentNode')
		
	def defineDependencies (self):
		def getContent ():
			return ' '.join ('{:02x}'.format (aByte) for aByte in app.main.contentNode.new)
		
		self.contentNode.dependsOn ([app.main.contentNode], getContent)

	def defineViews (self):
		return VGridView ([
			LabelView (captionNode = 'Type here in HEX'),
			TextView (valueNode = self.contentNode, multiLine = True, autoCommit = True), 25
		])

	def defineActions (self):
		pass
		