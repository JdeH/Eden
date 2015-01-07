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
import copy as cp

from ..node import *
from ..store import *

from kivy.logger import Logger

def setDebugExtra (self, debug):
	return
	if debug:
		Logger.setLevel (logging.ERROR)
	else:
		Logger.setLevel (logging.CRITICAL)
		
Application.setDebugExtra = setDebugExtra
application.debug = False

mainViewStoreFileName = 'views.store'
mainViewStore = Store ()
currentViewStore = CallableValue (mainViewStore)	# All applicable views will add themselves to currentViewStore ()

import kivy
kivy.require('1.8.0')

splitterGripSize = 2 * 4	# Always choose even, since it will be halved to achieve right item width when used in list header

class MainSizer:
	def __init__ (self):
		currentViewStore () .name (mainViewStoreFileName)
		currentViewStore () .add (self)
		
	def load (self):
		currentViewStore () .load (silent = True)	# Only main sizer can be loaded this early, don't show failure of all the rest that will be loaded later
		
		if hasattr (self, 'state'):	# Maybe there wasn't a state file yet
			global kivy
			kivy.config.Config.set ( 'graphics', 'width', self.state [0]) 
			kivy.config.Config.set ( 'graphics', 'height', self.state [1])
		
	def save (self):
		self.state = application.mainView.widget.size [:]
		currentViewStore () .save ()
		
mainSizer = MainSizer ()
mainSizer.load ()	# First call, only load mainSizer state, rest loaded with second call
		
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.checkbox import CheckBox
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.splitter import Splitter
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.treeview import TreeView as KivyTreeView, TreeViewNode, TreeViewLabel
from kivy.uix.listview import ListView as KivyListView, ListItemLabel, ListItemButton, CompositeListItem
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.adapters.dictadapter import ListAdapter
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

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
application.listSelectionJitterTime = 0.3

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
			
class ViewBase (object): 
	def __init__ (self, enabledNode = None, key = None):

		self.enabledNode = getNode (enabledNode)
		self.pointerIsInside = False
		self.pointerWasInside = self.pointerIsInside
		self.containsFocus = False
		self.containedFocus = self.containsFocus
		self.hasFocus = False
		self.hadFocus = self.hasFocus
		self.key = key
		self.touchArgs = None
			
	# Widget creation, enabling and event binding
	
	def getWidget (self, rootView):
		if hasattr (self, 'widget'):
			return self.widget
		else:
			return self.createWidget (rootView)
			
	def evaluateTaps (self, *args):
		if self.touchArgs [1] .is_triple_tap:
			self.pointerDown3 ()
		elif self.touchArgs [1] .is_double_tap:
			self.pointerDown2 ()
		else:
			self.pointerDown1 ()
			
	def createWidget (self, rootView):
		self.rootView = rootView
		self.bareCreateWidget ()
		
		application.mainView.widget.bind (on_resize_font = lambda *args: self.resizeFont ())
		application.mainView.widget.bind (on_change_font_scale = lambda *args: self.resizeFont ())
		
		def bareWriteEnabled ():
			self.widget.disabled = not self.enabledNode.new
	
		if self.enabledNode:
			self.enabledLink = Link (self.enabledNode, None, bareWriteEnabled)
			self.enabledLink.write ()
		
		def updatePointerPosition (pointerPosition):
			if isinstance (self, WindowViewBase):
				application.oldPointerPosition = application.pointerPosition
				application.pointerPosition = pointerPosition
				
			self.pointerIsInside = self.widget.collide_point (*self.widget.to_parent (*self.widget.to_widget (*application.pointerPosition)))
			if self.pointerIsInside != self.pointerWasInside:
				self.pointerWasInside = self.pointerIsInside
				if self.pointerIsInside:
					self.pointerEnter ()
				else:
					self.pointerLeave ()
				
			self.pointerMove ()
			
		def touchDown (*args):
			if application.mainView.rootViews [-1] != self.rootView:
				return
				
			application.oldPointerIsDown = application.pointerIsDown
			application.pointerIsDown = True
			application.pointerWentDownPosition = application.pointerPosition
			
			self.touchArgs = args
			
			Clock.unschedule (self.evaluateTaps)
			Clock.schedule_once (self.evaluateTaps, 0.5)
			
			self.pointerDown ()
			
			if hasattr (self.widget, 'focus') and self.widget.focus and not self.pointerIsInside:
				self.widget.focus = False
			
		self.widget.bind (on_touch_down = touchDown)
		
		def touchUp (*args):
			if application.mainView.rootViews [-1] != self.rootView:
				return

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
			
		self.widget.bind (on_touch_up = touchUp)
					
		def mousePos (*args):	
			if application.mainView.rootViews [-1] != self.rootView:
				return

			if not application.pointerIsDown:	# If the pointer is down, touchMove will take over
				updatePointerPosition (args [1])
				
		Window.bind (mouse_pos = mousePos)
				
		def touchMove (*args):	# Only called if pointer is down
			if application.mainView.rootViews [-1] != self.rootView:
				return		
		
			updatePointerPosition (args [1] .pos)
			if application.dragObject.dragging:
				application.dragObject.move ()
			else:	
				if hasattr (self, 'dragLink') and application.dragObject.armedForDrag and application.pointerIsDown and xDistance (application.pointerPosition, application.pointerWentDownPosition) > application.dragDistance:
					self.pointerStartDrag ()
					
				#if self.pointerIsInside:
				#	application.setPointerLabel (self.hintGetter ())
				
		self.widget.bind (on_touch_move = touchMove)
								
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
		
	def pointerDown1 (self):	# Called for each widget
		pass
		
	def pointerDown2 (self):	# Called for each widget
		pass
		
	def pointerDown3 (self):	# Called for each widget
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
		self.widget = Label ()

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
	def __init__ (self, actionNode = None, captionNode = None, enabledNode = None):
		ViewBase.__init__ (self, enabledNode)
		self.actionNode = getNode (actionNode)
		self.captionNode = getNode (captionNode)
		
	def bareCreateWidget (self):
		self.widget = Button ()
		
		if self.actionNode:
			self.actionLink = Link (self.actionNode, lambda params: self.actionNode.change (self.actionNode.new, True), None)
			self.widget.on_press = self.actionLink.read
		
		if self.captionNode:
			self.captionLink = Link (self.captionNode, None, lambda: self.setText (self.captionNode.new))
			self.captionLink.write ()
			
