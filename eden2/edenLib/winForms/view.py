# Copyright (C) 2005, 2006 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

from eden.edenLib.node import *
from eden.edenLib.store import *

import clr

clr.AddReference ('System')
clr.AddReference ('System.Drawing')
clr.AddReference ('System.Windows.Forms')

import System
from System import Drawing
from System.Windows import Forms
from System.Windows.Forms import Keys	# In a non .NET implementation the same identifiers should be defined as members of a Keys class

from string import *

mainViewStore = Store ()
currentViewStore = CallableValue (mainViewStore)	# All applicable views will add themselves to currentViewStore ()

application.designMode = False
application.initializing = True
application.focusedView = None

if hasattr (application, 'bitMapDirectories'):
	application.bitMapDirectories = getList (application.bitMapDirectories)

def shiftColor (color, red = 0, green = 0, blue = 0, alpha = 0):
	def clip (value):
		return min (max (value, 0), 255)

	colorNumber = color.ToArgb ()
			
	return Drawing.Color.FromArgb (
		clip ((colorNumber >> 24 & 255) + alpha),
		clip ((colorNumber >> 16 & 255) + red),
		clip ((colorNumber >> 8 & 255) + green),
		clip ((colorNumber & 255) + blue)
	)

HighBright = shiftColor (Drawing.SystemColors.Highlight, red = 128, green = 128, blue = 128)

class Clipboard:
	def read (self):
		try:
			return eval (Forms.Clipboard.GetText ())
		except:
			return Forms.Clipboard.GetText ()
			
	def write (self, data):
		Forms.Clipboard.SetText (fullString (data))
		
clipboard = Clipboard ()

class DropActions:
	Null = 0
	Move = 1
	Copy = 2
	Link = 3

class DragObject:
	def __init__ (self):
		self.clear ()
	
	def clear (self):
		self.value = None		
		self.sourceView = None
		self.targetView = None
		self.dropAction = None
		
	reflexive = property (lambda self: self.sourceView is self.targetView)
	imported = property (lambda self: self.sourceView is None)		
	exported = property (lambda self: self.targetView is None)
	modifiers = property (lambda self: ifExpr (self.keyState & 8, [Keys.Control], [])) 
			
dragObject = DragObject ()
		
def assignText (target, source):
	target.Text = source

def assignImage (target, source):
	target.Image = source

def assignTitle (target, source):
	target.Title = source
	
def getImage (stringOrImage):
	if stringOrImage.__class__ == str:
		for bitMapDirectory in application.bitMapDirectories:
			try:
				image = Drawing.Image.FromFile (bitMapDirectory + '/' + stringOrImage + '.bmp')
				break
			except IOError:
				pass
	else:
		image = stringOrImage
	
	try:
		image.MakeTransparent ()
	except:
		pass
		
	return image

def getIcon (stringOrIcon):
	if stringOrIcon.__class__ == str:
		for bitMapDirectory in application.bitMapDirectories:
			try:
				icon = Drawing.Icon (bitMapDirectory + '/' + stringOrIcon + '.ico')
				break
			except IOError:
				pass
	else:
		icon = stringOrIcon
			
	return icon

def getHint (hintGetter):
	try:
		return str (hintGetter ())
	except:
		return '???'

def tweak (view):
	if view.tweaker:
		view.tweaker (view)

class EnabledViewMix:
	def __init__ (self, enabled):
		self.enabledNode = getNode (enabled)
	
	def bareWriteEnabled (self):
		self.widget.Enabled = self.enabledNode.new
		
	def attachEnabledToWidget (self):
		if self.enabledNode:
			self.enabledLink = Link (self.enabledNode, None, self.bareWriteEnabled)
			self.enabledLink.write ()
			
class EditableViewMix:
	def __init__ (self, editable):
		self.editableNode = getNode (editable)
		
	def bareWriteEditable (self):
		self.widget.ReadOnly = not self.editableNode.new
		
	def attachEditableToWidget (self):
		if self.editableNode:
			self.editableLink = Link (self.editableNode, None, self.bareWriteEditable)
			self.editableLink.write ()
			
class HintedViewMix:
	def __init__ (self, hint):
		self.hintGetter = getFunction (hint)
		
	def attachHintedToWidget (self):
		if self.hintGetter:
			if isinstance (self.widget, Forms.Control):
				self.toolTip = Forms.ToolTip ()
				self.toolTip.ShowAlways = True
				self.widget.MouseEnter += self.updateControlHint
			else:
				self.widget.MouseEnter += self.updateStripElementHint

	def updateControlHint (self, sender, event):
		self.toolTip.Active = False
		self.toolTip.SetToolTip (self.widget, getHint (self.hintGetter))
		self.toolTip.Active = True
		
	def updateStripElementHint (self, sender, event):
		self.widget.ToolTipText = getHint (self.hintGetter)
			
class MultiSelectViewMix:
	def __init__ (self, multiSelect):
		self.multiSelectNode = getNode (multiSelect)
		
	def bareWriteMultiSelect (self):
		self.widget.MultiSelect = self.multiSelectNode.new
		
	def attachMultiSelectToWidget (self):
		if self.multiSelectNode:
			self.multiSelectLink = Link (self.multiSelectNode, None, self.bareWriteMultiSelect)
			self.multiSelectLink.write ()
			
class KeysViewMix:
	def __init__ (self, keysDownNode, keysUpNode, keyCharNode, keysHandled):
		self.keysDownNode = keysDownNode
		self.keysUpNode = keysUpNode
		self.keyCharNode = keyCharNode
		self.keysHandled = getFunction (keysHandled)
	
	def getEventKeys (self, event):
		return set ([event.KeyCode] + [modifier for modifier in [Keys.Alt, Keys.Control, Keys.Shift] if modifier & event.Modifiers])
	
	def bareReadKeysDown (self, params):
		self.keysDownNode.change (self.getEventKeys (params [1]), True)

	def bareReadKeysUp (self, params):
		self.keysUpNode.change (self.getEventKeys (params [1]), True)
		
	def bareReadKeyChar (self, params):
		self.keyCharNode.change (params [1] .KeyChar, True)

	def onKeyPress (self, sender, event):
		if self.keyCharNode:
			self.keyCharLink.read (sender, event)
			
		if not self.keysHandled is None:
			event.Handled = self.keysHandled ()
		
	def attachKeysToWidget (self):
		if self.keysDownNode:
			self.keysDownLink = Link (self.keysDownNode, self.bareReadKeysDown, None)
			self.widget.KeyDown += self.keysDownLink.read

		if self.keysUpNode:
			self.keysUpLink = Link (self.keysUpNode, self.bareReadKeysUp, None)
			self.widget.KeyUp += self.keysUpLink.read

		if self.keyCharNode:
			self.keyCharLink = Link (self.keyCharNode, self.bareReadKeyChar, None)
			
		if self.keyCharNode or self.keysHandled:
			self.widget.KeyPress += self.onKeyPress

class FocusViewMix:
	def __init__ (self):
		self.containsFocus = False
		
	focused = property (lambda self: self.widget.Focused)
		
	def attachFocusToWidget (self):
		def enter (sender, event):
			self.containsFocus = True

			if self.widget.Focused:
				application.focusedView = self
	
		self.widget.Enter += enter
		
		def leave (sender, event):
			self.containsFocus = False
			
			if application.focusedView == self:
				application.focusedView = None
			
		self.widget.Leave += leave
		
	def focus (self):
		self.widget.Focus ()

	def select (self):
		self.widget.Select ()

class LabelViewBase (HintedViewMix):
	def __init__ (self, caption, hint, tweaker):
		HintedViewMix.__init__ (self, hint)
		self.captionNode = getNode (caption)
		self.tweaker = tweaker
		self.stretchHeight = False
	
	def createWidget (self):
		self.widget = Forms.Label ()
		self.attachHintedToWidget ()
		self.widget.AutoSize = True
		self.widget.Dock = Forms.DockStyle.Top
		self.widget.TextAlign = Drawing.ContentAlignment.MiddleLeft
		
		self.link = Link (self.captionNode, None, lambda: assignText (self.widget, str (self.captionNode.new)))
		
		self.link.write ()
		return self.widget

class LLabelView (LabelViewBase):
	def __init__ (self, caption, hint = None, tweaker = None):
		LabelViewBase.__init__ (self, caption, hint, tweaker)

	def createWidget (self):
		LabelViewBase.createWidget (self)
		tweak (self)
		return self.widget

class RLabelView (LabelViewBase):
	def __init__ (self, caption, hint = None, tweaker = None):
		LabelViewBase.__init__ (self, caption, hint, tweaker)
		
	def createWidget (self):
		LabelViewBase.createWidget (self)
		self.widget.TextAlign = Drawing.ContentAlignment.MiddleRight
		tweak (self)
		return self.widget
		
class CLabelView (LabelViewBase):
	def __init__ (self, caption, hint = None, tweaker = None):
		LabelViewBase.__init__ (self, caption, hint, tweaker)
		
	def createWidget (self):
		LabelViewBase.createWidget (self)
		self.widget.TextAlign = Drawing.ContentAlignment.MiddleCenter
		tweak (self)
		return self.widget
		
class FillerView (CLabelView):
	def __init__ (self):
		if application.designMode:
			caption = '[FILLER VIEW]'
		else:
			caption = ''
			
		CLabelView.__init__ (self, caption)

class StretchView:
	def __init__ (self):
		self.stretchHeight = True
				
	def createWidget (self):
		self.widget = Forms.Panel ()
		self.widget.Dock = Forms.DockStyle.Fill
		return self.widget		
		
class ButtonViewBase (EnabledViewMix, HintedViewMix):
	def __init__ (self, actionNode, caption, icon, enabled, hint, tweaker):
		EnabledViewMix.__init__ (self, enabled)
		HintedViewMix.__init__ (self, hint)
		
		self.actionNode = actionNode
		self.captionNode = getNode (caption)
		self.iconNode = getNode (icon)
		self.tweaker = tweaker
		self.stretchHeight = False

	def createWidget (self):
		self.bareCreateWidget ()
		self.attachEnabledToWidget ()
		self.attachHintedToWidget ()	
		
		self.actionLink = Link (self.actionNode, lambda params: self.actionNode.change (None, True), None)
		self.widget.Click += self.actionLink.read				
		
		if self.captionNode:
			self.captionLink = Link (self.captionNode, None, lambda: assignText (self.widget, str (self.captionNode.new)))
			self.captionLink.write ()
		
		if self.iconNode:
			self.iconLink = Link (self.iconNode, None, lambda: assignImage (self.widget, getImage (self.iconNode.new)))
			self.iconLink.write ()	 
		
		tweak (self)
		return self.widget
			
