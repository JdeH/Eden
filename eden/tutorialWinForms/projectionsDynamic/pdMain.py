# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# pdMain.py

from org.qquick.eden import *

from pdProjectionDialog import *

application.designMode = True

Colors = ['Black', 'White', 'Red', 'Green', 'Blue', 'Yellow', 'Orange', 'Purple']

class Main (Module):
	def __init__ (self):
		Module.__init__ (self, 'main', True)
		
	def defineNodes (self):
		self.pointsNode = Node ([])
		
		self.nrOfPointsNode = Node ()
		self.nrOfProjectionsNode = Node (0)
		
		self.doNewProjectionNode = Node (None)
		
	def defineDependencies (self):
		self.nrOfPointsNode.dependsOn ([self.pointsNode], lambda: len (self.pointsNode.new))
		
	def defineViews (self):
		return MainView (
			VGridView ([
				LLabelView ('All points'),
				ListView (
					self.pointsNode,
					PointColumnLabels,
					key = 'mainPointsList'
				),
				HGridView ([
					LLabelView ('Nr of points'),
					TextView (self.nrOfPointsNode)
				]),
				HGridView ([
					LLabelView ('Nr of projection views'),
					TextView (self.nrOfProjectionsNode)
				]),
				HGridView ([
					ButtonView (self.doNewProjectionNode, 'Open a new projection view')
				])
			]),
			'Dynamic instantiation of Node subnetworks',
			fixedSize = True,
			key = 'main'
		)

	def defineActions (self):
		def doNewProjection ():
			ProjectionDialog (self, projectionViewStore) .getView () .execute ()
			
		self.doNewProjectionNode.action = doNewProjection
				
# --- Entrypoint

main = Main ()

projectionViewStore = Store ()
projectionViewStore.name ('projectionViews.store')

nodeStore = Store ()
nodeStore.load ('nodes.store')

main.getView () .execute ()

nodeStore.save ()

projectionViewStore.save ()
		