originalOnTouchDown = CheckBox.on_touch_down
			
def patchedOnTouchDown (self, touch):	# Behave like a checkbox rather then like a radio button
	oldGroup = self.group
	self.group = None
	originalOnTouchDown (self, touch)
	self.group = oldGroup
				
CheckBox.on_touch_down = patchedOnTouchDown
			
class SwitchView (ViewBase):
	def __init__ (self, stateNode = None, captionNode = None, enabledNode = None, kind = 'check'):	# Kind can be 'check', 'radio' or 'toggle'.
		ViewBase.__init__ (self, enabledNode)
		self.stateNode = getNode (stateNode)
		self.captionNode = getNode (captionNode)
		self.kind = kind
	
	def bareCreateWidget (self):	
		if self.kind == 'toggle':
			self.widget = ToggleButton ()
						
			if self.stateNode:
				def bareReadState (params):
					self.stateNode.change (self.widget.state == 'down')
			
				def bareWriteState ():
					self.widget.state = 'down' if self.stateNode.new else 'normal'

				self.widget.bind (on_press = lambda *args: self.stateLink.read ())
			
			if self.captionNode:
				def bareWriteCaption ():
					self.widget.text = str (self.captionNode.new)
		else:
			self.widget = BoxLayout ()
			
			self.switch = CheckBox (group = self if self.kind == 'radio' else None, size_hint_x = 0.5)	# Never the same group, since logic is handled only by nodes
			self.widget.add_widget (self.switch)
				
			self.label = Label ()
			def setTextSize (*args):
				self.label.text_size = (self.label.width, self.label.text_size [1])
			self.label.bind (size = setTextSize)			
			self.widget.add_widget (self.label)
			
			if self.stateNode:
				def bareReadState (params):
					self.stateNode.change (self.switch.active)
			
				def bareWriteState ():
					self.switch.active = self.stateNode.new			
			
				self.switch.bind (on_touch_up = lambda *args: self.stateLink.read ())
				
			if self.captionNode:
				def bareWriteCaption ():
					self.label.text = str (self.captionNode.new)
		
		if self.stateNode:
			self.stateLink = Link (self.stateNode, bareReadState, bareWriteState)
			self.stateLink.write ()
			
		if self.captionNode:
			self.captionLink = Link (self.captionNode, None, bareWriteCaption)
			self.captionLink.write ()	 

	def resizeFont (self):
		if self.kind == 'toggle':
			ViewBase.resizeFont (self)
		else:
			ViewBase.resizeFont (self, self.label)
			
