# Copyright (C) 2005, 2006 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.


import datetime
import logging

from kivy.logger import Logger
# Logger.setLevel(logging.ERROR)

import kivy
kivy.require('1.8.0') # replace with your current kivy version !

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.treeview import TreeView as KivyTreeView, TreeViewNode, TreeViewLabel
from kivy.clock import Clock

from eden.edenLib.node import *
from eden.edenLib.store import *

application.designMode = False
application.initializing = True
application.focusedView = None

application.pointerPosition = (-1, -1)
application.oldPointerPosition = application.pointerPosition

application.pointerIsDown = False
application.pointerWasDown = application.pointerIsDown
application.pointerWentDownPosition = (-1, -1)
application.pointerWentUpPosition = (-1, -1)

application.dragDistance = 6
application.dragFixDistance = 60
application.dragFixTime = 1
application.dragResetTime = 6

def blockDistance (position0, position1):
	return abs (position1 [0] - position0 [0]) + abs (position1 [1] - position0 [1])

class DragObject:
	def __init__ (self):
		self.reset ()
		self.armedForDrag = True
		self.armedForDrop = False
	
	def startDrag (self, dragView):
		self.dragging = True
		self.armedForDrop = False
		self.armedForDrag = False	# Will be set at touchUp
		Clock.schedule_once (self.reset, application.dragResetTime)
		
		self.dragView = dragView
		self.dragPosition = application.pointerPosition
		
		dragLabel = self.dragView.dragLabelGetter ()
		if not dragLabel is None:
			application.setPointerLabel (dragLabel)
						
		Clock.schedule_once (self.fixDrag, application.dragFixTime)
			
	def restartDrop (self, dropView):
		self.dropView = dropView
		self.dropPosition = application.pointerPosition
		
		dropLabel = self.dropView.dropLabelGetter ()
		if not dropLabel is None:
			application.setPointerLabel (dropLabel)
			
		Clock.unschedule (self.fixDrop)
		Clock.schedule_once (self.fixDrop, application.dragFixTime)
		
	def move (self):
		if self.dragging:
			if blockDistance (self.dragPosition, application.pointerPosition) > application.dragFixDistance:
				self.armedForDrop = True
				
			application.movePointerLabel ()
			
	def reset (self, *args):	# Clock requires args
		self.dragging = False		
		
		Clock.unschedule (self.reset)
		Clock.unschedule (self.fixDrag)
		Clock.unschedule (self.fixDrop)
		
		application.setPointerLabel ()
		
		self.dragView = None
		self.dragFixed = False
		
		self.dragLabel = None
		self.dragObject = None
		
		self.dropView = None
		self.dropFixed = False
			
	reflexive = property (lambda self: self.dragView is self.dropView)
	
	def fixDrag (self, *args):	# Clock requires args
		if blockDistance (self.dragPosition, application.pointerPosition) < application.dragFixDistance:
			self.dragFixed = True
			
			dragLabel = self.dragView.dragLabelGetter ()
			if not dragLabel is None:
				application.setPointerLabel (dragLabel)

			
	def fixDrop (self, *args):	# Clock requires args	
			self.dropFixed = True
			
			dropLabel = self.dropView.dropLabelGetter ()
			if not dropLabel is None:
				application.setPointerLabel (dropLabel)
			
