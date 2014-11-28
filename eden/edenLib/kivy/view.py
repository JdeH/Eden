# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
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
from kivy.uix.splitter import Splitter
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.treeview import TreeView as KivyTreeView, TreeViewNode, TreeViewLabel
from kivy.uix.listview import ListView as KivyListView, ListItemLabel, ListItemButton, CompositeListItem
from kivy.uix.scrollview import ScrollView
from kivy.adapters.dictadapter import ListAdapter
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

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

application.dragDistance = 15
application.dragFixDistance = 60
application.dragFixTime = 1
application.dragResetTime = 6

application.pointedListItemSettleTime = 0.3

def xDistance (position0, position1):
	return abs (position1 [0] - position0 [0])
	
def yDistance (position0, position1):
	return abs (position1 [1] - position0 [1])

def blockDistance (position0, position1):
	return xDistance (position0, position1) + yDistance (position0, position1) 
	
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
		
		application.mainView.widget.bind (size = lambda *args: self.resizeFont ())
		
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
			
			if hasattr (self.widget, 'focus') and self.widget.focus and not self.pointerIsInside:
				self.widget.focus = False
			
		application.mainView.widget.bind (on_touch_down = touchDown)
		
		def touchUp (*args):
			application.oldPointerIsDown = application.pointerIsDown
			application.pointerIsDown = False
			application.pointerWentUpPosition = application.pointerPosition
			application.dragObject.armedForDrag = True
			self.pointerUp ()
	
			if self.pointerIsInside:
				if hasattr (self, 'dropLink'):
					if application.dragObject.dragging:
						application.dragObject.dropView = self
						self.dropLink.read ()	# Should be first, not only because of error handling
						application.dragObject.dragView.dragLink.read ()	# Should be last
						application.dragObject.reset ()	
			
		application.mainView.widget.bind (on_touch_up = touchUp)
					
		def mousePos (*args):	
			if not application.pointerIsDown:	# If the pointer is down, touchMove will take over
				updatePointerPosition (args [1])

		Window.bind (mouse_pos = mousePos)
				
		def touchMove (*args):	# Only called if pointer is down
			updatePointerPosition (args [1] .pos)
			if application.dragObject.dragging:
				application.dragObject.move ()
			else:
				if application.dragObject.armedForDrag and application.pointerIsDown and xDistance (application.pointerPosition, application.pointerWentDownPosition) > application.dragDistance:
					self.pointerStartDrag ()
					
				#if self.pointerIsInside:
				#	application.setPointerLabel (self.hintGetter ())
				
		application.mainView.widget.bind (on_touch_move = touchMove)
								
		if hasattr (self.widget, 'focus'):
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
					
			self.widget.bind (focus = focus)
			
		return self.widget
		
	def createDragDropLinks (self, mainDataNode):
		def fallibleDropResultGetter ():
			self.dropResultOk = False
			result = mainDataNode.new
			
			try:
				result = self.dropResultGetter ()
				self.dropResultOk = True
				
			except Refusal as refusal:
				handleNotification (refusal)
				
			except Exception as exception:
				handleNotification (Objection (exMessage (exception), report = exReport (exception)))
				
			return result	
							
		self.dropLink = Link (mainDataNode, lambda params: mainDataNode.change (fallibleDropResultGetter ()), None)

		def fallibleDragResultGetter ():
			result = mainDataNode.new
			
			if application.dragObject.dropView.dropResultOk:
				try:
					result = self.dragResultGetter ()

				except Refusal as refusal:
					handleNotification (refusal)
					
				except Exception as exception:
					handleNotification (Objection (exMessage (exception), report = exReport (exception)))
					
			return result
					
		self.dragLink = Link (mainDataNode, lambda params: mainDataNode.change (fallibleDragResultGetter ()), None)		
				
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
		
	def resizeFont (self, widget = None):
		if widget:
			targetWidget = widget
		else:
			targetWidget = self.widget
			
		application.mainView.resizeFontOfTarget (targetWidget)
		
	# Utility methods
		
	def setText (self, text):
		self.widget.text = str (text)
		