class TextView (ViewBase):
	def __init__ (self, valueNode = None, enabledNode = None, multiLine = False, autoCommit = False):
		ViewBase.__init__ (self, enabledNode)	
		self.valueNode = getNode (valueNode)
		self.multiLine = multiLine
		self.autoCommit = autoCommit
		
	def bareCreateWidget (self):
		self.widget = TextInput (multiline = self.multiLine)
		
		if self.valueNode:
			self.valueLink = Link (self.valueNode, lambda params: self.valueNode.change (str (self.widget.text)), lambda: self.setText (self.valueNode.new))
			self.valueLink.write ()
			
		self.widget.bind (on_text_validate = self.valueLink.read)
		
		if self.autoCommit:
			self.widget.bind (text = self.valueLink.read)

	def resizeFont (self):
		ViewBase.resizeFont (self)
		paddingY = application.mainView.getPaddingHeight ()
		self.widget.padding = (5, paddingY, 0, paddingY)
		
	def focusOut (self):
		self.valueLink.read ()
		
# <options> = OrderedDict ([<optionId>: <optionName>, ...])
# <selectedOption> = <optionId>
		
class DropDownView (ViewBase):
	def __init__ (self, optionsNode = None, selectedOptionIdNode = None, enabledNode = None):
		ViewBase.__init__ (self, enabledNode)
		
		self.optionsNode = getNode (optionsNode)
		self.selectedOptionIdNode = getNode (selectedOptionIdNode)
		
	def bareCreateWidget (self):
		self.dropDown = DropDown ()
		self.widget = Button ()
		self.widget.background_color = (0, 0, 1, 1)
		self.widget.bind (on_release = self.dropDown.open)
		
		def select (optionId):
			self.dropDown.select (self.optionsNode.new [optionId])
			self.widget.text = self.optionsNode.new [optionId]
			self.selectedOptionIdLink.read (optionId)
		
		def writeOptions (*arg):
			self.dropDown.clear_widgets ()
			self.buttons = {}
			for optionId in self.optionsNode.new:
				optionName = self.optionsNode.new [optionId]
				button = Button (
					text = optionName,
					size_hint_y = None,
				)
				
				def bindButton (optionId = optionId):
					button.bind (on_release = lambda *args: select (optionId))
					
				bindButton ()
				
				self.buttons [optionId] = button
				self.dropDown.add_widget (button)
				
			self.widget.text = self.optionsNode.new [self.selectedOptionIdNode.new]
			self.resizeFont ()
				
		self.optionsLink = Link (self.optionsNode, None, writeOptions)
		self.optionsLink.write ()
		
		def bareReadSelectedOptionId (params):
			self.selectedOptionIdNode.change (params [0])
			
		def bareWriteSelectedOptionId ():
			select (self.selectedOptionIdNode.new)
		
		self.selectedOptionIdLink = Link (self.selectedOptionIdNode, bareReadSelectedOptionId, bareWriteSelectedOptionId)
		self.selectedOptionIdLink.write ()
		
	def resizeFont (self):
		ViewBase.resizeFont (self)
		for optionId in self.optionsNode.new:
			button = self.buttons [optionId]
			button.height = application.mainView.getLineHeight ()
			ViewBase.resizeFont (self, button)
		
# <tree> = [<branch>, ...]
# <branch> = <item> | (<item>, <tree>)
		