class ButtonView (ButtonViewBase):
	def __init__ (self, actionNode, caption = None, icon = None, enabled = None, hint = None, tweaker = None):
		ButtonViewBase.__init__ (self, actionNode, caption, icon, enabled, hint, tweaker)
		
	def bareCreateWidget (self):
		self.widget = Forms.Button ()
		self.widget.Dock = Forms.DockStyle.Top
		
class MenuButtonView (ButtonViewBase):
	def __init__ (self, actionNode, caption = None, icon = None, enabled = None, hint = None, tweaker = None):
		ButtonViewBase.__init__ (self, actionNode, caption, icon, enabled, hint, tweaker)
				
	def bareCreateWidget (self):
		self.widget = Forms.ToolStripMenuItem ()
		
		def terminateFocusedView (*params):
			try:
				application.focusedView.terminate ()
			except:
				pass
		
		self.widget.Click += terminateFocusedView
		
class ToolButtonView (ButtonViewBase):
	def __init__ (self, actionNode, caption = None, icon = None, enabled = None, hint = None, tweaker = None):
		ButtonViewBase.__init__ (self, actionNode, caption, icon, enabled, hint, tweaker)
				
	def bareCreateWidget (self):
		self.widget = Forms.ToolStripButton ()
		
		def terminateFocusedView (*params):
			try:
				application.focusedView.terminate ()
			except:
				pass
		
		self.widget.Click += terminateFocusedView
				
class TextView (EnabledViewMix, EditableViewMix, HintedViewMix, FocusViewMix):
	def __init__ (self, valueNode, enabled = None, editable = None, hint = None, tweaker = None):
		EnabledViewMix.__init__ (self, enabled)
		EditableViewMix.__init__ (self, editable)
		HintedViewMix.__init__ (self, hint)
		FocusViewMix.__init__ (self)	
		self.valueNode = valueNode
		self.tweaker = tweaker
		self.stretchHeight = False
	
	def createWidget (self):
		self.widget = Forms.TextBox ()
		self.attachEnabledToWidget ()
		self.attachEditableToWidget ()
		self.attachHintedToWidget ()	
		self.attachFocusToWidget ()	
		self.widget.Dock = Forms.DockStyle.Top
		
		self.link = Link (self.valueNode, lambda params: self.valueNode.change (str (self.widget.Text)), lambda: assignText (self.widget, str (self.valueNode.new)))											
		
		self.widget.LostFocus += self.link.read	# The leave event is not generated if next focus is on ListView
		self.widget.KeyDown += lambda sender, event: event.KeyCode != Forms.Keys.Enter or self.link.read (sender, event)	# .NET lib doc: KeyPressed only generated for char keys
			
		self.link.write ()
		tweak (self)
		return self.widget
		
	def terminate (self):
		self.link.read ()
		
class DeltaView (EnabledViewMix, EditableViewMix, HintedViewMix, FocusViewMix):
	def __init__ (self, valueNode, enabled = None, editable = None, hint = None, tweaker = None):
		EnabledViewMix.__init__ (self, enabled)
		EditableViewMix.__init__ (self, editable)
		HintedViewMix.__init__ (self, hint)	
		FocusViewMix.__init__ (self)	
		self.valueNode = valueNode
		self.tweaker = tweaker
		self.stretchHeight = False
	
	def createWidget (self):
		self.widget = Forms.NumericUpDown ()
		self.attachEnabledToWidget ()
		self.attachEditableToWidget ()
		self.attachHintedToWidget ()	
		self.attachFocusToWidget ()	
		self.widget.Dock = Forms.DockStyle.Top
		self.link = Link (self.valueNode, lambda params: self.valueNode.change (str (self.widget.Value)), lambda: assignText (self.widget, str (self.valueNode.new)))	# Read Value since Text changes too late, write Text since whe have an assignText anyhow.
		
		self.widget.ValueChanged += self.link.read
												
		self.link.write ()
		tweak (self)
		return self.widget	

class ComboBoxForComboView (Forms.ComboBox):
	def ProcessDialogKey (self, keyCode):
		result = Forms.ComboBox.ProcessDialogKey (self, keyCode)
		
		if keyCode == Keys.Enter:
			try:
				self.listView.proceedEdit (self, Keys.Enter)
			except:
				pass
				
		return result
		
class ComboView (EnabledViewMix, EditableViewMix, HintedViewMix, FocusViewMix):
	def __init__ (self, valueNode, options, enabled = None, editable = None, hint = None, tweaker = None):
		EnabledViewMix.__init__ (self, enabled)
		EditableViewMix.__init__ (self, editable)
		HintedViewMix.__init__ (self, hint)	
		FocusViewMix.__init__ (self)	
		self.valueNode = valueNode
		self.optionsNode = getNode (options)
		self.tweaker = tweaker
		self.stretchHeight = False
		
	def createWidget (self):
		self.widget = ComboBoxForComboView ()
		self.attachEnabledToWidget ()
		self.attachEditableToWidget ()
		self.attachHintedToWidget ()
		self.attachFocusToWidget ()	
		self.widget.Dock = Forms.DockStyle.Top
		
		self.valueLink = Link (self.valueNode, lambda params: self.valueNode.change (str (self.widget.Text)), lambda: assignText (self.widget, str (self.valueNode.new)))
		
		self.optionsLink = Link (self.optionsNode, None, self.bareWriteOptions)
		
		self.widget.LostFocus += self.valueLink.read	# The leave event is not generated if next focus is on ListView
		self.widget.KeyDown += lambda sender, event: event.KeyCode != Forms.Keys.Enter or self.valueLink.read (sender, event)	# .NET lib doc: KeyPressed only generated for char keys
		self.widget.SelectedValueChanged += self.valueLink.read				
												
		self.valueLink.write ()
		self.optionsLink.write ()
		tweak (self)
		return self.widget
		
	def bareWriteOptions (self):
		self.widget.Items.Clear ()
		
		for option in self.optionsNode.new:
			self.widget.Items.Add (str (option))
		
	def terminate (self):
		self.valueLink.read ()
		
class CheckView (EnabledViewMix, EditableViewMix, HintedViewMix, FocusViewMix):
	def __init__ (self, valueNode, caption, enabled = None, editable = None, hint = None, tweaker = None):
		EnabledViewMix.__init__ (self, enabled)
		EditableViewMix.__init__ (self, editable)
		HintedViewMix.__init__ (self, hint)	
		FocusViewMix.__init__ (self)	
		self.valueNode = valueNode
		self.captionNode = getNode (caption)
		self.tweaker = tweaker
		self.stretchHeight = False
			
	def createWidget (self):
		self.widget = Forms.CheckBox ()
		self.attachEnabledToWidget ()
		self.attachEditableToWidget ()
		self.attachHintedToWidget ()
		self.attachFocusToWidget ()	
		self.widget.Dock = Forms.DockStyle.Top
		
		self.valueLink = Link (self.valueNode, lambda params: self.valueNode.change (self.widget.Checked), self.bareWrite)
		self.widget.CheckedChanged += self.valueLink.read		
		self.valueLink.write ()				
		
		self.captionLink = Link (self.captionNode, None, lambda: assignText (self.widget, str (self.captionNode.new)))
		self.captionLink.write ()
				 	
		tweak (self)
		return self.widget
			
	def bareWrite (self):
		self.widget.Checked = self.valueNode.new
		
class RadioButtonView (EnabledViewMix, EditableViewMix, HintedViewMix, FocusViewMix):
	def __init__ (self, valueNode, caption, marker = None, enabled = None, editable = None, hint = None, tweaker = None):
		EnabledViewMix.__init__ (self, enabled)
		EditableViewMix.__init__ (self, editable)
		HintedViewMix.__init__ (self, hint)	
		FocusViewMix.__init__ (self)	
		self.valueNode = valueNode
		self.captionNode = getNode (caption)
		
		if not marker is None:
			self.marker = marker
		else:
			self.marker = caption
		
		self.tweaker = tweaker		
		self.stretchHeight = False
		
	def createWidget (self):
		self.widget = Forms.RadioButton ()
		self.attachEnabledToWidget ()
		self.attachEditableToWidget ()
		self.attachHintedToWidget ()
		self.attachFocusToWidget ()	
		self.widget.Dock = Forms.DockStyle.Top
		
		self.widget.AutoCheck = False
		
		self.valueLink = Link (self.valueNode, lambda params: self.valueNode.change (self.marker), self.bareWrite)
		self.widget.Click += self.valueLink.read		
		self.valueLink.write ()				
		
		self.captionLink = Link (self.captionNode, None, lambda: assignText (self.widget, str (self.captionNode.new)))
		self.captionLink.write ()			 
		
		tweak (self)
		return self.widget
			
	def bareWrite (self):
		self.widget.Checked = self.valueNode.new == self.marker
													
# <list> = [<item>, ...]
# <item> = <field> | [<field>, ...]