class EmptyView (ViewBase):
	def bareCreateWidget (self):
		self.widget = Label (text = 'Empty')

class ColoredLabel (Label):
	def __init__ (self, **args):		
		Label.__init__ (self, **args)
		
		if 'backgroundColor' in args.keys ():
			self.backgroundColor = args ['backgroundColor']
		else:
			self.backgroundColor = (0, 0, 0, 1)
		
		with self.canvas.before:
			Color (*self.backgroundColor)
			self.rectangle = Rectangle (pos = self.pos, size = self.size)
				
		def onSize (*args):
			self.rectangle.size = self.size
						
		self.bind (size = onSize)

		def onPos (*args):
			self.rectangle.pos = self.pos
	
		self.bind (pos = onPos)
		
class LabelView (ViewBase):
	def __init__ (self, captionNode = None, enabledNode = None):
		ViewBase.__init__ (self, enabledNode)	
		self.captionNode = getNode (captionNode)
		
	def bareCreateWidget (self):
		self.widget = ColoredLabel ()
		
		if self.captionNode:
			self.link = Link (self.captionNode, None, lambda: self.setText (self.captionNode.new))
			self.link.write ()

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
		hintGetter = None,
		expansionLevelNode = None,
		dragLabelGetter = None,
		dragValueGetter = None,
		dropLabelGetter = None,
		dropValueGetter = None,
		dragResultGetter = None,
		dropResultGetter = None,
		key = None,
		tweaker = None
	):
		ViewBase.__init__ (self, enabledNode)
	
		self.rootNode = getNode (rootNode, Node ('...'))
		self.treeNode = getNode (treeNode, Node ([]))
		self.pointedPathNode = getNode (pointedPathNode, Node ([]))
		self.selectedPathNode = getNode (selectedPathNode, Node ([]))
		self.contextMenuView = contextMenuView
		self.transformer = transformer
		self.expansionLevelNode = getNode (expansionLevelNode)
		self.hintGetter = getFunction (hintGetter, lambda: None)
		self.dragLabelGetter = getFunction (dragLabelGetter, self.defaultDragLabelGetter)
		self.dragValueGetter = getFunction (dragValueGetter, self.defaultDragValueGetter)
		self.dragResultGetter = getFunction (dragResultGetter, self.defaultDragResultGetter)
		self.dropLabelGetter = getFunction (dropLabelGetter, self.defaultDropLabelGetter)
		self.dropValueGetter = getFunction (dropValueGetter, self.defaultDropValueGetter)
		self.dropResultGetter = getFunction (dropResultGetter, self.defaultDropResultGetter)
		self.key = key,
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
			self.resizeFont ()
			
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
				
		self.createDragDropLinks (self.treeNode)
	
		# tweak (self) ...
		
	# Overriden methods

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
										
	def resizeFont (self):
		ViewBase.resizeFont (self)
		for node in self.widget.iterate_all_nodes ():
			ViewBase.resizeFont (self, node)

	# --- Default drag and drop methods

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
		
		rootBranch	= self.treeNode.new [0]
		
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
		
# <list> = [<item>, ...]
# <item> = <field> | [<field>, ...]

class ListHeadWidget (ColoredLabel):
	def __init__ (self, **args):		
		ColoredLabel.__init__ (self, backgroundColor = (0, 0, 0.2, 1))
		self.listView = args ['listView']
		self.fieldIndex = args ['fieldIndex']
		self.max_lines = 1
		self.halign = 'center'
		self.extraWidth = self.listView.headerStripWidth / 2 if self.fieldIndex in (0, len (self.listView.headerNode.new) - 1) else self.listView.headerStripWidth
		self.listView.listHeadWidgets [self.fieldIndex] = self
				
		def onSize (*args):
			self.listView.adaptItemSizes (self.fieldIndex)
			self.text_size = (self.width, None)
						
		self.bind (size = onSize)
		
		def touchDown (*args):
			if self.collide_point (*application.pointerPosition):
				self.listView.sortColumnNumberLink.read (self.fieldIndex)

		self.bind (on_touch_down = touchDown)
		
		def touchMove (*args):
			if self.collide_point (*self.to_parent (*self.to_widget (*application.pointerPosition))):
				self.listView.scheduleReadPointedList (None)

		application.mainView.widget.bind (on_touch_move = touchMove)
			
	def getGrossWidth (self):
		return self.width + self.extraWidth	
			