class TreeView (ViewBase):

	# --- Constructor and widget creation method, like supported by all views
	
	def __init__ (
		self,
		rootNode = None,
		treeNode = None,
		pointedPathNode = None,
		selectedPathNode = None,
		actionNode = None,
		otherActionNode = None,
		enabledNode = None,
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
		self.actionNode = getNode (actionNode)
		self.otherActionNode = getNode (otherActionNode)
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
			lambda params: self.visibleTreeLink.writing or self.selectedPathNode.change (self.pathFromTreeViewNode (self.widget.get_node_at_pos (self.widget.to_parent (*self.widget.to_widget (*application.pointerPosition))))),
			bareWriteSelectedPath
		)
		# Leave self.selectedPathLink.writeBack == True to properly deal with rightclicks. Probably bug in WinForms, because not needed with ListView.
		self.selectedPathLink.write ()
					
		self.visiblePathNode = Node ([])			
		self.visiblePathNode.dependsOn ([self.interestingPathsNode], lambda: self.interestingPathsNode.new [1])
		self.visiblePathLink = Link (self.visiblePathNode, None, lambda: treeViewNodeFromPath (self.visiblePathNode.new) .EnsureVisible ())				
				
		self.createDragDropLinks (self.treeNode)
	
		# tweak (self) ...
		
	# Overriden methods

	def pointerDown (self): # Use this event rather than selected_node, because it is the only event already occurring at mouse down, so before a drag
		if self.pointerIsInside:
			self.selectedPathLink.read ()
			
	def pointerDown2 (self):
		if self.pointerIsInside and self.actionNode:
			self.actionNode.change (None, True)
	
	def pointerDown3 (self):
		if self.pointerIsInside and self.otherActionNode:
			self.otherActionNode.change (None, True)
			
	def pointerStartDrag (self):
		if self.pointerIsInside and self.selectedPathNode.new:
			application.dragObject.startDrag (dragView = self)
			
	def pointerMove (self):
		if self.pointerIsInside:	# Check, because get_node_at_pos is expensive
			self.pointedTreeViewNode = self.widget.get_node_at_pos (self.widget.to_parent (*self.widget.to_widget (*application.pointerPosition)))
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
		
class ListHeadWidget (ColoredLabel):
	def __init__ (self, **args):		
		ColoredLabel.__init__ (self, backgroundColor = (0, 0, 0.2, 1))
		self.listView = args ['listView']
		self.fieldIndex = args ['fieldIndex']
		self.max_lines = 1
		self.halign = 'center'
		self.extraWidth = splitterGripSize / 2 if self.fieldIndex in (0, len (self.listView.headerNode.new) - 1) else splitterGripSize
		self.listView.listHeadWidgets [self.fieldIndex] = self
				
		def onSize (*args):
			self.listView.adaptItemSizes (self.fieldIndex)
			self.text_size = (self.width, None)
						
		self.bind (size = onSize)
		
		def touchDown (*args):
			if self.collide_point (*self.to_parent (*self.to_widget (*application.pointerPosition))):
				self.listView.sortColumnNumberLink.read (self.fieldIndex)
				self.listView.scheduleReadPointedList (None)

		self.bind (on_touch_down = touchDown)
		
		def touchMove (*args):
			if self.collide_point (*self.to_parent (*self.to_widget (*application.pointerPosition))):
				self.listView.scheduleReadPointedList (None)

		self.bind (on_touch_move = touchMove)
			
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
		self.max_lines = 25
		self.halign = 'center'
		self.size_hint_x = None
		self.bind (size = self.onSize)

		application.mainView.resizeFontOfTarget (self)
		
		def touchDown (*args):	# Block deselection in case of double or triple tap or click
			if self.collide_point (*self.to_parent (*self.to_widget (*application.pointerPosition))):
				touchDownTime = args [1] .time_start
				result = self.is_selected and touchDownTime - self.listView.touchDownTime < application.listSelectionJitterTime
				self.listView.touchDownTime = touchDownTime
				return result
		
		self.bind (on_touch_down = touchDown)
			
		def onSelect (*args):
			if self.is_selected:
				self.listView.listAdapter.get_view (self.rowIndex) .select_from_child (self)
			else:
				self.listView.listAdapter.get_view (self.rowIndex) .deselect_from_child (self)
			self.listView.selectedListLink.read (self.rowIndex)
			self.listView.scheduleReadPointedList (self.rowIndex)
				
		self.bind (is_selected = onSelect)
				
		def touchMove (*args):
			if	(
				self.listView.pointerIsInside	# Since the items receive collisions also when the pointer is outside the listview, e.g. below it
				and
				self.collide_point (*self.to_parent (*self.to_widget (*application.pointerPosition)))
			):
				self.listView.scheduleReadPointedList (self.rowIndex)
				
		self.listView.widget.bind (on_touch_move = touchMove)
		
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
		