class ViewBase: 
	def __init__ (self, enabledNode = None):
	
		self.enabledNode = getNode (enabledNode)
		self.pointerIsInside = False
		self.pointerWasInside = self.pointerIsInside
		self.containsFocus = False
		self.containedFocus = self.containsFocus
		self.hasFocus = False
		self.hadFocus = self.hasFocus
			
	# Widget creation, enabling and event binding
	
	def createWidget (self):
		self.bareCreateWidget ()

		def bareWriteEnabled ():
			self.widget.disabled = not self.enabledNode.new
	
		if self.enabledNode:
			self.enabledLink = Link (self.enabledNode, None, bareWriteEnabled)
			self.enabledLink.write ()
		
		def updatePointerPosition (pointerPosition):
			if self == application.mainView:
				application.oldPointerPosition = application.pointerPosition
				application.pointerPosition = pointerPosition
				
			self.pointerIsInside = self.widget.collide_point (*application.pointerPosition)
			if self.pointerIsInside != self.pointerWasInside:
				self.pointerWasInside = self.pointerIsInside
				if self.pointerIsInside:
					self.pointerEnter ()
				else:
					self.pointerLeave ()
					
			self.pointerMove ()

		def touchDown (*args):
			application.oldPointerIsDown = application.pointerIsDown
			application.pointerIsDown = True
			application.pointerWentDownPosition = application.pointerPosition
			self.pointerDown ()
			
		self.widget.bind (on_touch_down = touchDown)
		
		def touchUp (*args):
			application.oldPointerIsDown = application.pointerIsDown
			application.pointerIsDown = False
			application.pointerWentUpPosition = application.pointerPosition
			application.dragObject.armedForDrag = True
			self.pointerUp ()
			
		self.widget.bind (on_touch_up = touchUp)
					
		def mousePos (*args):	
			if not application.pointerIsDown:	# If the pointer is down, touchMove will take over
				updatePointerPosition (args [1])

		Window.bind (mouse_pos = mousePos)
				
		def touchMove (*args):	# Only called if pointer is down
			updatePointerPosition (args [1] .pos)
			if application.dragObject.dragging:
				application.dragObject.move ()
			else:
				if application.dragObject.armedForDrag and application.pointerIsDown and blockDistance (application.pointerPosition, application.pointerWentDownPosition) > application.dragDistance:
					self.pointerStartDrag ()
					
				#if self.pointerIsInside:
				#	application.setPointerLabel (self.hintGetter ())
				
		self.widget.bind (on_touch_move = touchMove)
				
		def focus (*args):
			if self.widget.focus:
				application.focusedView = self
				self.hadFocus = self.hasFocus
				self.hasFocus = True
				self.focusIn ()
			else:
				if application.focusedView == self:	# Be safe, may already point to new focus
					application.focusedView = None
					
				self.hadFocus = self.hasFocus
				self.hasFocus = False
				self.focusOut ()
		
		if hasattr (self.widget, 'focus'):
			self.widget.bind (focus = focus)
			
		return self.widget
				
	# Methods to override
	
	def pointerMove (self):	# Called for each widget and any button status
		pass
		
	def pointerDown (self):	# Called for each widget
		pass
		
	def pointerUp (self):	# Called for each widget
		pass
				
	def pointerEnter (self):	# Called for any button status
		pass
		
	def pointerLeave (self):	# Called for any button status
		pass
		
	def pointerStartDrag (self):	# Called for each widget
		pass
		
	def focusIn (self):
		pass
		
	def focusOut (self):
		pass
		
	def dragLabelGetter (self):
		return None
		
	def dragValueGetter (self):
		return None
		
	def dragResultGetter (self):
		return None
		
	def dropLabelGetter (self):
		return None
		
	def dropValueGetter (self):
		return None
		
	def dropResultGetter (self):
		return None

	def adaptFontSize (self):
		pass
		
	# Utility methods
		
	def setText (self, text):
		self.widget.text = str (text)
		
class EmptyView (ViewBase):
	def bareCreateWidget (self):
		self.widget = Label (text = 'Empty')
		
	def adaptFontSize (self):
		pass

class LabelView (ViewBase):
	def __init__ (self, captionNode = None, enabledNode = None):
		ViewBase.__init__ (self, enabledNode)	
		self.captionNode = getNode (captionNode)
		
	def bareCreateWidget (self):
		self.widget = Label ()
		
		if self.captionNode:
			self.link = Link (self.captionNode, None, lambda: self.setText (self.captionNode.new))
			self.link.write ()
		
	def adaptFontSize (self):
		self.widget.font_size = self.widget.height / 1.5