class ListItemWidget (ListItemButton):	
	def __init__ (self, **args):
		self.listView = args ['listView']
		self.fieldIndex = args ['fieldIndex']
		self.rowIndex = args ['rowIndex']
		self.deselected_color = (0.3, 0.3, 0.3, 1) if self.rowIndex % 2 else (0.5, 0.5, 0.5, 1)
		self.selected_color = (0.9, 0.9, 0.9, 1)
		self.background_down = self.background_normal
		ListItemButton.__init__ (self, **args)
		self.max_lines = 1
		self.halign = 'center'
		self.size_hint_x = None
		self.bind (size = self.onSize)

		application.mainView.resizeFontOfTarget (self)
			
		def onSelect (*args):
			if self.is_selected:
				self.listView.listAdapter.get_view (self.rowIndex) .select_from_child (self)
			else:
				self.listView.listAdapter.get_view (self.rowIndex) .deselect_from_child (self)
			self.listView.selectedListLink.read (self.rowIndex)
		
		self.bind (is_selected = onSelect)
		
		def touchMove (*args):				
			if	(
				self.listView.pointerIsInside	# Since the items receive collisions also when the pointer is outside the listview, e.g. below it
				and
				self.collide_point (*self.to_parent (*self.to_widget (*application.pointerPosition)))
			):
				self.listView.scheduleReadPointedList (self.rowIndex)
				
		application.mainView.widget.bind (on_touch_move = touchMove)
						
	def onSize (self, *args):	# Member, since it is also called by ListView.adaptItemSizes, initiated by a head resize
		self.width = self.listView.listHeadWidgets [self.fieldIndex] .getGrossWidth ()
		self.text_size = (self.width, None)

	def isSelected (self):	# ... Ugly hack, since is_selected doesn't do the job in Kivy 1.8
		return self.background_color == self.selected_color
		
	def select (self, *args):
		if not application.dragObject.dragging:
			ListItemButton.select (self, *args)
	
	def deselect (self, *args):
		if not application.dragObject.dragging:
			ListItemButton.deselect (self, *args)
			
	def select_from_composite(self, *args):
		if not application.dragObject.dragging:
			ListItemButton.select_from_composite (self, *args)

	def deselect_from_composite(self, *args):
		if not application.dragObject.dragging:	
			ListItemButton.deselect_from_composite (self, *args)
		