# <list> = [<item>, ...]
# <item> = <field> | [<field>, ...]

class ListWidget (KivyListView):
	def on_touch_up (self, *args):
		KivyListView.on_touch_up (self, *args)
		return False

	def on_touch_move (self, *args):
		KivyListView.on_touch_move (self, *args)
		return False

class ListView (ViewBase):
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
		actionNode = None,
		otherActionNode = None,
		enabledNode = None,
		transformer = None,
		hintGetter = None,
		sortColumnNumberNode = None,
		dragLabelGetter = None,
		dragValueGetter = None,
		dropLabelGetter = None,
		dropValueGetter = None,
		dragResultGetter = None,
		dropResultGetter = None,
		multiSelect = True,
		key = None,
		tweaker = None
	):
		ViewBase.__init__ (self, enabledNode)
	
		self.headerNode = getNode (headerNode)
		self.listNode = getNode (listNode, Node ([]))
		self.pointedListNode = getNode (pointedListNode, Node ([]))
		self.selectedListNode = getNode (selectedListNode, Node ([]))
		self.actionNode = getNode (actionNode)
		self.otherActionNode = getNode (otherActionNode)
		self.transformer = transformer
		self.hintGetter = hintGetter = getFunction (hintGetter, lambda: None)
		self.sortColumnNumberNode = getNode (sortColumnNumberNode, Node (0))
		self.dragLabelGetter = getFunction (dragLabelGetter, self.defaultDragLabelGetter)
		self.dragValueGetter = getFunction (dragValueGetter, self.defaultDragValueGetter)
		self.dragResultGetter = getFunction (dragResultGetter, self.defaultDragResultGetter)
		self.dropLabelGetter = getFunction (dropLabelGetter, self.defaultDropLabelGetter)
		self.dropValueGetter = getFunction (dropValueGetter, self.defaultDropValueGetter)
		self.dropResultGetter = getFunction (dropResultGetter, self.defaultDropResultGetter)
		self.multiSelect = multiSelect
		self.key = key
		self.tweaker = None
		
		self.listHeadWidgets = [None for header in self.headerNode.new]
		self.touchDownTime = -1		
				
	def bareCreateWidget (self):
		def rowBuilder (rowIndex, item):
			return {
				'text': 'aap',
				'size_hint_y': None,
				'height': application.mainView.getLineHeight (),
				'cls_dicts': [{
					'cls': ListItemWidget,
					'kwargs': {
						'text': str (item [index]),
						'listView': self,
						'fieldIndex': index,
						'rowIndex': rowIndex,
					}
				} for index in range (len (self.headerNode.new))]
			}
			
		self.listAdapter = ListAdapter (data = [], selection_mode = 'multiple' if self.multiSelect else 'single', args_converter = rowBuilder, cls = CompositeListItem, sorted_keys = [])
		
		self.widget = BoxLayout (orientation = 'vertical')
		self.headerWidget = BoxLayout (height = 25, size_hint_y = None)
		for index, head in enumerate (self.headerNode.new):
			listHeadWidget = ListHeadWidget (text = '', height = 25, size_hint_y = None, listView = self, fieldIndex = index)
			if index == len (self.headerNode.new) - 1:
				self.headerWidget.add_widget (listHeadWidget)
			else:
				splitter = Splitter (sizable_from = 'right', strip_size = splitterGripSize, height = 25, size_hint_y = None)
				splitter.add_widget (listHeadWidget)
				self.headerWidget.add_widget (splitter)
				
		self.widget.add_widget (self.headerWidget)
		self.kivyListView = ListWidget (adapter = self.listAdapter)
		self.widget.add_widget (self.kivyListView)
		
		def bareWriteHeader ():
			for index, listHeadWidget in enumerate (self.listHeadWidgets):
				prefix = ''
				if self.sortColumnNumberNode.touched:
					if self.sortColumnNumberNode.new == index + 1:
						prefix = '+ '
					elif self.sortColumnNumberNode.new == -index - 1:
						prefix = '- '
			
				listHeadWidget.text = prefix + self.headerNode.new [index]
		
		self.headerLink = Link (self.headerNode, None, bareWriteHeader)
		self.headerLink.write ()
		
		self.headerSortLink = Link (self.sortColumnNumberNode, None, bareWriteHeader)
		self.headerUnsortLink = Link (self.listNode, None, bareWriteHeader)
		
		def bareReadList (params):
			listToSort = self.listNode.new	# We're still before the change event, so don't use self.listNode.old	
			self.listNode.change (sortList (listToSort, self.sortColumnNumberNode.new), self.transformer)
		
		def bareWriteList ():
			data = (
				[self.transformer (item) for item in self.listNode.new]
			if self.transformer else
				self.listNode.new
			)
			
			if data and type (data [0]) != list:
				data = [[item] for item in data]
		
			self.listAdapter.data = data
			
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
		
	def pointerDown2 (self):
		if self.pointerIsInside and self.actionNode:
			self.actionNode.change (None, True)
	
	def pointerDown3 (self):
		if self.pointerIsInside and self.otherActionNode:
			self.otherActionNode.change (None, True)
		
	def pointerStartDrag (self):
		if self.kivyListView.collide_point (*self.kivyListView.to_parent (*self.kivyListView.to_widget (*application.pointerPosition))) and self.selectedListNode.new:
			application.dragObject.startDrag (dragView = self)	
		
	def pointerLeave (self):
		self.scheduleReadPointedList (None)
		
	def resizeFont (self):
		ViewBase.resizeFont (self)			
		
		for listHeadWidget in self.listHeadWidgets:
			listHeadWidget.parent.height = application.mainView.getLineHeight ()	# Sometimes a spliter, sometimes the headerWidget
			ViewBase.resizeFont (self, listHeadWidget)
			
		for itemIndex in range (len (self.listNode.new)):
			lineWidget = self.listAdapter.get_view (itemIndex)
			lineWidget.height = application.mainView.getLineHeight ()
			for fieldWidget in  lineWidget.children:
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
		rowHeight = self.height / float (self.nrOfRows)
		columnWidth = self.width / float (self.nrOfColumns)
		
		for taggedWidget in self.taggedWidgets:		
			taggedWidget [0] .y = int (self.height - (taggedWidget [1] + taggedWidget [2]) * rowHeight)
			taggedWidget [0] .height = int (taggedWidget [2] * rowHeight)

			taggedWidget [0] .x = int (taggedWidget [3] * columnWidth)
			taggedWidget [0] .width = int (taggedWidget [4] * columnWidth)
		
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
				self.widget.addChildWidget (element [0] .createWidget (self.rootView), rowIndex, row [1], columnIndex, element [1], element [0])
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