class ButtonView (ViewBase):
	def __init__ (self, actionNode = None, captionNode = None):
		ViewBase.__init__ (self)
		self.actionNode = getNode (actionNode)
		self.captionNode = getNode (captionNode)
		
	def bareCreateWidget (self):
		self.widget = Button ()
		
		if self.actionNode:
			self.actionLink = Link (self.actionNode, lambda params: self.actionNode.change (None, True), None)
			self.widget.on_press = self.actionLink.read
		
		if self.captionNode:
			self.captionLink = Link (self.captionNode, None, lambda: self.setText (self.captionNode.new))
			self.captionLink.write ()		
		
	def adaptFontSize (self):
		self.widget.font_size = self.widget.height / 1.5 
		
class TextView (ViewBase):
	def __init__ (self, valueNode = None, enabledNode = None):
		ViewBase.__init__ (self, enabledNode)	
		self.valueNode = getNode (valueNode)
		
	def bareCreateWidget (self):
		self.widget = TextInput ()
		
		if self.valueNode:
			self.valueLink = Link (self.valueNode, lambda params: self.valueNode.change (str (self.widget.text)), lambda: self.setText (self.valueNode.new))
			self.valueLink.write ()
			
	def focusOut (self):
		self.valueLink.read ()
		
# <tree> = [<branch>, ...]
# <branch> = <item> | (<item>, <tree>)
		
