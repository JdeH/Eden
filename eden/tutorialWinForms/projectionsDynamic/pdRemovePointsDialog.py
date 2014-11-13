# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# removePointsDialog.py

from eden import *

from pdBase import *

class RemovePointsDialog (Module):
	def __init__ (self, projectionDialog):
		self.projectionDialog = projectionDialog
		self.main = projectionDialog.main
		Module.__init__ (self)
		
	def defineNodes (self):
		self.doOkNode = Node (None)
		self.doCancelNode = Node (None)

	def defineViews (self):
		return ModalView (
			VGridView ([
				LLabelView ('Points to be removed'),
				ListView (
					self.projectionDialog.selectedPointsNode,
					PointColumnLabels,
					key = 'removalPointsList'
				),
				FillerView (),
				HGridView ([
					FillerView (),
					ButtonView (self.doOkNode, 'OK'),
					ButtonView (self.doCancelNode, 'Cancel')
				])
			]),
			'Remove points',
			fixedSize = True,
			key = 'removePointsDialog'
		)
		
	def defineActions (self):
		def doOk ():
			self.main.pointsNode.follow (shrinkList (
				deepcopy (self.main.pointsNode.old),
				self.projectionDialog.selectedPointsNode.old
			))
			self.getView () .exit ()
		
		self.doOkNode.action = doOk

		self.doCancelNode.action = self.getView (). exit