class ListView (EnabledViewMix, MultiSelectViewMix, FocusViewMix):
	Neutral, Next, Previous, Up, Down, Insert, Delete, Undo = range (8)

	# --- Constructor and widget creation method, like supported by all views

	def __init__ (
		self,
		listNode,
		columnLabels,
		selectedListNode = None,
		enabled = None,
		contextMenuView = None,
		checkedListNode = None,
		transformer = None,
		editViews = None,
		exitStateNode = None,
		actionStateNode = None,
		dragObjectGetter = None,
		dragResultGetter = None,
		dropResultGetter = None,
		dropActionGetter = None,
		hoverListNode = None,
		hoverColumnIndexNode = None,
		hintGetter = None,
		key = None,
		sortColumnNumberNode = None,
		clickedColumnIndexNode = None,
		visibleColumns = None,
		multiSelect = None,		
		tweaker = None
	):
		EnabledViewMix.__init__ (self, enabled)
		MultiSelectViewMix.__init__ (self, multiSelect)
		FocusViewMix.__init__ (self)	
		
		self.listNode = listNode
		self.columnLabelsNode = getNode (columnLabels)
		self.selectedListNode = selectedListNode
		self.contextMenuView = contextMenuView
		self.checkedListNode = checkedListNode
		self.transformer = transformer
		self.editViews = editViews
		self.exitStateNode = exitStateNode
		self.actionStateNode = actionStateNode
		self.dragObjectGetter = dragObjectGetter
		self.dragResultGetter = dragResultGetter
		self.dropResultGetter = dropResultGetter
		self.dropActionGetter = dropActionGetter
		self.hoverListNode = hoverListNode
		self.hoverColumnIndexNode = hoverColumnIndexNode
		self.hintGetter = hintGetter
		self.sortColumnNumberNode = sortColumnNumberNode
		self.clickedColumnIndexNode = clickedColumnIndexNode
		self.visibleColumnsNode = getNode (visibleColumns)
		self.tweaker = tweaker
		
		self.stretchHeight = True
		self.sortColumnNumber = 1

		self.editWidget = None
		self.editing = False
		self.edited = False
		self.editRowIndex = -1
		self.editColumnIndex = 0
		self.selecting = False
		self.shifted = False
		
		self.tweakListViewItems = None
		
		currentViewStore () .add (self, key)
	
	def getLrList (self, listViewItem):
		lrList = []
	
		for subItem in listViewItem.SubItems:
			lrList.append ([subItem.Bounds.Left, subItem.Bounds.Right])
			
		if len (lrList) > 1:
			for nextItem in lrList [1:]:
				if nextItem [0]:					# If nextItem doesn't have zero width (which in .Net makes both bounds 0)
					lrList [0][1] = nextItem [0]	#	Correct first subitem, because in .NET the first subitem is the whole item
					break							# (If no non-zero width item found, just leave first subitem equal to whole item
	
		return lrList
		
	def rcFromXy (self, x, y):
		listViewItem = self.widget.GetItemAt (x, y)

		if listViewItem == None:
			return None
			
		for lrIndex, lr in enumerate (self.getLrList (listViewItem)):
			if lr [0] < x < lr [1]:
				return (self.widget.Items.IndexOf (listViewItem), lrIndex)
		else:
			return None
		
	def xyWhFromRc (self, rowIndex, columnIndex):
		listViewItem = self.widget.Items [rowIndex]
		lr = self.getLrList (listViewItem) [columnIndex]
		return (lr [0], listViewItem.Bounds.Top, lr [1] - lr [0], listViewItem.Bounds.Bottom - listViewItem.Bounds.Top)
	
	def getFirstVisibleColumnIndex (self):
		for columnIndex, column in enumerate (self.widget.Columns):
			if column.Width:
				return columnIndex
		else:
			return -1
	
	def getLastVisibleColumnIndex (self):
		lastVisibleColumnIndex  = -1
	
		for columnIndex, column in enumerate (self.widget.Columns):
			if column.Width:
				lastVisibleColumnIndex = columnIndex

		return lastVisibleColumnIndex
	
	def nextEditColumnIndex (self):
		while self.editColumnIndex < self.getLastVisibleColumnIndex ():
			self.editColumnIndex += 1
			
			if self.widget.Columns [self.editColumnIndex] .Width:
				return
		
	def previousEditColumnIndex (self):
		while self.editColumnIndex > self.getFirstVisibleColumnIndex ():
			self.editColumnIndex -= 1
			
			if self.widget.Columns [self.editColumnIndex] .Width:
				return
	
	def proceedEdit (self, editWidget, keyCode):
		# print keyCode
	
		if keyCode == Keys.ShiftKey:
			self.shifted = True
		
		if self.editing:
			if (
				keyCode in [Keys.Enter, Keys.Tab, Keys.Insert, Keys.Delete, Keys.Escape, Keys.None]
				or
				not isinstance (editWidget, ComboBoxForComboView) and keyCode in [Forms.Keys.Up, Forms.Keys.Down]
			):
				self.editing = False
				self.edited = True
								
				lastRowIndex = len (self.listNode.new) - 1
																										
				exitState = ListView.Neutral
												
				if keyCode == Keys.Tab and self.shifted:
					# print 'shift + tab'
				
					exitState = ListView.Previous
					while self.editColumnIndex > self.getFirstVisibleColumnIndex ():
						self.editColumnIndex -= 1
						if self.widget.Columns [self.editColumnIndex] .Width > 0:
							break
					else:
						if self.editRowIndex > 0:
							self.editRowIndex -= 1
							self.editColumnIndex = self.getLastVisibleColumnIndex ()
				elif keyCode in [Keys.Enter] or (keyCode == Keys.Tab and not self.shifted):
					# print 'enter / tab'

					exitState = ListView.Next
					while self.editColumnIndex < self.getLastVisibleColumnIndex ():
						self.editColumnIndex += 1
						if self.widget.Columns [self.editColumnIndex] .Width:
							break
					else:
						if self.editRowIndex < lastRowIndex:
							self.editRowIndex += 1
							self.editColumnIndex = self.getFirstVisibleColumnIndex ()
				elif keyCode == Keys.Up:
					exitState = ListView.Up
					if self.editRowIndex > 0:
						self.editRowIndex -= 1
				elif keyCode in [Keys.Down]:
					exitState = ListView.Down
					if self.editRowIndex < lastRowIndex:
						self.editRowIndex += 1
				elif keyCode == Keys.Insert:
					exitState = ListView.Insert
					
					if not self.actionStateNode is None:	# If autoinserting is applicable at all for this list
						self.editRowIndex += 1
						self.editColumnIndex = self.getFirstVisibleColumnIndex ()
					
				editWidget.Hide ()
				self.widget.TopLevelControl.Controls.Remove (editWidget)				
				self.widget.Focus ()
				self.exitStateNode.change (exitState, True)								
				
			if keyCode != Keys.ShiftKey:
				self.shifted = False

	def createWidget (self):
		self.widget = Forms.ListView ()
		
		self.attachEnabledToWidget ()
		self.attachMultiSelectToWidget ()
		self.attachFocusToWidget ()	
		self.widget.Dock = Forms.DockStyle.Fill
		
		# self.widget.DoubleBuffered = True
		
		self.setStateAllowed = True
		
		def setState (sender, event):			
			if (
				self.setStateAllowed
				and
				hasattr (self, 'state')
				and
				len (self.state) == len (self.widget.Columns)
				and
				(not self.visibleColumnsNode or event.ColumnIndex in self.visibleColumnsNode.new)
			):
				self.state [event.ColumnIndex] = self.widget.Columns [event.ColumnIndex] .Width
				
		self.widget.ColumnWidthChanged += setState

		self.widget.VisibleChanged += lambda sender, event: self.getState ()
			
		if self.checkedListNode:
			self.widget.CheckBoxes = True
			
		self.widget.View = Forms.View.Details
		self.widget.FullRowSelect = True
		self.widget.HideSelection = False
		self.widget.AllowColumnReorder = False
		self.widget.AutoArrange = True
		self.widget.AllowDrop = True
		
		if self.editViews:
			self.widget.OwnerDraw = True
			
		self.widget.GridLines = True

		def onMouseUp (sender, event):
			self.selecting  = False
		
		self.widget.MouseUp += onMouseUp

		def onKeyUp (sender, event):
			self.selecting  = False
		
		self.widget.KeyUp += onKeyUp
		
		def onMouseDown (sender, event):
			self.selecting = True
			
			try:
				self.editColumnIndex = self.rcFromXy (event.X, event.Y) [1]
			except:
				pass
				
		self.widget.MouseDown += onMouseDown

		def onKeyDown (sender, event):
			self.selecting = True
			
			if event.KeyCode == Keys.Left:
				self.previousEditColumnIndex ()
			
			elif event.KeyCode == Keys.Right:
				self.nextEditColumnIndex ()

		self.widget.KeyDown += onKeyDown

		def onDrawColumnHeader (sender, event):
			event.DrawDefault = True

		self.widget.DrawColumnHeader += onDrawColumnHeader
			
		def onDrawItem (sender, event):
			event.DrawDefault = not event.Item.Selected

		self.widget.DrawItem += onDrawItem
		
		def onDrawSubItem (sender, event):
			if event.Item.Selected:
				DrawDefault = False
			
				if event.ColumnIndex < len (self.editViews) and not self.editViews [event.ColumnIndex] is None:
					focusBackgroundColor = HighBright
					foregroundColor = Drawing.Color.Black
					foregroundBrush = Drawing.Brushes.Black
				else:
					focusBackgroundColor = Drawing.SystemColors.Highlight
					foregroundColor = Drawing.Color.White
					foregroundBrush = Drawing.Brushes.White

				if self.widget.Focused or self.editWidget and self.editWidget.Focused:
					event.Graphics.FillRectangle (Drawing.SolidBrush (focusBackgroundColor), event.Bounds)
					if not self.selecting and event.ColumnIndex == self.editColumnIndex and event.ItemIndex == self.editRowIndex:
						event.Graphics.DrawRectangle (Drawing.Pen (foregroundColor), event.Bounds.Left + 1, event.Bounds.Top, event.Bounds.Width - 2, event.Bounds.Height - 2)			
				else:
					event.Graphics.FillRectangle (Drawing.SolidBrush (Drawing.Color.LightGray), event.Bounds)

				event.Graphics.DrawString (
					event.SubItem.Text,
					self.widget.Font,
					foregroundBrush,
					Drawing.RectangleF (event.Bounds.X + 4, event.Bounds.Y, event.Bounds.Width, event.Bounds.Height)
				)
			else:
				event.DrawDefault = True

		self.widget.DrawSubItem += onDrawSubItem	
		
		# --- In place editing

		if self.editViews:		
			self.editWidgets = []
			
			for editView in self.editViews:
				if editView:
					editWidget = editView.createWidget ()
					
					if isinstance (editWidget, ComboBoxForComboView):
						editWidget.listView = self
						
					editWidget.Dock = Forms.DockStyle.None
					editWidget.BackColor = HighBright
					editWidget.AutoSize = False
						
					editWidget.KeyDown += lambda sender, event: self.proceedEdit (sender, event.KeyCode)					
					editWidget.LostFocus += lambda sender, event: self.proceedEdit (sender, Keys.Tab)

					self.editWidgets.append (editWidget)
				else:
					self.editWidgets.append (None)	
					
			def enterEdit (sender, event):
				event.Handled = True
				if self.editRowIndex >= 0 and (event.KeyChar in letters + digits + punctuation):
					try:
						editWidget = self.editWidgets [self.editColumnIndex]
					except:
						editWidget = None
						
					if editWidget is None:
						return
						
					self.editWidget = editWidget

					if editWidget:
						self.editing = True

						rectangleOnForm = self.widget.TopLevelControl.RectangleToClient (
							self.widget.RectangleToScreen (
								Drawing.Rectangle (*self.xyWhFromRc (self.editRowIndex, self.editColumnIndex))
							)
						)
								
						self.widget.TopLevelControl.Controls.Add (editWidget)

						editWidget.Show ()
						editWidget.Width = rectangleOnForm.Size.Width + 1
						editWidget.Height = rectangleOnForm.Size.Height + 1
						editWidget.Left = rectangleOnForm.Location.X
						editWidget.Top = rectangleOnForm.Location.Y - 1
						
						try:
							editWidget.Clear ()
						except:
							pass	
							
						try:
							editWidget.AppendText (event.KeyChar)
						except:
							pass

						editWidget.BringToFront ()
						editWidget.Focus ()
								
			self.widget.KeyPress += enterEdit
			
			def handleActionKey (sender, event):
				if event.KeyCode == Keys.Insert:
					self.actionStateNode.change (ListView.Insert, True)
				elif event.KeyCode == Keys.Delete:
					self.actionStateNode.change (ListView.Delete, True)
					
			if not self.actionStateNode is None:
				self.widget.KeyDown += handleActionKey			
								
		# --- End in place editing
		
		if self.visibleColumnsNode:
			self.visibleColumnsLink = Link (self.visibleColumnsNode, None, self.bareWriteVisibleColumns)
		
		if self.clickedColumnIndexNode:
			self.clickedColumnIndexLink = Link (self.clickedColumnIndexNode, self.bareReadClickedColumnIndex, None)
			self.widget.MouseClick += self.clickedColumnIndexLink.read
		
		if self.sortColumnNumberNode:
			self.listLink = Link (self.listNode, None, self.bareWriteItems)
			self.sortColumnNumberLink = Link (self.sortColumnNumberNode, self.bareReadSortColumnNumber, None)
			self.widget.ColumnClick += self.sortColumnNumberLink.read
		else:
			self.listLink = Link (self.listNode, self.bareReadItems, self.bareWriteItems)
			self.widget.ColumnClick += self.listLink.read
			
