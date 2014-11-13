# Copyright (C) 2005, 2006 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# pdProjectionDialog.py

from eden import *

from pdAddPointsDialog import *
from pdRemovePointsDialog import *
from pdEditPointsDialog import *

class ProjectionDialog (Module):
	def __init__ (self, main, viewStore):
		self.main = main
		main.nrOfProjectionsNode.follow (main.nrOfProjectionsNode.old + 1)
		
		currentViewStore.value = viewStore
		Module.__init__ (self, 'projectionDialog', True)
		viewStore.load ()
		
	def defineModules (self):
		self.addPointsDialog = self.addModule (AddPointsDialog (self))
		self.removePointsDialog = self.addModule (RemovePointsDialog (self))
		self.editPointsDialog = self.addModule (EditPointsDialog (self))
		
	def defineNodes (self):
		self.pointsNode = Node ()
		self.selectedPointsNode = Node ([])
		self.sortColumnNumberNode = Node (0)
	
		self.doAddPointsNode = Node (None)
		self.doRemovePointsNode = Node (None)
		self.doEditPointsNode = Node (None)
		
		self.doCloseNode = Node (None)
		self.doExitNode = Node (None)
				
	def defineDependencies (self):
		self.pointsNode.dependsOn (
			[self.main.pointsNode, self.sortColumnNumberNode],
			lambda: sortList (self.main.pointsNode.new, self.sortColumnNumberNode.new)
		)
		
	def defineViews (self):
		return ModelessView (
			VGridView ([
				LLabelView ('All points'),				
				HGridView ([
					ListView (
						self.pointsNode,
						PointColumnLabels,
						selectedListNode = self.selectedPointsNode,
						key = 'projectionPointsList',
						sortColumnNumberNode = self.sortColumnNumberNode
					),
					HExtensionView (), HExtensionView (),
					VGridView ([
						ButtonView (self.doAddPointsNode, 'Add', hint = 'Add a range of points'),
						ButtonView (self.doRemovePointsNode, 'Remove', hint = 'Remove the selected points'),
						ButtonView (self.doEditPointsNode, 'Edit', 'Edit the selected points'),
						StretchView (),
						ButtonView (self.doCloseNode, 'Close', 'Close this projection view')
					])
				])
			]),
			'ProjectionDialog',
			fixedSize = True,
			key = 'Projection view',
			exitActionNode = self.doExitNode
		)
		
	def defineActions (self):			
		self.doAddPointsNode.action = self.addPointsDialog.getView () .execute
		self.doRemovePointsNode.action = self.removePointsDialog.getView () .execute
		self.doEditPointsNode.action = self.editPointsDialog.getView () .execute
		self.doCloseNode.action = self.getView () .exit
		self.doExitNode.action = lambda: self.main.nrOfProjectionsNode.follow (self.main.nrOfProjectionsNode.old - 1)		
