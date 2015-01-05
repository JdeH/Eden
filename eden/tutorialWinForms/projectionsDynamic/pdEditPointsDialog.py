# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# editPointsDialog.py

from org.qquick.eden import *

from pdBase import *

class EditPointsDialog (Module):
	def __init__ (self, projectionDialog):
		self.projectionDialog = projectionDialog
		self.main = projectionDialog.main
		Module.__init__ (self)
		
	def defineNodes (self):
		self.colorNode = Node (Colors [0])

		self.doOkNode = Node (None)
		self.doCancelNode = Node (None)
		
	def defineViews (self):
		return ModalView (
			VGridView ([
				LLabelView ('Points whose color will be altered'),
				ListView (
					self.projectionDialog.selectedPointsNode,
					PointColumnLabels,
					key = 'edittingPointsList'
				),
				FillerView (),
				HGridView ([
					FillerView (),
					CLabelView ('New color'),
					ComboView (self.colorNode, Colors),
					FillerView ()
				]),
				FillerView (),
				HGridView ([
					FillerView (),
					ButtonView (self.doOkNode, 'OK'),
					ButtonView (self.doCancelNode, 'Cancel')
				])
			]),
			'Edit points',
			fixedSize = True,
			key = 'editPointsDialog'
		)
		
	def defineActions (self):
		def doOk ():
			points = deepcopy (self.main.pointsNode.old)
			
			for selectedPoint in self.projectionDialog.selectedPointsNode.new:
				for point in points:
					if point == selectedPoint:
						point [3] = self.colorNode.new
						
			self.main.pointsNode.follow (points)
			
			self.getView () .exit ()
		
		self.doOkNode.action = doOk

		self.doCancelNode.action = self.getView (). exit