#		self.listLink.write ()
		
		self.columnLabelsLink = Link (self.columnLabelsNode, None, lambda: self.bareWriteColumnLabels ())

#		self.columnLabelsLink.write ()
		
#		if self.visibleColumnsNode:
#			self.visibleColumnsLink.write ()
		
		if self.selectedListNode:
			if not hasattr (self.selectedListNode, 'getter'):
				self.selectedListNode.dependsOn ([self.listNode], self.interestingItemList)
				
			self.selectedListLink = Link (self.selectedListNode, lambda params: self.listLink.writing or self.bareReadSelectedItems (), self.bareWriteSelectedItems)
			self.selectedListLink.writeBack = False
			self.widget.MouseDown += self.selectedListLink.read
			self.widget.MouseUp += self.selectedListLink.read
			self.widget.KeyUp += self.selectedListLink.read
			self.widget.ItemDrag += self.selectedListLink.read
#			self.selectedListLink.write ()
						
		if self.checkedListNode:
			self.checkedListNode.dependsOn ([self.listNode], self.checkedItemsLeft)  
			self.checkedListLink = Link (self.checkedListNode, lambda params: self.listLink.writing or self.bareReadCheckedItems (), self.bareWriteCheckedItems)
			self.checkedListLink.writeBack = False
			
			self.preparedToCheckItems = False
			
			def early (*params):
				self.preparedToCheckItems = True
			
			self.widget.ItemCheck += early
			
			def late (*params):
				if self.preparedToCheckItems:
					self.checkedListLink.read ()

				self.preparedToCheckItems = False
			
			self.widget.ItemChecked += late
		
		if self.contextMenuView:
			self.widget.ContextMenuStrip = self.contextMenuView.createWidget ()
			self.widget.MouseUp += lambda sender, event: event.Button != Forms.MouseButtons.Right or sender.ContextMenuStrip.Show (sender, event.Location)
			
		if self.dragObjectGetter:
			self.widget.ItemDrag += self.itemDrag
			
		if self.dragResultGetter:
			self.dragLink = Link (self.listNode, lambda params: self.listNode.change (self.dragResultGetter ()), None)
			
		if self.dropActionGetter:
			self.dropLink = Link (self.listNode, lambda params: self.listNode.change (self.dropResultGetter (params [0])), None)
			
			self.widget.DragEnter += self.dragEnter
			self.widget.DragOver += self.dragOver
			self.widget.DragLeave += self.dragLeave
			self.widget.DragDrop += self.dragDrop
			
		self.toolTip = Forms.ToolTip ()
		self.toolTip.ShowAlways = True
		self.hoverListViewItem = None
		self.hoverColumnIndex = -1
		self.widget.MouseMove += self.track

		tweak (self)

		self.listLink.write ()
		self.columnLabelsLink.write ()

		if self.visibleColumnsNode:
			self.visibleColumnsLink.write
			
		if self.selectedListNode:
			self.selectedListLink.write
		
		return self.widget

	# --- Low level read methods to be passed to Links

	def newSortColumnNumber (self, sortColumnIndex):
		if sortColumnIndex == abs (self.sortColumnNumber) - 1:	# If denotes same column
			self.sortColumnNumber = -self.sortColumnNumber
		else:
			self.sortColumnNumber = sortColumnIndex + 1
			
		return self.sortColumnNumber
		
	def bareReadItems (self, params):
		listToSort = self.listNode.new	# We're still before the change event, so don't use self.listNode.old	
		self.listNode.change (sortList (listToSort, self.newSortColumnNumber (params [1] .Column), self.transformer))
		
	def bareReadSortColumnNumber (self, params):
		self.sortColumnNumberNode.change (self.newSortColumnNumber (params [1] .Column))
	
	def bareReadClickedColumnIndex (self, params):
		rc = self.rcFromXy (params [1] .X, params [1] .Y)
		
		if not rc is None:
			self.clickedColumnIndexNode.change (rc [1])

	def bareReadSelectedItems (self):
		aList = []
		
		for listViewItem in self.widget.SelectedItems:
			aList.append (self.itemFromListViewItem (listViewItem))
			lastSelectedListViewItem = listViewItem
		
		try:
			self.editRowIndex = lastSelectedListViewItem.Index
			self.widget.FocusedItem = lastSelectedListViewItem
			self.widget.Invalidate (lastSelectedListViewItem.Bounds)
		except:
			pass
			
		self.selectedListNode.change (aList)
		
	def bareReadCheckedItems (self):
		aList = []			
		for listViewItem in self.widget.CheckedItems:
			aList.append (self.itemFromListViewItem (listViewItem))
			
		self.checkedListNode.change (aList)
		
	# --- Low level write methods to be passed to Links	
		
	def bareWriteVisibleColumns (self):
		self.widget.BeginUpdate ()
		
		for columnIndex, columnHeader in enumerate (self.widget.Columns):
			if columnIndex in self.visibleColumnsNode.new:
				if hasattr (self, 'state') and len (self.state) == len (self.widget.Columns):
					columnHeader.Width = self.state [columnIndex]
			else:
				columnHeader.Width = 0
				
		self.widget.EndUpdate ()

	def bareWriteItems (self):		
		self.widget.BeginUpdate ()

		self.widget.Items.Clear ()			

		if len (self.listNode.new):				
			if self.transformer:
				listViewItemsBuffer = []
				
				for item in self.listNode.new:					
					listViewItem = Forms.ListViewItem (tuple ([str (field) for field in self.transformer (item)]))		
					listViewItem.Tag = item
					listViewItemsBuffer.append (listViewItem)
					
			elif self.listNode.new [0] .__class__ == list:
				listViewItemsBuffer = [Forms.ListViewItem (tuple ([str (field) for field in item])) for item in self.listNode.new]					
			else:
				listViewItemsBuffer = [Forms.ListViewItem (str (item)) for item in self.listNode.new]
				
			self.widget.Items.AddRange (tuple (listViewItemsBuffer))  # If needed for performance: listViewItems.AddRange (System.Array [Forms.ListViewItem] (listViewItemsBuffer))
			
			if not self.tweakListViewItems is None:
				self.tweakListViewItems ()
			
		self.widget.EndUpdate ()

	def bareWriteColumnLabels (self):
		self.widget.BeginUpdate ()

		if self.widget.Columns.Count == len (self.columnLabelsNode.new):
			for columnIndex, columnLabel in enumerate (self.columnLabelsNode.new):
				self.widget.Columns [columnIndex].Text = str (columnLabel)	# columnLabelsNode.new may be composed of raw contents of other nodes, not only strings
		else:
			self.widget.Columns.Clear ()
			
			self.setStateAllowed = False
			
			for columnIndex, columnLabel in enumerate (self.columnLabelsNode.new):
				columnHeader = Forms.ColumnHeader ()
				columnHeader.Text = str (columnLabel)	# columnLabelsNode.new may be composed of raw contents of other nodes, not only strings

				self.widget.Columns.Add (columnHeader)
				
			self.setStateAllowed = True
			
		if not self.getState ():
			self.state = [columnHeader.Width for columnHeader in self.widget.Columns]

		self.widget.EndUpdate ()

	def bareWriteSelectedItems (self):
		self.widget.BeginUpdate ()

		self.listNode.evaluate ()				# Make sure widget has newest version, so selection will succeed
		
		for listViewItem in self.widget.SelectedItems:
			listViewItem.Selected = False
			
		sortedItemTuples = sorted ([(self.itemFromListViewItem (listViewItem), listViewItem) for listViewItem in self.widget.Items])
		sortedSelectedItems = sorted (self.selectedListNode.new)
	
		itemIndex = 0
		for selectedItem in sortedSelectedItems:
			while sortedItemTuples [itemIndex][0] != selectedItem:
				itemIndex += 1
			
			lastSelectedListViewItem = sortedItemTuples [itemIndex][1]
			lastSelectedListViewItem.Selected = True
			itemIndex += 1
					
		try:
			self.editRowIndex = lastSelectedListViewItem.Index
			lastSelectedListViewItem.EnsureVisible ()				
			self.widget.Invalidate (lastSelectedListViewItem.Bounds)
		except:
			pass		

		self.widget.EndUpdate ()
						
	def bareWriteCheckedItems (self):
		self.widget.BeginUpdate ()

		for listViewItem in self.widget.CheckedItems:
			listViewItem.Checked = False
	
		for listViewItem in self.widget.Items:
			candidateItem = self.itemFromListViewItem (listViewItem)

			for checkedItem in self.checkedListNode.new:
				if candidateItem == checkedItem:
					listViewItem.Checked = True
					break

		self.widget.EndUpdate ()
					
	# --- Drag and drop support methods
	
	def setTargetListViewItem (self, event):
		# From the combination (self.targetListViewItem, self.targetValid) the insertion location can be deduced:
		# - (<anItem>, True) means: insert below underlined item
		# - (None, True) means: insert above first item
		# - (None, False) means: invalid insertion location
		
		try:
			topListViewItem = self.widget.TopItem
		
			mousePoint = self.widget.PointToClient (Drawing.Point (event.X, event.Y))							# Normalized mouse cursor
			targetPoint = Drawing.Point (mousePoint.X, mousePoint.Y - 2 * topListViewItem.Bounds.Height / 3)	# Item above rather than under mouse cursor
																												# Target item is underlined item, line is approximately on mouse cursor
			
			if targetPoint.Y > self.widget.TopItem.Bounds.Top:													# Regular or invalid item
				self.targetListViewItem = self.widget.GetItemAt (targetPoint.X, targetPoint.Y)
				self.targetValid = not self.targetListViewItem is None
			else:																								# If target point above top item
				self.targetListViewItem = None																	# Fictional sentry item above first item
				self.targetValid = self.widget.TopItem == self.widget.Items [0]									# Sentry underlined if line is above first item
		except AttributeError:	# topListViewItem is None, None doesn't have Bounds attribute
			self.targetListViewItem = None
			self.targetValid = len (self.widget.Items) == 0														# Empty list, see target as valid, append to list
		
	def drawTargetLine (self, appear):
		try:
			color = ifExpr (appear, Drawing.Color.Blue, Drawing.Color.White)
				
			if self.targetValid:
				if self.targetListViewItem:
					referenceListViewItem = self.targetListViewItem
					y = referenceListViewItem.Bounds.Bottom						
				else:
					referenceListViewItem = self.widget.TopItem
					y = referenceListViewItem.Bounds.Top
				
				self.widget.CreateGraphics () .DrawLine (Drawing.Pen (color, 1), referenceListViewItem.Bounds.Left, y, referenceListViewItem.Bounds.Right, y)
		except:
			pass				
			
	def itemDrag (self, sender, event):
		dragObject.sourceView = self
		dragObject.value = self.dragObjectGetter ()
	
		if self.widget.DoDragDrop (str (dragObject.value), Forms.DragDropEffects.Move | Forms.DragDropEffects.Copy) != Forms.DragDropEffects.None:
			if self.dragResultGetter:
				self.dragLink.read ()
		
		dragObject.clear ()
	
	def dragDrop (self, sender, event):
		self.drawTargetLine (False)
		
		dragObject.keyState = event.KeyState	# Don't use directly, use dragObject.modifiers property instead		
		dragObject.dropAction = self.dropActionGetter ()
		
		if dragObject.dropAction and self.targetValid:
			try:		
				if self.targetListViewItem:
					self.dropLink.read ([self.itemFromListViewItem (self.targetListViewItem)])								
				else:
					self.dropLink.read ([])
			except Refusal, refusal:
				handleNotification (refusal) 
				event.Effect = Forms.DragDropEffects.None
		
		if dragObject.imported:
			dragObject.clear ()
						
	def dragEnter (self, sender, event):
		event.Effect = event.AllowedEffect
		
		self.targetListViewItem = None	
		self.targetValid = False
			
		if dragObject.imported:
			text = event.Data.GetData (Forms.DataFormats.Text)
			
			try:
				dragObject.value = eval (text)
			except:
				dragObject.value = text
			
		dragObject.targetView = self
		
	def dragOver (self, sender, event):
		self.drawTargetLine (False)
		
		dragObject.keyState = event.KeyState	# Don't use directly, use dragObject.modifiers property instead		
		dropAction = self.dropActionGetter ()
	
		if dropAction:						
			self.setTargetListViewItem (event)
			
			event.Effect = ifExpr (self.targetValid,
				ifExpr (dropAction == DropActions.Move,
					Forms.DragDropEffects.Move,
					Forms.DragDropEffects.Copy),
				Forms.DragDropEffects.None)
			
			self.drawTargetLine (True)
							
		else:
			event.Effect = Forms.DragDropEffects.None				
			
	def dragLeave (self, sender, event):
		self.drawTargetLine (False)
		
		if dragObject.imported:
			dragObject.clear ()
			
		dragObject.targetView = None

	# --- Miscellaneous methods
	
	def getState (self):
		if (
			hasattr (self, 'state')	# Either from viewStore or from previously closed modal dialog widget
			and
			len (self.state) == len (self.widget.Columns)
		):
			for columnIndex, columnHeader in enumerate (self.widget.Columns):
				if not self.visibleColumnsNode or columnIndex in self.visibleColumnsNode.new:
					columnHeader.Width = self.state [columnIndex]
				else:
					columnHeader.Width = 0
					
			return True
		else:
			return False

	def track (self, sender, event):
		hoverItemOrColumnChanged = False
	
		if self.hoverListNode:
			hoverListViewItem = self.widget.GetItemAt (event.X, event.Y)
			
			if not self.hoverListViewItem is hoverListViewItem:
				self.hoverListViewItem = hoverListViewItem
				hoverItemOrColumnChanged = True
				
				if self.hoverListViewItem:
					self.hoverListNode.change ([self.itemFromListViewItem (self.hoverListViewItem)])
				else:
					self.hoverListNode.change ([])

		if self.hoverColumnIndexNode:
			rc = self.rcFromXy (event.X, event.Y)
			
			if not rc is None:
				hoverColumnIndex = (rc [1])
			else:
				hoverColumnIndex = -1
		
			if self.hoverColumnIndex != hoverColumnIndex:
				self.hoverColumnIndex = hoverColumnIndex
				hoverItemOrColumnChanged = True
				
				self.hoverColumnIndexNode.change (hoverColumnIndex)			

		if hoverItemOrColumnChanged:			
			self.toolTip.Active = False
			
			if self.hintGetter and self.hoverListViewItem:
				self.toolTip.SetToolTip (self.widget, getHint (self.hintGetter))
				self.toolTip.Active = True
	
	def interestingItemList (self):							# Order n rather than n**2  !!! Tidyup!!!
		if application.initializing:
			return []
	
		if self.edited:
			self.edited = False
			return [self.listNode.new [self.editRowIndex]]
			
		indexNew = len (self.listNode.new) - 1
		growth = indexNew - (len (self.listNode.old) - 1)
		
		if growth == 0:										# If same size
			if self.listNode.new == self.listNode.old:			# Lists are identical
				return self.selectedListNode.old
			else:												# Both insertion and removal have taken place, no sensible selection possible
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

	def checkedItemsLeft (self):		# Order n**2, usually replaced by external function
		theCheckedItemsLeft = []
		for checkedItem in self.checkedListNode.old:
			for item in self.listNode.new:
				if checkedItem == item:
					theCheckedItemsLeft.append (item)
					break
		return theCheckedItemsLeft			

	def itemFromListViewItem (self, listViewItem):
		if not listViewItem:
			item = None
		elif self.transformer:
			item = listViewItem.Tag
		elif len (listViewItem.SubItems) == 1:
			item = getAsTarget (listViewItem.Text, self.listNode.new [0] .__class__)
		else:
			item = []				
			for subItemIndex, listViewSubItem in enumerate (listViewItem.SubItems):
				item.append (getAsTarget (listViewSubItem.Text, self.listNode.new [0][subItemIndex] .__class__))
					
		return item
			