class TreeView (ViewBase):	# Views a <tree>

	# --- Constructor and widget creation method, like supported by all views
	
	def __init__ (
		self,
		rootNode = None,
		treeNode = None,
		pointedPathNode = None,
		selectedPathNode = None,
		enabledNode = None,
		contextMenuView = None,
		transformer = None,
		expansionLevel = None,
		hintGetter = None,
		dragLabelGetter = None,
		dragValueGetter = None,
		dropLabelGetter = None,
		dropValueGetter = None,
		dragResultGetter = None,
		dropResultGetter = None,
		tweaker = None
	):
		ViewBase.__init__ (self, enabledNode)
	
		self.rootNode = getNode (rootNode, Node ('...'))
		self.treeNode = getNode (treeNode, Node ([]))
		self.pointedPathNode = getNode (pointedPathNode, Node ([]))
		self.selectedPathNode = getNode (selectedPathNode, Node ([]))
		self.contextMenuView = contextMenuView
		self.transformer = transformer
		self.expansionLevelNode = getNode (expansionLevel)
		self.hintGetter = getFunction (hintGetter, lambda: None)
		self.dragLabelGetter = getFunction (dragLabelGetter, self.defaultDragLabelGetter)
		self.dragValueGetter = getFunction (dragValueGetter, self.defaultDragValueGetter)
		self.dragResultGetter = getFunction (dragResultGetter, self.defaultDragResultGetter)
		self.dropLabelGetter = getFunction (dropLabelGetter, self.defaultDropLabelGetter)
		self.dropValueGetter = getFunction (dropValueGetter, self.defaultDropValueGetter)
		self.dropResultGetter = getFunction (dropResultGetter, self.defaultDropResultGetter)
		self.tweaker = tweaker
		
		self.pointedTreeViewNode = None
		self.oldPointedTreeViewNode = self.pointedTreeViewNode
	
	def bareCreateWidget (self):
		self.widget = KivyTreeView ()
		#self.widget.HideSelection = False
		#self.widget.AllowDrop = True
		
		def bareWriteRoot ():
			self.widget.root.text = str (self.rootNode.new)
			
		def keepRootNodeOpen (*args):
			if not self.widget.root.is_open:
				self.widget.toggle_node (self.widget.root)
			
		self.widget.root.bind (is_open = keepRootNodeOpen)
		
		self.rootLink = Link (self.rootNode, None, bareWriteRoot) 
		self.rootLink.write ()
		
		self.visibleTreeNode = Node ([])
		if self.expansionLevelNode:
			self.visibleTreeNode.dependsOn ([self.treeNode, self.expansionLevelNode], lambda: None)
		else:
			self.visibleTreeNode.dependsOn ([self.treeNode], lambda: None)
			
		def bareWriteVisibleTree ():
			def fillExpansionDictionary (parentWidgetNode, hashPath, expansionDictionary):		
				for treeViewNode in parentWidgetNode.nodes:
					if self.transformer:
						newHashPath = hashPath + (treeViewNode.tag, )
					else:
						newHashPath = hashPath + (treeViewNode.text, )	# Store as string since its used in View rather than Node
						
					expansionDictionary [newHashPath] = treeViewNode.is_open
					fillExpansionDictionary (treeViewNode, newHashPath, expansionDictionary)
			
			def clearTree ():
				for treeViewNode in list (self.widget.iterate_all_nodes ()):
					self.widget.remove_node (treeViewNode)
			
			def writeTree (tree, parentWidgetNode, hashPath, expansionDictionary):
				for branch in tree:
					widgetNode = TreeViewLabel ()
					
					item = branch [0] if branch.__class__ == tuple else branch
					itemText = str (item)
						
					if self.transformer:
						newHashPath = hashPath + (item, )
					else:
						newHashPath = hashPath + (itemText, )

					if self.transformer:
						widgetNode.tag = item
						widgetNode.text = self.transformer (item)
					else:
						widgetNode.text = itemText
							
					try:
						if self.expansionLevelNode:
							if self.expansionLevelNode.new > len (hashPath) + 1:
								if not widgetNode.is_open:
									self.widget.toggle_node (widgetNode)
						elif expansionDictionary [newHashPath]:
							if not widgetNode.is_open:
								self.widget.toggle_node (widgetNode)
					except KeyError:	# Is ok, expansionDictionary does not contain the newest node
						pass
					
					self.widget.add_node (widgetNode, parentWidgetNode)
						
					if branch.__class__ == tuple:
						writeTree (branch [1], widgetNode, newHashPath, expansionDictionary)

			expansionDictionary = {}
			fillExpansionDictionary (self.widget.root, (), expansionDictionary)
			clearTree ()
			writeTree (self.treeNode.new, None, (), expansionDictionary)			
			
		self.visibleTreeLink = Link (self.visibleTreeNode, None, bareWriteVisibleTree) 
		self.visibleTreeLink.write ()		

		self.interestingPathsNode = Node ([])
		self.interestingPathsNode.dependsOn ([self.treeNode], lambda: self.interestingPaths ())		

		def treeViewNodeFromPath (path):
			treeViewNodes = self.widget.root.nodes
			treeViewNode = None
			
			for item in path:
				for treeViewNode in treeViewNodes:
					candidateItem = self.itemFromTreeViewNode (treeViewNode)
					
					if candidateItem == item:
						treeViewNodes = treeViewNode.nodes
						break
						
			return treeViewNode		
		
		if not hasattr (self.selectedPathNode, 'getter'):
			self.selectedPathNode.dependsOn ([self.interestingPathsNode], lambda: self.interestingPathsNode.new [0])
			
		def bareWriteSelectedPath ():
			treeViewNode = treeViewNodeFromPath (self.selectedPathNode.new)
			if treeViewNode is None:
				bareWriteVisibleTree ()	# Currently the only way to deselect all
			else:
				self.widget.select_node (treeViewNodeFromPath (self.selectedPathNode.new))
			
		self.selectedPathLink = Link (
			self.selectedPathNode,
			lambda params: self.visibleTreeLink.writing or self.selectedPathNode.change (self.pathFromTreeViewNode (self.widget.get_node_at_pos (application.pointerPosition))),
			bareWriteSelectedPath
		)
		# Leave self.selectedPathLink.writeBack == True to properly deal with rightclicks. Probably bug in WinForms, because not needed with ListView.
		self.selectedPathLink.write ()
					
		self.visiblePathNode = Node ([])			
		self.visiblePathNode.dependsOn ([self.interestingPathsNode], lambda: self.interestingPathsNode.new [1])
		self.visiblePathLink = Link (self.visiblePathNode, None, lambda: treeViewNodeFromPath (self.visiblePathNode.new) .EnsureVisible ())				