class SplitViewBase (ViewBase):
	def __init__ (self, childViews, sizableFrom, orientation):
		ViewBase.__init__ (self)
		self.childViews = childViews
		self.sizableFrom = sizableFrom
		self.orientation = orientation

	def bareCreateWidget (self):
		self.widget = BoxLayout (orientation = self.orientation)
		for index, childView in enumerate (self.childViews):
			if index == len (self.childViews) - 1:
				self.widget.add_widget (childView.createWidget (self.rootView))
			else:
				splitter = Splitter (sizable_from = self.sizableFrom, strip_size = splitterGripSize, min_size = 10, max_size = 10000)
				splitter.add_widget (childView.createWidget (self.rootView))				
				self.widget.add_widget (splitter)				
				
		currentViewStore () .add (self)
		
class HSplitView (SplitViewBase):
	def __init__ (self, childViews):
		SplitViewBase.__init__ (self, childViews, 'right', 'horizontal')
	
	def getState (self):
		return [childView.widget.parent.width / float (self.childViews [-1] .widget.width) for childView in self.childViews [:-1]]
		
	def setState (self, value):
		for index, childView in enumerate (self.childViews [:-1]):
			childView.widget.parent.size_hint_x = value [index]

	state = property (getState, setState)
		
class VSplitView (SplitViewBase):
	def __init__ (self, childViews):
		SplitViewBase.__init__ (self, childViews, 'bottom', 'vertical')
		
	def getState (self):
		return [childView.widget.parent.height / float (self.childViews [-1] .widget.height) for childView in self.childViews [:-1]]
		
	def setState (self, value):
		for index, childView in enumerate (self.childViews [:-1]):
			childView.widget.parent.size_hint_y = value [index]

	state = property (getState, setState)
		