# <tree> = [<branch>, ...]
# <branch> = <item> | (<item>, <tree>)

class TreeView (EnabledViewMix, FocusViewMix):	# Views a <tree>

	# --- Constructor and widget creation method, like supported by all views
	
	def __init__ (
		self,
		treeNode,
		selectedPathNode = None,
		enabled = None,
		contextMenuView = None,
		transformer = None,
		expansionLevel = None,
		dragObjectGetter = None,
		dragResultGetter = None,
		dropResultGetter = None,
		dropActionGetter = None,
		hoverPathNode = None,
		hintGetter = None,
		tweaker = None
	):
		EnabledViewMix.__init__ (self, enabled)
		FocusViewMix.__init__ (self)	
	
		self.treeNode = treeNode
		self.selectedPathNode = selectedPathNode
		self.contextMenuView = contextMenuView
		self.transformer = transformer
		self.expansionLevelNode = getNode (expansionLevel)
		self.dragObjectGetter = dragObjectGetter
		self.dragResultGetter = dragResultGetter
		self.dropResultGetter = dropResultGetter
		self.dropActionGetter = dropActionGetter
		self.hoverPathNode = hoverPathNode
		self.hintGetter = hintGetter
		self.tweaker = tweaker
		self.stretchHeight = True
				
	def createWidget (self):
		self.widget = Forms.TreeView ()
		self.attachEnabledToWidget ()
		self.attachFocusToWidget ()	
		self.widget.Dock = Forms.DockStyle.Fill
		self.widget.HideSelection = False
		self.widget.AllowDrop = True

		self.visibleTreeNode = Node ([])
		
		if self.expansionLevelNode:
			self.visibleTreeNode.dependsOn ([self.treeNode, self.expansionLevelNode], lambda: None)
		else:
			self.visibleTreeNode.dependsOn ([self.treeNode], lambda: None)
	
		self.visibleTreeLink = Link (self.visibleTreeNode, None, lambda: self.bareWrite ()) 
		self.visibleTreeLink.write ()			

		self.interestingPathsNode = Node ([])
		self.interestingPathsNode.dependsOn ([self.treeNode], lambda: self.interestingPaths ())

		if self.selectedPathNode:
			if not hasattr (self.selectedPathNode, 'getter'):
				self.selectedPathNode.dependsOn ([self.interestingPathsNode], lambda: self.interestingPathsNode.new [0])
				
			self.selectedPathLink = Link (self.selectedPathNode, lambda params: self.visibleTreeLink.writing or self.selectedPathNode.change (self.pathFromTreeViewNode (self.widget.GetNodeAt (params [1] .Location))), self.bareWriteSelectedPath)
			# Leave self.selectedPathLink.writeBack == True to properly deal with rightclicks. Probably bug in WinForms, because not needed with ListView.
			self.widget.MouseDown += self.selectedPathLink.read		# This is the only event already occurring at mouse down, so before a drag
		
		self.visiblePathNode = Node ([])			
		self.visiblePathNode.dependsOn ([self.interestingPathsNode], lambda: self.interestingPathsNode.new [1])
		self.visiblePathLink = Link (self.visiblePathNode, None, lambda: self.treeViewNodeFromPath (self.visiblePathNode.new) .EnsureVisible ())				
		
		if self.contextMenuView:
			self.widget.ContextMenuStrip = self.contextMenuView.createWidget ()
			self.widget.MouseUp += lambda sender, event: event.Button != Forms.MouseButtons.Right or sender.ContextMenuStrip.Show (sender, event.Location)
					
		if self.dropActionGetter:
			self.dragLink = Link (self.treeNode, lambda params: self.treeNode.change (self.dragResultGetter ()), None)
			self.dropLink = Link (self.treeNode, lambda params: self.treeNode.change (self.dropResultGetter (params [0], params [1])), None)
			
			self.widget.ItemDrag += self.itemDrag
			self.widget.DragEnter += self.dragEnter
			self.widget.DragOver += self.dragOver
			self.widget.DragLeave += self.dragLeave
			self.widget.DragDrop += self.dragDrop
			
		self.toolTip = Forms.ToolTip ()
		self.toolTip.ShowAlways = True
		self.hoverTreeViewNode = None
		self.widget.MouseMove += self.track

		tweak (self)
		return self.widget

	# --- Low level read methods to be passed to Links
	
	# None here, all coded as lambdas
	
	# --- Low level write methods to be passed to Links
	
	def bareWriteSelectedPath (self):	# Assignment can't be directly replaced by a lambda
		self.widget.SelectedNode = self.treeViewNodeFromPath (self.selectedPathNode.new)
				
	def bareWrite (self):
		expansionDictionary = {}
		self.fillExpansionDictionary (self.widget.Nodes, (), expansionDictionary)
		self.widget.Nodes.Clear ()
		self.writeTree (self.treeNode.new, self.widget.Nodes, (), expansionDictionary)
		
	def writeTree (self, tree, widgetNodes, hashPath, expansionDictionary):
		for branch in tree:
			widgetNode = Forms.TreeNode ()
			
			if branch.__class__ == tuple:
				item = branch [0]
				itemText = str (item)
				
				if self.transformer:
					newHashPath = hashPath + (item, )
				else:
					newHashPath = hashPath + (itemText, )
									
				self.writeTree (branch [1], widgetNode.Nodes, newHashPath, expansionDictionary)
			else:
				item = branch
				itemText = str (item)
				
				if self.transformer:
					newHashPath = hashPath + (item, )
				else:
					newHashPath = hashPath + (itemText, )
			
			if self.transformer:
				widgetNode.Tag = item
				
				bugFix = self.transformer (item)
				widgetNode.Text = bugFix
			else:
				widgetNode.Text = itemText
					
			try:
				if self.expansionLevelNode:
					if self.expansionLevelNode.new > len (hashPath) + 1:
						widgetNode.Expand ()
				elif expansionDictionary [newHashPath]:
					widgetNode.Expand ()
			except KeyError:						# ... Modified y06m05d08
				pass
			
			widgetNodes.Add (widgetNode)		

	# --- Drag and drop support methods
	
	def setTargetTreeViewNode (self, event):
		# From the combination (self.targetTreeViewNode, self.targetValid, self.onTarget) the insertion location can be deduced:
		# - (<anItem>, True, False) means: insert below underlined node
		# - (<anItem>, True, True) means: insert into highLighted node
		# - (None, True, False) means: insert above top node
		# - (None, False, False) means: invalid insertion location
		
		try:
			topTreeViewNode = self.widget.TopNode
			
			mousePoint = self.widget.PointToClient (Drawing.Point (event.X, event.Y))						# Normalized mouse cursor
			targetPoint = Drawing.Point (mousePoint.X, mousePoint.Y + topTreeViewNode.Bounds.Height / 4)	# Node above rather than under mouse cursor
			
			self.targetTreeViewNode = self.widget.GetNodeAt (targetPoint.X, targetPoint.Y)
			self.targetValid = True																			# Even when targetTreeViewNode is None
			
			# Selection area is is symetric around targetPoint
			# On target area should cover exactly half the selection area
			# First assume targetPoint == mousePoint, derive selection area and from that the on target area
			# Then translate both area's over targetPoint.y - mousePoint.y
			self.onTarget = self.targetValid and self.targetTreeViewNode.Bounds.Top + topTreeViewNode.Bounds.Height / 4 < mousePoint.Y < self.targetTreeViewNode.Bounds.Bottom - topTreeViewNode.Bounds.Height / 4
		except AttributeError:	# topTreeViewNode is None or self.targetTreeViewNode is None, None doesn't have Bounds attribute
			self.targetTreeViewNode = None
			self.onTarget = False

			if self.treeNode.new == []:
				self.targetValid = True
			else:
				self.fillLastExpandedTreeViewNode ()
				self.targetValid = self.lastExpandedTreeViewNode.Bounds.Bottom < self.widget.ClientSize.Height - 1
				
	def drawTargetLine (self, appear):
		try:
			if self.onTarget:
				if appear:
					self.oldForeColor = self.targetTreeViewNode.ForeColor
					self.oldBackColor = self.targetTreeViewNode.BackColor

					self.targetTreeViewNode.ForeColor = Drawing.SystemColors.HighlightText
					self.targetTreeViewNode.BackColor = Drawing.SystemColors.Highlight
				else:
					self.targetTreeViewNode.ForeColor = self.oldForeColor
					self.targetTreeViewNode.BackColor = self.oldBackColor	
			elif self.targetValid:
				color = ifExpr (appear, Drawing.Color.Blue, Drawing.Color.White)
				
				if self.targetTreeViewNode:
					self.widget.CreateGraphics () .DrawLine (Drawing.Pen (color, 1), self.targetTreeViewNode.Bounds.Left, self.targetTreeViewNode.Bounds.Top, self.targetTreeViewNode.Bounds.Right, self.targetTreeViewNode.Bounds.Top)
				elif self.treeNode.new != []:
					self.widget.CreateGraphics () .DrawLine (Drawing.Pen (color, 1), 0, self.lastExpandedTreeViewNode.Bounds.Bottom, self.widget.ClientSize.Width, self.lastExpandedTreeViewNode.Bounds.Bottom)
		except:
			pass
				
	def itemDrag (self, sender, event):
		self.widget.Focus ()
	
		dragObject.sourceView = self
		dragObject.value = self.dragObjectGetter ()
	
		if self.widget.DoDragDrop (str (dragObject.value), Forms.DragDropEffects.Move | Forms.DragDropEffects.Copy) != Forms.DragDropEffects.None:
			self.dragLink.read ()
		
		dragObject.clear ()
				
	def dragDrop (self, sender, event):
		self.widget.HideSelection = False
		self.widget.Focus ()
		
		self.drawTargetLine (False)

		dragObject.keyState = event.KeyState	# Don't use directly, use dragObject.modifiers property instead		
		dragObject.dropAction = self.dropActionGetter ()
		
		if dragObject.dropAction and self.targetValid:
			try:		
				if self.targetTreeViewNode:
					self.dropLink.read (self.pathFromTreeViewNode (self.targetTreeViewNode), not self.onTarget)
				else:
					self.dropLink.read ([], False)
			except Refusal, refusal:
				handleNotification (refusal) 
				event.Effect = Forms.DragDropEffects.None
		
		if dragObject.imported:
			dragObject.clear ()
				
	def dragEnter (self, sender, event):
		self.widget.HideSelection = True
		
		event.Effect = event.AllowedEffect
		
		self.targetTreeViewNode = None	
		self.targetValid = False
		
		if dragObject.imported:
			text = event.Data.GetData (Forms.DataFormats.Text)
			
			try:
				dragObject.value = eval (text)
			except:
				dragObject.value = text
			
		dragObject.targetView = self
		
	def dragOver (self, sender, event):
		self.drawTargetLine (False)
		
		dragObject.keyState = event.KeyState	# Don't use directly, use dragObject.modifiers property instead		
		dropAction = self.dropActionGetter ()
	
		if dropAction:						
			self.setTargetTreeViewNode (event)

			event.Effect = ifExpr (self.targetValid,
				ifExpr (dropAction == DropActions.Move,
					Forms.DragDropEffects.Move,
					Forms.DragDropEffects.Copy),
				Forms.DragDropEffects.None)
			
			self.drawTargetLine (True)
							
		else:
			event.Effect = Forms.DragDropEffects.None
										
	def dragLeave (self, sender, event):
		self.widget.HideSelection = False
		
		self.drawTargetLine (False)
		
		if dragObject.imported:
			dragObject.clear ()
			
		dragObject.targetView = None

	# --- Miscellaneous methods
	
	def track (self, sender, event):
		hoverTreeViewNode = self.widget.GetNodeAt (event.Location)
		if not hoverTreeViewNode is self.hoverTreeViewNode:
			self.hoverTreeViewNode = hoverTreeViewNode
			
			if self.hoverPathNode:
				self.hoverPathNode.change (self.pathFromTreeViewNode (self.hoverTreeViewNode))
				
			self.toolTip.Active = False
			
			if self.hintGetter and self.hoverTreeViewNode:
				self.toolTip.SetToolTip (self.widget, getHint (self.hintGetter))
				self.toolTip.Active = True
	
	def assignSelectedTreeViewNode (self, treeViewNode):
		self.widget.SelectedNode = treeViewNode		
				
	def itemFromTreeViewNode (self, treeViewNode):
		if not treeViewNode:
			return None
		
		rootBranch  = self.treeNode.new [0]
		
		if self.transformer:
			return treeViewNode.Tag
		elif rootBranch.__class__ == tuple:
			return getAsTarget (treeViewNode.Text, rootBranch [0] .__class__)
		else:
			return getAsTarget (treeViewNode.Text, rootBranch.__class__)
			
	def pathFromTreeViewNode (self, treeViewNode):
		path = []
		while not treeViewNode is None:
			path.insert (0, self.itemFromTreeViewNode (treeViewNode))
			treeViewNode = treeViewNode.Parent
			
		return path
	
	def treeViewNodeFromPath (self, path):
		treeViewNodes = self.widget.Nodes
		treeViewNode = None						# ... Added y06m05d08
		
		for item in path:
			for treeViewNode in treeViewNodes:
				candidateItem = self.itemFromTreeViewNode (treeViewNode)
				
				if candidateItem == item:
					treeViewNodes = treeViewNode.Nodes
					break
					
		return treeViewNode		
		
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
	
	def fillExpansionDictionary (self, treeViewNodes, hashPath, expansionDictionary):
		for treeViewNode in treeViewNodes:
			if self.transformer:
				newHashPath = hashPath + (treeViewNode.Tag, )
			else:
				newHashPath = hashPath + (treeViewNode.Text, )	# Store as string since its used in View rather than Node
				
			expansionDictionary [newHashPath] = treeViewNode.IsExpanded
			self.fillExpansionDictionary (treeViewNode.Nodes, newHashPath, expansionDictionary)
			
	def fillLastExpandedTreeViewNode (self):
		currentTreeViewNode = None	# Virtual parent of root(s)
		expanded = True				# Always expanded	
		treeViewNodes = self.widget.Nodes
		
		while expanded and len (treeViewNodes) > 0:
			currentTreeViewNode = treeViewNodes [len (treeViewNodes) - 1]
			expanded = currentTreeViewNode.IsExpanded
			treeViewNodes = currentTreeViewNode.Nodes
			
		self.lastExpandedTreeViewNode = currentTreeViewNode
			
