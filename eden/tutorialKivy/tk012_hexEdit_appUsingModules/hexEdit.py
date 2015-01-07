# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# hexEdit.py

from org.qquick.eden import *

from fileDialog import *
from aboutDialog import *
from asciiPane import *
from hexPane import *

# Non-trivial Eden applications should be split into modules, this example shows how.
# Some nodes, by virtue of their dependencies on nodes in other modules, act as interface between modules.
# These nodes may be grouped together and labeled as (stable and thin) interface by a suitable comment.
# Interconnecting modules through this interface is not enforced, much like class interfaces are not enforced in Python.
#
# Each module consists of a fixed number possible of clauses, presumably in a fixed order:
#
#	defineModules	N.B. Each module may have submodules
#	defineNodes
#	defineDependencies
#	defineViews
#	defineActions
#
# Empty clauses may be omitted

# The dialog modules in this example have much in common.
# In a real world app they would inherit from a common ancestor.
# But in this example keeping things simple was considered more important.
# In general nodes and views mix well with "standard" OOP concepts.

class Main (Module):
	def defineModules (self):	# Modules are defined hierarchically, but are all made accessible flat as members of the global app object provided by Eden.
		self.addModule (FileDialog (moduleName = 'loadFileDialog', save = False))
		self.addModule (FileDialog (moduleName = 'saveFileDialog', save = True))
		self.addModule (AboutDialog ())
		self.addModule (HexPane ())	# Module name defaults to 'hexPane'
		self.addModule (AsciiPane ())
		
	def defineNodes (self):
		self.addNode (Node (None), 'openFileMenuNode')	# Accessible as self.fileNode
		self.addNode (Node (None), 'closeFileMenuNode')
		
		self.addNode (Node (None), 'openHelpMenuNode')
		self.addNode (Node (None), 'closeHelpMenuNode')
		
		self.addNode (Node (None), 'closeAppNode')
		
		self.addNode (Node (bytearray ('')), 'contentNode', app.nodeStore)	# Persistent
		
	def defineDependencies (self):
		def getContent ():
			try:
				if app.asciiPane.contentNode.triggered:
					return bytearray (app.asciiPane.contentNode.new)
				else:
					return bytearray.fromhex (app.hexPane.contentNode.new)
			except:	# Invalid ascii or hex, preserve old content
				return self.contentNode.old
	
		self.contentNode.dependsOn ([app.hexPane.contentNode, app.asciiPane.contentNode], getContent)
		
		self.closeFileMenuNode.dependsOn ([app.loadFileDialog.openNode, app.saveFileDialog.openNode])
		self.closeHelpMenuNode.dependsOn ([app.aboutDialog.openNode])
		
	def defineViews (self):
		self.fileMenuView = ModalView (
			VGridView ([
				ButtonView (captionNode = 'Load', actionNode = app.loadFileDialog.openNode),
				ButtonView (captionNode = 'Save', actionNode = app.saveFileDialog.openNode)
			]),
			captionNode = 'File',
			closeNode = self.closeFileMenuNode,
			relativeSize = (0.125, 0.15)
		)
	
		self.helpMenuView = ModalView (
			VGridView ([
				ButtonView (captionNode = 'About', actionNode = app.aboutDialog.openNode),
			]),
			captionNode = 'Help',
			closeNode = self.closeHelpMenuNode,
			relativeSize = (0.125, 0.11)
		)
	
		return MainView (	# The defineViews clause should return the module's View, if it has one.
			VGridView ([
				HGridView ([
					ButtonView (captionNode = 'File', actionNode = self.openFileMenuNode),
					ButtonView (captionNode = 'Help', actionNode = self.openHelpMenuNode),
					EmptyView (), 6
				]),
				HSplitView ([
					app.asciiPane.getView (),
					app.hexPane.getView ()
				]), 25
			]),
			captionNode = 'Editor (no need to save your file between edits, it\'s persistent even if you never gave it a name)'
		)
		
	def defineActions (self):
		self.openFileMenuNode.action = self.fileMenuView.execute
		self.openHelpMenuNode.action = self.helpMenuView.execute
		
# ====== PROGRAM ENTRYPOINT ======	

Main () .execute ()
		