class TabbedView (ViewBase):
	def __init__ (self, pageViews, tabsNode, indexNode = None):
		ViewBase.__init__ (self)
		self.pageViews = pageViews
		self.tabsNode = getNode (tabsNode)
		self.indexNode = Node (0) if indexNode == None else getNode (indexNode)
		self.indexNode.addException (lambda value: value < 0 or value >= len (self.pageViews) or not self.pageWidgets [value], Objection, 'Tab index out of range')
		self.pageWidgets = []
		
	def bareCreateWidget (self):
		self.widget = TabbedPanel (do_default_tab = False)
		self.widget.background_color = (0, 0, 0, 1)
		
		with self.widget.canvas.before:
			Color (0.15, 0.15, 0.15, 1)
			self.rectangle = Rectangle (pos = self.widget.pos, size = self.widget.size)
				
		def onSize (*args):
			self.rectangle.size = self.widget.size
						
		self.widget.bind (size = onSize)

		def onPos (*args):
			self.rectangle.pos = self.widget.pos
	
		self.widget.bind (pos = onPos)
		
		def bareReadIndex (params):
			if not application.initializing:
				for index, pageWidget in enumerate (self.pageWidgets):
					if pageWidget == self.widget.current_tab:
						self.indexNode.change (index)
						break
			
		def bareWriteIndex ():
			self.widget.switch_to (self.pageWidgets [self.indexNode.new])
		
		self.indexLink = Link (self.indexNode, bareReadIndex, bareWriteIndex)
		Clock.schedule_once (lambda *args: self.indexLink.write ())
		Clock.schedule_once (lambda *args: self.widget.bind (current_tab = lambda *args: self.indexLink.read ()))
		
		def bareWriteTabs ():
			self.widget.clear_tabs ()
			self.pageWidgets = []
			
			firstIndex = -1
			for index, (tab, pageView) in enumerate (zip (self.tabsNode.new, self.pageViews)):	# So if tab == '', page is hidden
				if tab:
					if firstIndex == -1:
						firstIndex = index
					self.pageWidgets.append (TabbedPanelHeader (text = tab, content = pageView.getWidget (self.rootView)))
					self.widget.add_widget (self.pageWidgets [-1])
				else:
					self.pageWidgets.append (None)
					
			try:
				bareWriteIndex ()	# Restore current page
			except:	# Current page, adapt index to page, -1 if there are no pages
				self.indexNode.follow (firstIndex)
				
			self.resizeFont ()
			
		self.tabsLink = Link (self.tabsNode, None, bareWriteTabs)
		self.tabsLink.write ()
		
	def resizeFont (self):			
		Clock.schedule_once (self.adaptTabWidth, 1)	# This hack should really not be necessary

		for tabbedPanelHeader in self.pageWidgets:
			ViewBase.resizeFont (self, tabbedPanelHeader)

	def adaptTabWidth (self, *args):
		self.widget.tab_width = self.widget.width / (len (self.pageWidgets) + 0.5)
			
class WindowViewBase (ViewBase):
	def __init__ (
		self,
		clientView,
		captionNode,
		closeNode
	):
		ViewBase.__init__ (self)
		self.clientView = clientView
		self.captionNode = getNode (captionNode)
		self.closeNode = getNode (closeNode)
		
	def bareCreateWidget (self):
		self.createOuterWidget ()
		
		self.innerWidget  = RelativeLayout ()
		self.widget.add_widget (self.innerWidget)
		
		self.clientWidget = self.clientView.createWidget (self.rootView)
		self.innerWidget.add_widget (self.clientWidget)
		
		self.pointerLabelSurface = FloatLayout (size_hint = (1, 1))
		self.innerWidget.add_widget (self.pointerLabelSurface)
										
		def setCaption ():
			self.titleWidget.title = ('[DESIGN MODE] ' if application.designMode else '') + str (self.captionNode.new)
		
		self.captionLink = Link (
			self.captionNode,
			None,
			setCaption
		)
		self.captionLink.write ()
		