class GroupView:
	def __init__ (self, clientView, caption, tweaker = None):
		self.clientView = clientView
		self.captionNode = getNode (caption)
		self.stretchHeight = False
		self.tweaker = tweaker
		
	def createWidget (self):
		self.widget = Forms.GroupBox ()
		self.widget.Dock = Forms.DockStyle.Fill
		
		self.widget.Controls.Add (self.clientView.createWidget ())
		
		if self.clientView.stretchHeight:
			self.stretchHeight = True
		else:
			self.widget.MinimumSize = Drawing.Size (0, self.clientView.widget.PreferredSize.Height + 20)
		
		self.captionLink = Link (self.captionNode, None, lambda: assignText (self.widget, str (self.captionNode.new)))			
		self.captionLink.write ()
		
		tweak (self)
		return self.widget
			
class PageView (FocusViewMix):
	def __init__ (self, clientView, caption, enabled = None, tweaker = None):
		FocusViewMix.__init__ (self)
		self.clientView = clientView
		self.captionNode = getNode (caption)
		self.enabledNode = getNode (enabled)
		self.tweaker = tweaker

	selected = property (lambda self: self.tabbedView.pageViews.index (self) == self.tabbedView.selectedIndexNode.new)

	def select (self):
		self.tabbedView.selectedIndexNode.follow (self.tabbedView.pageViews.index (self))

	def createWidget (self):
		self.widget = Forms.TabPage ()
		self.attachFocusToWidget ()
		self.widget.Controls.Add (self.clientView.createWidget ())
				
		if not hasattr (self, 'captionLink'):	
			self.captionLink = Link (self.captionNode, None, lambda: assignText (self.widget, str (self.captionNode.new)))
			
		self.captionLink.write ()
		
		tweak (self)
		return self.widget
		
