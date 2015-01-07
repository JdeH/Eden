# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# aboutDialog.py

from org.qquick.eden import *

class AboutDialog (Module):
	def __init__ (self):
		Module.__init__ (self)
		
	def defineNodes (self):
		self.addNode (Node (None), 'openNode')
		self.addNode (Node (None), 'closeNode')
		
	def defineViews (self):
		return ModalView (
			ButtonView (captionNode = 'Eden modules demo app\nPress to dismiss', actionNode = self.closeNode),
			captionNode = 'About',
			closeNode = self.closeNode,
			relativeSize = (0.2, 0.3)
		)
		
	def defineActions (self):
		self.openNode.action = self.getView () .execute
		