class ListView (ViewBase):
	Neutral, Next, Previous, Up, Down, Insert, Delete, Undo = range (8)

	currentListView = None
	pointedItemIndex = None
	def readPointedList (*args):
		ListView.currentListView.pointedListLink.read ()
	
	# --- Constructor and widget creation method, like supported by all views

	def __init__ (
		self,
		headerNode = None,
		listNode = None,
		pointedListNode = None,
		selectedListNode = None,
		enabledNode = None,
		contextMenuView = None,
		transformer = None,
		hintGetter = None,
		multiSelectNode = None,
		sortColumnNumberNode = None,
		pointedColumnIndexNode = None,
		clickedColumnIndexNode = None,
		visibleColumnsNode = None,
		editViews = None,
		exitStateNode = None,
		actionStateNode = None,
		dragLabelGetter = None,
		dragValueGetter = None,
		dropLabelGetter = None,
		dropValueGetter = None,
		dragResultGetter = None,
		dropResultGetter = None,
		key = None,
		tweaker = None
	):
		ViewBase.__init__ (self, enabledNode)
	
		self.headerNode = getNode (headerNode)
		self.listNode = getNode (listNode, Node ([]))
		self.pointedListNode = getNode (pointedListNode, Node ([]))
		self.selectedListNode = getNode (selectedListNode, Node ([]))
		self.contextMenuView = contextMenuView
		self.transformer = transformer
		self.hintGetter = hintGetter = getFunction (hintGetter, lambda: None)
		self.multiSelectNode = getNode (multiSelectNode, Node (False))
		self.sortColumnNumberNode = getNode (sortColumnNumberNode, Node (1))
		self.pointedColumnIndexNode = getNode (pointedColumnIndexNode, Node (0))
		self.clickedColumnIndexNode = getNode (clickedColumnIndexNode, Node (0))
		self.visibleColumnsNode = getNode (visibleColumnsNode, Node (0)),
		self.editViews = editViews,
		self.exitStateNode = getNode (exitStateNode, Node ('???'))
		self.actionStateNode = getNode (actionStateNode, Node ('???'))
		self.dragLabelGetter = getFunction (dragLabelGetter, self.defaultDragLabelGetter)
		self.dragValueGetter = getFunction (dragValueGetter, self.defaultDragValueGetter)
		self.dragResultGetter = getFunction (dragResultGetter, self.defaultDragResultGetter)
		self.dropLabelGetter = getFunction (dropLabelGetter, self.defaultDropLabelGetter)
		self.dropValueGetter = getFunction (dropValueGetter, self.defaultDropValueGetter)
		self.dropResultGetter = getFunction (dropResultGetter, self.defaultDropResultGetter)
		self.key = key
		self.tweaker = None
		
		self.headerStripWidth = 2 * 4	# Always choose even, since it will be halved to achieve right item width
		self.listHeadWidgets = [None for header in self.headerNode.new]
		
	def bareCreateWidget (self):
		def rowBuilder (rowIndex, item):
			return {
				'text': 'aap',
				'size_hint_y': None,
				'height': 25,
				'cls_dicts': [{
					'cls': ListItemWidget,
					'kwargs': {
						'text': item [index],
						'listView': self,
						'fieldIndex': index,
						'rowIndex': rowIndex,
					}
				} for index in range (len (self.headerNode.new))]
			}
			
		self.listAdapter = ListAdapter (data = [], selection_mode = 'multiple', args_converter = rowBuilder, cls = CompositeListItem, sorted_keys = [])
		
		self.widget = BoxLayout (orientation = 'vertical')
		self.headerWidget = BoxLayout (height = 25, size_hint_y = None)
		for index, head in enumerate (self.headerNode.new):
			listHeadWidget = ListHeadWidget (text = '', height = 25, size_hint_y = None, listView = self, fieldIndex = index)
			if index == len (self.headerNode.new) - 1:
				self.headerWidget.add_widget (listHeadWidget)
			else:
				splitter = Splitter (sizable_from = 'right', strip_size = self.headerStripWidth, height = 25, size_hint_y = None)
				splitter.add_widget (listHeadWidget)
				self.headerWidget.add_widget (splitter)
				
		self.widget.add_widget (self.headerWidget)
		self.kivyListView = KivyListView (adapter = self.listAdapter)
		self.widget.add_widget (self.kivyListView)
		
		def bareWriteHeader ():
			for index, listHeadWidget in enumerate (self.listHeadWidgets):
				listHeadWidget.text = self.headerNode.new [index]
		
		self.headerLink = Link (self.headerNode, None, bareWriteHeader)
		self.headerLink.write ()
				
		def bareReadList (params):
			listToSort = self.listNode.new	# We're still before the change event, so don't use self.listNode.old	
			self.listNode.change (sortList (listToSort, self.sortColumnNumberNode.new), self.transformer)
		
		def bareWriteList ():
			self.listAdapter.data = self.listNode.new if self.listNode.new and self.listNode.new [0] .__class__ == list else [[item] for item in self.listNode.new]
			self.listView.populate ()
			
		self.listLink = Link (self.listNode, bareReadList, bareWriteList)
		self.listLink.write ()
		
		if not hasattr (self.selectedListNode, 'getter'):
			self.selectedListNode.dependsOn ([self.listNode], self.interestingItemList)
			
		def bareReadSelectedList (params):
			if application.dragObject.dragging:
				self.selectedListLink.write ()
			else:
				if not self.listLink.writing:
					selectedList = []
					for itemIndex, item in enumerate (self.listNode.new):
						for fieldWidget in self.listAdapter.get_view (itemIndex) .children:
							if fieldWidget.isSelected ():
								selectedList.append (item [:] if item.__class__ == list else item)	# Item isn't always a list, can also be a single field!
								break	# Add only once, if any view of a row is selected
					self.selectedListNode.change (selectedList)
				
		def bareWriteSelectedList ():
			for itemIndex, item in enumerate (self.listNode.new):
				if item in self.selectedListNode.new:
					self.listAdapter.get_view (itemIndex) .select_from_child (None)
				else:
					self.listAdapter.get_view (itemIndex) .deselect_from_child (None)
			
		self.selectedListLink = Link (self.listNode, bareReadSelectedList, bareWriteSelectedList)
		self.selectedListLink.writeBack = False
		
		def bareReadPointedList (params):
			self.pointedListNode.change ([self.listNode.new [ListView.pointedItemIndex]] if ListView.pointedItemIndex != None else [])
		
		def bareWritePointedList ():
			for itemIndex, item in enumerate (self.listNode.new):
				if item in self.pointedListNode.old:
					for fieldWidget in self.listAdapter.get_view (itemIndex) .children:
						fieldWidget.bold = False
					
				if item in self.pointedListNode.new:
					for fieldWidget in self.listAdapter.get_view (itemIndex) .children:
						fieldWidget.bold = True

		self.pointedListLink = Link (self.pointedListNode, bareReadPointedList, bareWritePointedList)
		
		def bareReadSortColumnNumber (params):
			self.sortColumnNumberNode.change (
				(
					-self.sortColumnNumberNode.new
				) if params [0] == abs (self.sortColumnNumberNode.new) - 1 else (
					params [0] + 1
				)
			)
			listToSort = self.listNode.new	# We're still before the change event, so don't use self.listNode.old	
			self.listNode.follow (sortList (listToSort, self.sortColumnNumberNode.new), self.transformer)
		
		self.sortColumnNumberLink = Link (self.sortColumnNumberNode, bareReadSortColumnNumber, None)
		
		self.createDragDropLinks (self.listNode)


	def scheduleReadPointedList (self, pointedItemIndex):	
		Clock.unschedule (ListView.readPointedList)	# No problem if nothing to unschedule

		ListView.currentListView = self
		ListView.pointedItemIndex = pointedItemIndex
		
		if ListView.pointedItemIndex == None: # Prevent forgetting to make pointedList empty if listView is left (else a newer schedule may override it)
			Clock.schedule_once (ListView.readPointedList)
		else:
			Clock.schedule_once (ListView.readPointedList, application.pointedListItemSettleTime)
		
	# Overridden methods
	
	def pointerUp (self):
		ViewBase.pointerUp (self)
		
	def pointerStartDrag (self):
		if self.pointerIsInside and self.selectedListNode.new:
			application.dragObject.startDrag (dragView = self)
		
	def pointerLeave (self):
		self.scheduleReadPointedList (None)
		
	def resizeFont (self):
		ViewBase.resizeFont (self)

		for listHeadWidget in self.listHeadWidgets:
			ViewBase.resizeFont (self, listHeadWidget)
			
		for itemIndex in range (len (self.listNode.new)):
			for fieldWidget in self.listAdapter.get_view (itemIndex) .children:
				ViewBase.resizeFont (self, fieldWidget)
		
	# Default drag and drop methods
		
	def defaultDragLabelGetter (self):
		dragValue = self.dragValueGetter ()
		bareDragLabel = '{0} items'.format (len (dragValue))
				
		if application.dragObject.dragFixed:
			return '+ {0}'.format (bareDragLabel)
		else:
			return bareDragLabel
			
	def defaultDragValueGetter (self):
		return self.selectedListNode.new
		
	def defaultDragResultGetter (self):
		return (
				shrinkList (self.listNode.new, self.selectedListNode.new)
			if not application.dragObject.dragFixed and not application.dragObject.reflexive else
				self.listNode.new
		)
		
	def defaultDropLabelGetter (self):
		bareDropLabel = application.dragObject.dragView.dragLabelGetter ()
		
		if application.dragObject.dropFixed:
			return '{0} v'.format (bareDropLabel)
		
	def defaultDropValueGetter (self):
		return application.dragObject.dragView.dragValueGetter ()
		
	def defaultDropResultGetter (self):
		return (
				reorderList (self.listNode.new, self.pointedListNode.new, self.dropValueGetter ())
			if application.dragObject.reflexive else
				insertList (self.listNode.new, self.pointedListNode.new, self.dropValueGetter ())
		)
		
	# Miscellaneous methods
	
	def adaptItemSizes (self, fieldIndex):
		for itemIndex in range (len (self.listNode.new)):
			fieldWidget = self.listAdapter.get_view (itemIndex) .children [-(fieldIndex + 1)]
			fieldWidget.onSize ()		

	def interestingItemList (self):							# Order n rather than n**2  !!! Tidyup!!!
		if application.initializing:
			return []
	