class TabbedView:
	def __init__ (self, pageViews, selectedIndex = None, tweaker = None):
		self.pageViews = pageViews
		
		self.repageNode = Node (None)
		self.repageNode.dependsOn ([pageView.enabledNode for pageView in self.pageViews if pageView.enabledNode], lambda: None)
		
		self.selectedIndexNode = getNode (selectedIndex)
		self.tweaker = tweaker

		self.stretchHeight = True

		for pageView in pageViews:
			pageView.tabbedView = self
			
		self.selectedIndexFollows = False
		self.clearPages = True		
		
	def createWidget (self):
		self.widget = Forms.TabControl ()
		self.widget.Dock = Forms.DockStyle.Fill
		
		for pageView in self.pageViews:
			pageView.createWidget ()
			
		self.repageLink = Link (self.repageNode, None, self.repage)
		self.clearPages = False
		self.repageLink.write ()
		self.clearPages = True
			
		if self.selectedIndexNode:
			def bareReadSelectedIndex (params):			
				for pageView in self.pageViews:
					if pageView.widget == self.widget.SelectedTab:
						if self.selectedIndexFollows:
							self.selectedIndexNode.follow (self.pageViews.index (pageView))
						else:
							self.selectedIndexNode.change (self.pageViews.index (pageView))
							
						return
				
				if self.selectedIndexFollows:
					self.selectedIndexNode.follow (-1)
				else:
					self.selectedIndexNode.change (-1)
				
			def bareWriteSelectedIndex ():
				self.widget.SelectedIndex = self.pageViews [self.selectedIndexNode.new] .internalIndex
			
			self.selectedIndexLink = Link (self.selectedIndexNode, bareReadSelectedIndex, bareWriteSelectedIndex)
			self.selectedIndexLink.writeBack = False
			self.widget.SelectedIndexChanged += self.selectedIndexLink.read
			self.selectedIndexLink.write ()
			
			
		tweak (self)
		return self.widget 

	def repage (self):
		self.widget.SuspendLayout ()
		
		if self.clearPages:
			self.widget.TabPages.Clear ()
			
		internalIndex = 0
					
		for pageView in self.pageViews:
			if pageView.enabledNode is None or pageView.enabledNode.new:
				self.widget.TabPages.Add (pageView.widget)
				pageView.internalIndex = internalIndex
				internalIndex += 1
			else:
				pageView.internalIndex = -1
				
		if hasattr (self, 'selectedIndexLink'):
			self.selectedIndexFollows = True
			self.selectedIndexLink.read ()	# self.widget.SelectedIndexChanged is not sent
			self.selectedIndexFollows = False
						
		self.widget.ResumeLayout ()
		
class GridView:
	def __init__ (self, childViews, tweaker = None):
		self.childViews = childViews
		self.tweaker = tweaker
		self.stretchHeight = False
		
	def createWidget (self):
		self.widget = Forms.TableLayoutPanel ()
		self.widget.Dock = Forms.DockStyle.Fill
		
		columnWidths = []
		for rowIndex, childViewRow in enumerate (self.childViews):
			stretchRowHeight = False
			preferredRowHeight = 0
			for columnIndex, childView in enumerate (childViewRow):
				if len (columnWidths) <= columnIndex:
					columnWidths.append (0)
			
				if not childView.__class__ in [HExtensionView, VExtensionView, EmptyView]:
					sentryColumnIndex = columnIndex + 1		
					try:
						while childViewRow [sentryColumnIndex] .__class__ is HExtensionView:
							sentryColumnIndex += 1
					except:
						pass
					nrOfColumns = sentryColumnIndex - columnIndex
					
					sentryRowIndex = rowIndex + 1
					try:
						while self.childViews [sentryRowIndex] [columnIndex] .__class__ is VExtensionView:
							sentryRowIndex += 1
					except:
						pass
					nrOfRows = sentryRowIndex - rowIndex					
					
					self.widget.Controls.Add (childView.createWidget (), columnIndex, rowIndex)
					
					self.widget.SetColumnSpan (childView.widget, nrOfColumns)
					self.widget.SetRowSpan (childView.widget, nrOfRows)
					
					if childView.stretchHeight:
						stretchRowHeight = True
					elif childView.widget.PreferredSize.Height > preferredRowHeight:
						preferredRowHeight = childView.widget.PreferredSize.Height

					if childView.__class__ in [LToolBarView, RToolBarView]:
						columnWidths [columnIndex] = childView.widget.PreferredSize.Width
									
			rowStyle = Forms.RowStyle ()
			
			if stretchRowHeight:
				self.stretchHeight = True
				
				rowStyle.SizeType = Forms.SizeType.Percent
				rowStyle.Height = 100 
			else:
				rowStyle.SizeType = Forms.SizeType.Absolute
				rowStyle.Height = preferredRowHeight + 7
				
			self.widget.RowStyles.Add (rowStyle)
					
		gridWidth = 0
		for childViewRow in self.childViews:
			gridWidth = max (gridWidth, len (childViewRow))
	
		for columnIndex in range (gridWidth):
			columnStyle = Forms.ColumnStyle ()
			if columnWidths [columnIndex] == 0:
				columnStyle.SizeType = Forms.SizeType.Percent
				columnStyle.Width = 100 / gridWidth
			else:
				columnStyle.SizeType = Forms.SizeType.Absolute
				columnStyle.Width = columnWidths [columnIndex]			
			
			self.widget.ColumnStyles.Add (columnStyle)
							
		tweak (self)						
		return self.widget

class HGridView (GridView):
	def __init__ (self, childViews, tweaker = None):
		GridView.__init__ (self, [childViews], tweaker)
		
class VGridView (GridView):
	def __init__ (self, childViews, tweaker = None):
		childRows = []
		for childView in childViews:
			childRows.append ([childView])
			
		GridView.__init__ (self, childRows, tweaker)
	
class SplitViewBase:
	def __init__ (self, childView1, childView2, key, tweaker):
		self.childView1 = childView1
		self.childView2 = childView2
		self.tweaker = tweaker
		
		self.stretchHeight = True
		
		currentViewStore () .add (self, key)

	def createWidget (self):
		self.widget = Forms.SplitContainer ()
		self.widget.Dock = Forms.DockStyle.Fill
		
		def setState (sender, event):
			self.state = (1.0 * self.widget.SplitterDistance) / self.getMaxSplitterDistance ()

		def getStateAndAllowSetState (sender, event):
			if self.widget.Visible:
				if hasattr (self, 'state'):	# Either from viewStore or from previously closed modal dialog widget
					try:
						self.widget.SplitterDistance = int (self.state * self.getMaxSplitterDistance ())
					except:	# If impossible to obey, due to e.g. minimum size
						pass
					
				self.widget.SplitterMoved += setState
		
		self.widget.VisibleChanged += getStateAndAllowSetState
		
		self.widget.Panel1.Controls.Add (self.childView1.createWidget ())		
		self.widget.Panel2.Controls.Add (self.childView2.createWidget ())
		
		return self.widget
	
class HSplitView (SplitViewBase):
	def __init__ (self, leftChildView, rightChildView, key = None, tweaker = None):
		SplitViewBase.__init__ (self, leftChildView, rightChildView, key, tweaker)
		
	def createWidget (self):
		SplitViewBase.createWidget (self)
		return self.widget
		
	def getMaxSplitterDistance (self):
		return self.widget.Width
		
class VSplitView (SplitViewBase):
	def __init__ (self, topChildView, bottomChildView, key = None, tweaker = None):
		SplitViewBase.__init__ (self, topChildView, bottomChildView, key, tweaker)
		
	def createWidget (self):
		SplitViewBase.createWidget (self)
		self.widget.Orientation = Forms.Orientation.Horizontal
		tweak (self)
		return self.widget
		
	def getMaxSplitterDistance (self):
		return self.widget.Height
	
class HExtensionView:
	pass
	
class VExtensionView:
	pass
	
class EmptyView:
	pass

class ToolBarView:
	def __init__ (self, toolViews, tweaker = None):
		self.toolViews = toolViews
		self.tweaker = tweaker

		self.stretchHeight = False

	def createWidget (self):
		self.widget = Forms.ToolStrip ()
		self.widget.GripStyle = Forms.ToolStripGripStyle.Hidden
		self.widget.RenderMode = Forms.ToolStripRenderMode.System

		for toolView in self.toolViews:
			self.widget.Items.Add (toolView.createWidget ())
					
		tweak (self)
		return self.widget

