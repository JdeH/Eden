# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# addPointsDialog.py

from eden import *

from pdBase import *

class AddPointsDialog (Module):
	def __init__ (self, projectionDialog):
		self.projectionDialog = projectionDialog
		self.main = projectionDialog.main
		Module.__init__ (self)
		
	def defineNodes (self):
		self.xMinNode = Node (0) 
		self.xMaxNode = Node (0) 

		self.yMinNode = Node (0) 
		self.yMaxNode = Node (0) 

		self.zMinNode = Node (0) 
		self.zMaxNode = Node (0) 
		
		self.colorNode = Node (Colors [0])
		
		self.doOkNode = Node (None)
		self.doCancelNode = Node (None)

	def defineViews (self):
		return ModalView (
			VGridView ([
				HGridView ([
					CLabelView ('X   from'),
					TextView (self.xMinNode),
					CLabelView ('to'),
					TextView (self.xMaxNode)
				]),
				HGridView ([
					CLabelView ('Y   from'),
					TextView (self.yMinNode),
					CLabelView ('to'),
					TextView (self.yMaxNode)
				]),
				HGridView ([
					CLabelView ('Z   from'),
					TextView (self.zMinNode),
					CLabelView ('to'),
					TextView (self.zMaxNode)
				]),
				FillerView (),
				HGridView ([
					FillerView (),
					CLabelView ('Color'),
					ComboView (self.colorNode, Colors),
					FillerView ()
				]),
				StretchView (),
				HGridView ([
					FillerView (),
					ButtonView (self.doOkNode, 'OK'),
					ButtonView (self.doCancelNode, 'Cancel')
				])
			]),
			'Add range of points',
			fixedSize = True,
			key = 'addPointsDialog'
		)
		
	def defineActions (self):
		def doOk ():
			self.main.pointsNode.follow (appendList (
				deepcopy (self.main.pointsNode.old),
				[
					[x, y, z, self.colorNode.new]
					for x in range (self.xMinNode.new, self.xMaxNode.new + 1)	
						for y in range (self.yMinNode.new, self.yMaxNode.new + 1)	
							for z in range (self.zMinNode.new, self.zMaxNode.new + 1)	
				]
			))
			self.getView () .exit ()
		
		self.doOkNode.action = doOk

		self.doCancelNode.action = self.getView (). exit