class ModalView (WindowViewBase):
	def __init__ (
		self,
		clientView = None,
		captionNode = 'Eden ModalView',
		closeNode = None,
		relativeSize = (1, 1)
	):
		WindowViewBase.__init__ (self, clientView, captionNode, closeNode)
		self.relativeSize = relativeSize
		
	def createOuterWidget (self):
		def adaptSize (*args):
			self.widget.height = application.mainView.widget.height + 15
			self.widget.width = application.mainView.widget.width + 25

		self.widget = Popup (size_hint = self.relativeSize, auto_dismiss = False)
		self.titleWidget = self.widget
		adaptSize ()
		application.mainView.widget.bind (size = adaptSize)
		
		self.widget.bind (on_open = application.mainView.dispatchResizeFont)
		self.widget.bind (on_open = lambda *args: application.mainView.pushRootView (self))
		self.widget.bind (on_dismiss = lambda *args: application.mainView.popRootView ())	
		
		if self.closeNode:
			self.closeNode.addAction (self.widget.dismiss)	# Don't use a link, since closing can't be rolled back
			
	def execute (self):
		self.getWidget (self)
		self.widget.open ()
		
	def resizeFont (self):
		ViewBase.resizeFont (self)
		self.widget.title_size = application.mainView.getFontSize ()
				
class MainView (WindowViewBase, App):	# App must be last, unclear why
	def __init__ (
		self,
		clientView = None,
		captionNode = 'Eden MainView',
		closeNode = None,
		fontScale = 1,
	):
		WindowViewBase.__init__ (self, clientView, captionNode, closeNode)
		App.__init__ (self)
		self.fontScale = fontScale
		
		application.mainView = self
		self.rootViews = [self]
		self.pointerLabelVisible = False
		
		def movePointerLabel ():
			widget = self.rootViews [-1] .pointerLabelSurface
			self.pointerLabel.pos = widget.to_parent (*widget.to_widget (*application.pointerPosition))
				
		application.movePointerLabel = movePointerLabel
		
		def setPointerLabel (text = None):
			if text is None:
				self.rootViews [-1] .pointerLabelSurface.remove_widget (self.pointerLabel)
				self.pointerLabelVisible = False
				self.pointerLabelText = ''
			else:
				self.pointerLabel.text = text
				if not self.pointerLabelVisible:
					self.rootViews [-1] .pointerLabelSurface.add_widget (self.pointerLabel)
					self.pointerLabelVisible = True
					
		application.setPointerLabel = setPointerLabel
		
	def pushRootView (self, rootView):
		self.rootViews.append (rootView)
	
	def popRootView (self):
		self.rootViews.pop ()
		
	def createOuterWidget (self):
		self.widget = FloatLayout ()
		self.titleWidget = self
		
		self.widget.__class__.on_resize_font = lambda *args: None
		self.widget.register_event_type ('on_resize_font')		
		self.widget.bind (size = self.dispatchResizeFont)		
									
		if self.closeNode:
			self.closeNode.addAction (self.stop)	# Don't use a link, since closing can't be rolled back

	def dispatchResizeFont (self, *args):
		self.widget.dispatch ('on_resize_font', args)

	def getFontNorm (self):
		return self.fontScale * float (min (self.widget.height, self.widget.width))

	def getFontSize (self):
		return self.getFontNorm () / 60
		
	def getLineHeight (self):
		return int (application.mainView.getFontNorm () / 30)
		
	def getPaddingHeight (self):
		return int (application.mainView.getFontNorm () / 120)
				
	def resizeFont (self):
		ViewBase.resizeFont (self, self.pointerLabel)

	def resizeFontOfTarget (self, widget):
		newFontSize = self.getFontSize ()
		if hasattr (widget, 'font_size') and not widget.font_size == newFontSize:
			widget.font_size = newFontSize
			
	def build (self):
		self.createWidget (self)
		self.pointerLabel = Label (size_hint = (None, None), size = (1, 1), color = (1, 1, 0, 1),)
		application.dragObject = DragObject ()	# Needs self.pointerLabelSurface and self.pointerLabel
		return self.widget
		
	def on_start (self):
		mainSizer.load ()
		
	def execute (self):
		application.initializing = False
		self.run ()
		mainSizer.save ()