class LToolBarView (ToolBarView):
	def __init__ (self, toolViews, tweaker = None):
		ToolBarView.__init__ (self, toolViews, tweaker)

	def createWidget (self):
		ToolBarView.createWidget (self)
		self.widget.Dock = Forms.DockStyle.Left
		return self.widget
		
class RToolBarView (ToolBarView):
	def __init__ (self, toolViews, tweaker = None):
		ToolBarView.__init__ (self, toolViews, tweaker)

	def createWidget (self):
		ToolBarView.createWidget (self)
		self.widget.Dock = Forms.DockStyle.Right
		return self.widget

class TToolBarView (ToolBarView):
	def __init__ (self, toolViews, tweaker = None):
		ToolBarView.__init__ (self, toolViews, tweaker)

	def createWidget (self):
		ToolBarView.createWidget (self)
		self.widget.Dock = Forms.DockStyle.Top
		return self.widget

class BToolBarView (ToolBarView):
	def __init__ (self, toolViews, tweaker = None):
		ToolBarView.__init__ (self, toolViews, tweaker)

	def createWidget (self):
		ToolBarView.createWidget (self)
		self.widget.Dock = Forms.DockStyle.Bottom
		return self.widget

class MenuBarView:
	def __init__ (self, menuItemViews, tweaker = None):
		self.menuItemViews = menuItemViews
		self.tweaker = tweaker
		
	def createWidget (self):
		self.widget = Forms.MenuStrip ()

		for menuItemView in self.menuItemViews:
			self.widget.Items.Add (menuItemView.createWidget ())
			
		tweak (self)
		return self.widget
		
class ContextMenuView:
	def __init__ (self, menuItemViews, tweaker = None):
		self.menuItemViews = menuItemViews
		self.tweaker = tweaker
		
	def closeFix (self, sender, event):
		# Don't block closing, this will cause a deadlock if the app's close button is clicked.
		# Just prepend a better way of closing
		if event.CloseReason == Forms.ToolStripDropDownCloseReason.AppClicked:
			Forms.SendKeys.SendWait ('{ESC}')
				
	def createWidget (self):
		self.widget = Forms.ContextMenuStrip ()
		self.widget.Closing += self.closeFix

		for menuItemView in self.menuItemViews:
			self.widget.Items.Add (menuItemView.createWidget ())
			
		tweak (self)
		return self.widget		

class MenuListView:
	def __init__ (self, menuItemViews, caption, tweaker = None):
		self.menuItemViews = menuItemViews
		self.captionNode = getNode (caption)
		self.tweaker = tweaker
		
	def createWidget (self):
		self.widget = Forms.ToolStripMenuItem ()
				
		for menuItemView in self.menuItemViews:
			self.widget.DropDownItems.Add (menuItemView.createWidget ())
		
		self.captionLink = Link (self.captionNode, None, lambda: assignText (self.widget, str (self.captionNode.new)))		
		self.captionLink.write ()
		
		tweak (self)
		return self.widget

class MenuSeparatorView:
	def __init__ (self, tweaker = None):
		self.tweaker = tweaker
		
	def createWidget (self):
		self.widget = Forms.ToolStripSeparator ()
		tweak (self)
		return self.widget
		
class ToolSeparatorView (MenuSeparatorView):
	def __init__ (self, tweaker = None):
		self.tweaker = tweaker
		
class WindowViewBase (object, KeysViewMix):
	def __init__ (self, clientView, caption, menuBarView, key, fixedSize, tweaker, keysDownNode, keysUpNode, keyCharNode, keysHandled, icon, exitChecker):
		KeysViewMix.__init__ (self, keysDownNode, keysUpNode, keyCharNode, keysHandled)
		self.clientView = clientView
		self.captionNode = getNode (caption)
		self.menuBarView = menuBarView
		self.fixedSize = fixedSize
		self.tweaker = tweaker
		self.icon = icon
		self.exitChecker = exitChecker

		currentViewStore () .add (self, key)

	def createWidget (self):	# ??? bareCreateWidget, just as with buttons?
		self.widget = Forms.Form ()

		if not self.icon is None:
			self.widget.Icon = getIcon (self.icon)
			
		self.attachKeysToWidget ()

		if self.keysDownNode or self.keysUpNode or self.keyCharNode or self.keysHandled:
			self.widget.KeyPreview = True
		
		if hasattr (self, 'state'):	# Either from viewStore or from previously closed modal dialog widget
			if (currentViewStore () is mainViewStore):
				self.widget.StartPosition = Forms.FormStartPosition.Manual
				self.widget.Left, self.widget.Top, self.widget.Width, self.widget.Height = self.state
			else:
				self.widget.StartPosition = Forms.FormStartPosition.WindowsDefaultLocation
				self.widget.Width, self.widget.Height = self.state [2:]
		else:
			self.widget.StartPosition = Forms.FormStartPosition.WindowsDefaultBounds
		
		def setState (sender, event):
			self.widget.StartPosition = Forms.FormStartPosition.Manual	# Modal dialog widget may be reshown using StartPosition, without being recreated
			self.state = self.widget.Left, self.widget.Top, self.widget.Width, self.widget.Height

		self.widget.Move += setState
		self.widget.Resize += setState
		
		childViews = [self.clientView]
		if self.menuBarView:
			childViews.append (self.menuBarView)
			
		for childView in childViews:
			self.widget.Controls.Add (childView.createWidget ())
			
		self.captionLink = Link (
			self.captionNode,
			None,
			lambda: assignText (self.widget, ifExpr (application.designMode, '[DESIGN MODE] ', '') + str (self.captionNode.new))
		)
		
		self.captionLink.write ()

		return self.widget
		
	def execute (self):
		try:
			self.bareExecute ()
		except Refusal, refusal:
			handleNotification (refusal)
		except Exception, exception:
			problem = 'Cannot execute widget, '
			handleNotification (Error (problem + exMessage (exception), report = problem + exReport (exception)))

	def exit (self):
		self.widget.Hide ()

	def terminateFocusedView (self):
		try:
			application.focusedView.terminate ()
		except:
			pass
			
class MainView (WindowViewBase):
	def __init__ (
		self,
		clientView,
		caption,
		menuBarView = None,
		viewStoreFileName = 'views.store',
		key = None,
		fixedSize = False,
		tweaker = None,
		keysDownNode = None,
		keysUpNode = None,
		keyCharNode = None,
		keysHandled = None,
		icon = None,
		exitChecker = None
	):
		application.mainView = self
		WindowViewBase.__init__ (self, clientView, caption, menuBarView, key, fixedSize, tweaker, keysDownNode, keysUpNode, keyCharNode, keysHandled, icon, exitChecker)
		Forms.Application.EnableVisualStyles ()
#		Forms.Application.SetCompatibleTextRenderingDefault (False)

		self.viewStoreFileName = viewStoreFileName
	
	def createWidget (self):
		WindowViewBase.createWidget (self)			

		def onFormClosing (sender, event):
			self.terminateFocusedView ()
			event.Cancel = not (self.exitChecker is None or self.exitChecker ())

		self.widget.FormClosing += onFormClosing
				
		if self.fixedSize and not application.designMode:		
			self.widget.FormBorderStyle = Forms.FormBorderStyle.FixedDialog
		else:
			self.widget.FormBorderStyle = Forms.FormBorderStyle.Sizable
	
		return self.widget
		
	def bareExecute (self):
		mainViewStore.load (self.viewStoreFileName)
		self.createWidget ()
		application.initializing = False
		
		tweak (self)
		self.widget.ShowDialog ()
		mainViewStore.save ()

	def exit (self):
		self.widget.Close ()
					
class ModalView (WindowViewBase):
	def __init__ (
		self,
		clientView,
		caption,
		menuBarView = None,
		key = None,
		fixedSize = False,
		tweaker = None,
		keysDownNode = None,
		keysUpNode = None,
		keyCharNode = None,
		keysHandled = None,
		icon = None
	):
		WindowViewBase.__init__ (self, clientView, caption, menuBarView, key, fixedSize, tweaker, keysDownNode, keysUpNode, keyCharNode, keysHandled, icon, None)
		
	def createWidget (self):
		WindowViewBase.createWidget (self)
	
		if self.fixedSize and not application.designMode:		
			self.widget.FormBorderStyle = Forms.FormBorderStyle.FixedDialog
		else:
			self.widget.FormBorderStyle = Forms.FormBorderStyle.Sizable

		self.widget.MinimizeBox = False
		self.widget.MaximizeBox = False
		self.widget.ShowInTaskbar = False
				
		return self.widget

	def bareExecute (self):
		if not hasattr (self, 'widget'):
			self.createWidget ()
			
		tweak (self)
		self.widget.ShowDialog ()
			
class ModelessView (WindowViewBase):
	def __init__ (
		self,
		clientView,
		caption,
		menuBarView = None,
		key = None,
		fixedSize = False,
		exitActionNode = None,
		tweaker = None,
		keysDownNode = None,
		keysUpNode = None,
		keyCharNode = None,
		keysHandled = None,
		icon = None,
		exitChecker = None
	):
		WindowViewBase.__init__ (self, clientView, caption, menuBarView, key, fixedSize, tweaker, keysDownNode, keysUpNode, keyCharNode, keysHandled, icon, exitChecker)
		self.exitActionNode = exitActionNode
		
	def createWidget (self):
		WindowViewBase.createWidget (self)
		
		def onFormClosing (sender, event):
			self.terminateFocusedView ()
			event.Cancel = True
			
			if self.exitChecker is None or self.exitChecker ():					
				self.widget.Hide ()
		
		self.widget.FormClosing += onFormClosing
		
		if self.exitActionNode:
			self.exitActionLink = Link (self.exitActionNode, lambda params: self.exitActionNode.change (None, True), None)			
			self.widget.Closed += self.exitActionLink.read
					
		if self.fixedSize and not application.designMode:		
			self.widget.FormBorderStyle = Forms.FormBorderStyle.FixedToolWindow
		else:
			self.widget.FormBorderStyle = Forms.FormBorderStyle.SizableToolWindow
				
		self.widget.ShowInTaskbar = False
		
		return self.widget

	def bareExecute (self):
		if not hasattr (self, 'widget'):
			self.createWidget ()
			self.widget.Owner = application.mainView.widget
			
		tweak (self)
		self.widget.Show ()