#		if self.edited:
#			self.edited = False
#			return [self.listNode.new [self.editRowIndex]]
			
		indexNew = len (self.listNode.new) - 1
		growth = indexNew - (len (self.listNode.old) - 1)
		
		if growth == 0:														# If same size
			if sorted (self.listNode.new) == sorted (self.listNode.old):		# If contain same elements
				return self.selectedListNode.old
			else:															# Both insertion and removal have taken place, no sensible selection possible
				return []
		else:
		
			# Look for a difference between the lists, that have unequal length

			try:
				while self.listNode.new [indexNew] == self.listNode.old [indexNew - growth]:
					indexNew -= 1				
			except IndexError:
				pass	

			# When here, a difference has been found, including exhaustion of exactly one of both lists
		
			if indexNew == -1:									# If index points at fictional sentry at index -1
				return []										#	Don't return sentry, since it is fictional...
			else:												# If index points at a real item
				return [self.listNode.new [indexNew]]			#	Inserted item or item just above the ones deleted
			
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
		rowHeight = int (self.height / self.nrOfRows)
		remainingHeight = self.height - self.nrOfRows * rowHeight
	
		columnWidth = int (self.width / self.nrOfColumns)
		remainingWidth = self.width - self.nrOfColumns * columnWidth
		
		for taggedWidget in self.taggedWidgets:
			heightCorrection = remainingHeight if taggedWidget [1] + taggedWidget [2] == self.nrOfRows else 0
			widthCorrection = remainingWidth if taggedWidget [3] + taggedWidget [4] == self.nrOfColumns else 0
		
			taggedWidget [0] .y = self.height - (taggedWidget [1] + taggedWidget [2]) * rowHeight - heightCorrection
			taggedWidget [0] .height = taggedWidget [2] * rowHeight + heightCorrection

			taggedWidget [0] .x = taggedWidget [3] * columnWidth
			taggedWidget [0] .width = taggedWidget [4] * columnWidth + widthCorrection
		
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
		fontScaleNode = 1,
	):
		App.__init__ (self)
		ViewBase.__init__ (self)
		self.clientView = clientView
		self.captionNode = getNode (captionNode)
		self.fontScaleNode = getNode (fontScaleNode)
		application.mainView = self
		self.pointerLabelVisible = False
		self.transientWidgetDict = {}
		
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
		
		# self.fontScaleLink = Link (self.fontScaleNode, None, traverseResizeFont)
		
	def resizeFont (self):
		ViewBase.resizeFont (self, self.pointerLabel)

	def resizeFontOfTarget (self, widget):
		newFontSize = self.fontScaleNode.new * self.widget.width / 70
		if hasattr (widget, 'font_size') and not widget.font_size == newFontSize:
			widget.font_size = newFontSize
			
	def build (self):
		return self.createWidget ()
		
	def execute (self):
		application.initializing = False
		self.run ()