#		if self.contextMenuView:
#			self.widget.ContextMenuStrip = self.contextMenuView.createWidget ()
#			self.widget.MouseUp += lambda sender, event: event.Button != Forms.MouseButtons.Right or sender.ContextMenuStrip.Show (sender, event.Location)
					
		def fallibleDropResultGetter ():
			self.dropResultOk = False
			result = self.treeNode.new
			
			try:
				result = self.dropResultGetter ()
				self.dropResultOk = True
				
			except Refusal as refusal:
				handleNotification (refusal)
				
			except Exception as exception:
				handleNotification (Objection (exMessage (exception), report = exReport (exception)))
				
			return result	
				
					
		self.dropLink = Link (self.treeNode, lambda params: self.treeNode.change (fallibleDropResultGetter ()), None)

		def fallibleDragResultGetter ():
			result = self.treeNode.new
			
			if application.dragObject.dropView.dropResultOk:
				try:
					result = self.dragResultGetter ()

				except Refusal as refusal:
					handleNotification (refusal)
					
				except Exception as exception:
					handleNotification (Objection (exMessage (exception), report = exReport (exception)))
					
			return result
					
		self.dragLink = Link (self.treeNode, lambda params: self.treeNode.change (fallibleDragResultGetter ()), None)

		# tweak (self) ...

	# Overriden pointer methods

	def pointerDown (self): # Use this event rather than selected_node, because it is the only event already occurring at mouse down, so before a drag
		if self.pointerIsInside:
			self.selectedPathLink.read ()
			
	def pointerStartDrag (self):
		if self.pointerIsInside and self.selectedPathNode.new:
			application.dragObject.startDrag (dragView = self)
			
	def pointerMove (self):
		if self.pointerIsInside:	# Check, because get_node_at_pos is expensive
			self.pointedTreeViewNode = self.widget.get_node_at_pos (application.pointerPosition)
		else:
			self.pointedTreeViewNode = None
			
		if self.pointedTreeViewNode != self.oldPointedTreeViewNode:
			if self.pointedTreeViewNode:
				self.pointedTreeViewNode.bold = True
			
			if self.oldPointedTreeViewNode:
				self.oldPointedTreeViewNode.bold = False
			
			self.pointedPathNode.change (self.pathFromTreeViewNode (self.pointedTreeViewNode))
			
			if application.dragObject.dragging and application.dragObject.armedForDrop:
				application.dragObject.restartDrop (dropView = self)
			
			self.oldPointedTreeViewNode = self.pointedTreeViewNode
						
	def pointerUp (self):
		if self.pointerIsInside:
			if application.dragObject.dragging:			
				application.dragObject.dropView = self
				self.dropLink.read ()	# Should be first, not only because of error handling
				application.dragObject.dragView.dragLink.read ()	# Should be last
				application.dragObject.reset ()

	# --- Drag and drop support methods

	def defaultDragLabelGetter (self):
		branch = self.dragValueGetter () [1]
		item = branch [0] if branch.__class__ == tuple else branch
		bareDragLabel = (
				self.transformer (item)
			if self.transformer	else
				str (item)
		)
		
		if application.dragObject.dragFixed:
			return '+ {0}'.format (bareDragLabel)
		else:
			return bareDragLabel
			
	def defaultDragValueGetter (self):
		return self.selectedPathNode.new, cloneBranch (self.treeNode.new, self.selectedPathNode.new)
		
	def defaultDragResultGetter (self):
		return (
				removeBranch (self.treeNode.new, self.selectedPathNode.new)
			if not application.dragObject.dragFixed and not application.dragObject.reflexive else
				self.treeNode.new
		)
		
	def defaultDropLabelGetter (self):
		bareDropLabel = application.dragObject.dragView.dragLabelGetter ()
		
		if application.dragObject.dropFixed:
			return '{0} v'.format (bareDropLabel)
		
	def defaultDropValueGetter (self):
		return application.dragObject.dragView.dragValueGetter ()
		
	def defaultDropResultGetter (self):
		dropValue = self.dropValueGetter ()
		return (
				editTree (self.treeNode.new, dropValue [0], self.pointedPathNode.new, application.dragObject.dropFixed, application.dragObject.dragFixed)
			if application.dragObject.reflexive else
				insertBranch (self.treeNode.new, self.pointedPathNode.new, dropValue [1], application.dragObject.dropFixed)
		)
		
	# --- Miscellaneous methods
			
	def assignSelectedTreeViewNode (self, treeViewNode):
		self.widget.SelectedNode = treeViewNode		
				
	def itemFromTreeViewNode (self, treeViewNode):
		if not treeViewNode:
			return None
		
		rootBranch  = self.treeNode.new [0]
		
		if self.transformer:
			return treeViewNode.tag
		elif rootBranch.__class__ == tuple:
			return getAsTarget (treeViewNode.text, rootBranch [0] .__class__)
		else:
			return getAsTarget (treeViewNode.text, rootBranch.__class__)
			
	def pathFromTreeViewNode (self, treeViewNode):
		path = []
		while not treeViewNode in (None, self.widget.root):
			path.insert (0, self.itemFromTreeViewNode (treeViewNode))
			treeViewNode = treeViewNode.parent_node
		return path	
		
	def interestingPaths (self):
		selectedPath = []
		visiblePath = []
		self.fillInterestingPaths (self.treeNode.new, self.treeNode.old, selectedPath, visiblePath, [True])
		return (selectedPath, visiblePath)

	def fillInterestingPaths (self, newTree, oldTree, selectedPath, visiblePath, select):
		newIndex = len (newTree) - 1
		oldIndex = len (oldTree) - 1
		
		growth = newIndex - oldIndex
		
		while newIndex >= 0 and oldIndex >= 0:
			newBranch = tupleFromBranch (newTree [newIndex])
			oldBranch = tupleFromBranch (oldTree [oldIndex])
			
			if newBranch [0] == oldBranch [0]:
				if self.fillInterestingPaths (newBranch [1], oldBranch [1], selectedPath, visiblePath, select):
					if select [0]:
						selectedPath.insert (0, newBranch [0])
					visiblePath.insert (0, newBranch [0])
					return True
			else:
				if growth <= 0:
					selectedPath.insert (0, newBranch [0])
				visiblePath.insert (0, newBranch [0])
				return True
			
			newIndex -= 1
			oldIndex -= 1
			
		if newIndex >= 0:
			visiblePath.insert (0, tupleFromBranch (newTree [newIndex]) [0])
			return True
		
		if oldIndex >= 0:
			select [0] = False
			return True
			
		return False		
				
class SpanLayout (RelativeLayout):
	def __init__ (self):
		RelativeLayout.__init__ (self)
		self.taggedWidgets = []
		self.nrOfRows = 0
		self.nrOfColumns = 0

	def addChildWidget (self, childWidget, rowIndex, rowSpan, columnIndex, columnSpan, view):
		self.add_widget (childWidget)
		self.taggedWidgets.append ((childWidget, rowIndex, rowSpan, columnIndex, columnSpan, view))
		self.nrOfRows = max (self.nrOfRows, rowIndex + rowSpan)
		self.nrOfColumns = max (self.nrOfColumns, columnIndex + columnSpan)
		
	def do_layout (self, *args):
		rowHeight = self.height / self.nrOfRows
		columnWidth = self.width / self.nrOfColumns
		
		for taggedWidget in self.taggedWidgets:
			taggedWidget [0] .y = self.height - (taggedWidget [1] + taggedWidget [2]) * rowHeight
			taggedWidget [0] .height = taggedWidget [2] * rowHeight
			taggedWidget [0] .x = taggedWidget [3] * columnWidth
			taggedWidget [0] .width = taggedWidget [4] * columnWidth
			taggedWidget [5] .adaptFontSize ()
		
class GridView (ViewBase):
	def __init__ (self, childViews):
		ViewBase.__init__ (self)
		
		self.rows = []
		for rowOrWeight in childViews:
			if isinstance (rowOrWeight, int):
				self.rows [-1][1] = rowOrWeight
			elif rowOrWeight:
				self.rows.append ([[], 1])
				for viewOrSpan in rowOrWeight:
					if isinstance (viewOrSpan, int):
						self.rows [-1][0][-1][1] = viewOrSpan				
					elif viewOrSpan:
						self.rows [-1][0] .append ([viewOrSpan, 1])
					else:
						self.rows [-1][0] .append ([EmptyView (), 1])
			else:
				self.rows.append ([[[EmptyView (), 1]], 0])
						
	def bareCreateWidget (self):
		self.widget = SpanLayout ()
		
		self.nrOfRowCells = 0
		self.nrOfColumnCells = 0
		rowIndex = 0
		for row in self.rows:
			columnIndex = 0
			for element in row [0]:
				self.widget.addChildWidget (element [0] .createWidget (), rowIndex, row [1], columnIndex, element [1], element [0])
				columnIndex += element [1]
				self.nrOfColumnCells = max (self.nrOfColumnCells, columnIndex)
				
			rowIndex += row [1]
				
			if row [1]:
				self.nrOfRowCells += rowIndex
			else:
				self.nrOfRowCells += rowIndex
		
class HGridView (GridView):
	def __init__ (self, childViews):
		GridView.__init__ (self, [childViews])
		
class VGridView (GridView):
	def __init__ (self, childViews):
		weightedRows = []
		for viewOrWeight in childViews:
			if isinstance (viewOrWeight, ViewBase):		
				weightedRows.append ([viewOrWeight])
			elif viewOrWeight is None:
				weightedRows.append ([])
			else:
				weightedRows.append (viewOrWeight)
		GridView.__init__ (self, weightedRows)
		
class MainView (App, ViewBase):
	def __init__ (
		self,
		clientView = None,
		captionNode = 'Eden',
	):
		App.__init__ (self)
		ViewBase.__init__ (self)
		self.clientView = clientView
		self.captionNode = getNode (captionNode)
		application.mainView = self
		self.pointerLabelVisible = False
		
		def movePointerLabel ():
			self.pointerLabel.pos = application.pointerPosition		
				
		application.movePointerLabel = movePointerLabel
		
		def setPointerLabel (text = None):
			if text is None:
				self.pointerLabelSurface.remove_widget (self.pointerLabel)
				self.pointerLabelVisible = False
				self.pointerLabelText = ''
			else:
				self.pointerLabel.text = text
				if not self.pointerLabelVisible:
					self.pointerLabelSurface.add_widget (self.pointerLabel)
					self.pointerLabelVisible = True
					
		application.setPointerLabel = setPointerLabel
		
	def bareCreateWidget (self):
		self.widget = FloatLayout ()
		
		self.widget.add_widget (self.clientView.createWidget ())
		
		self.pointerLabelSurface = FloatLayout (size_hint = (None, None))
		self.widget.add_widget (self.pointerLabelSurface)
		self.pointerLabel = Label (width = 1, height = 1, color = (1, 1, 0, 1),)
		
		application.dragObject = DragObject ()	# Needs self.pointerLabelSurface and self.pointerLabel
				
		def setTitle ():
			self.title = ('[DESIGN MODE] ' if application.designMode else '') + str (self.captionNode.new)
		
		self.captionLink = Link (
			self.captionNode,
			None,
			setTitle
		)
		self.captionLink.write ()
		
	def build (self):
		return self.createWidget ()
		
	def execute (self):
		self.run ()

	