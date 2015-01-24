# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

import Tkinter as tki

from edenLib.node import *
from edenLib.store import *

mainViewStore = Store ()
currentViewStore = CallableValue (mainViewStore)	# All applicable views will add themselves to currentViewStore ()
		
class ViewBase:
	def configCell (self, rowIndex = 0, columnIndex = 0, rowSpan = 1, columnSpan = 1):
		self.widget.grid (row = rowIndex, column = columnIndex, rowspan = rowSpan, columnspan = columnSpan, sticky = 'nsew' if self.stretchHeight else 'new')
		
	def stretchRow (self, rowIndex = 0):
		self.widget.rowconfigure (rowIndex, weight = 1)
	
	def stretchColumn (self, columnIndex = 0):	
		self.widget.columnconfigure (columnIndex, weight = 1)
				
class LabelViewBase (ViewBase):
	def __init__ (self, caption):
		self.captionNode = getNode (caption)
	
	def createWidget (self):
		self.stretchHeight = False
		self.widget = Forms.Label ()
		self.link = Link (self.captionNode, None, lambda: self.widget.config (text = str (self.captionNode.new)))
		self.link.write ()
		return self.widget

class LLabelView (LabelViewBase):
	def __init__ (self, caption):
		LabelViewBase.__init__ (self, caption)

	def createWidget (self):
		LabelViewBase.createWidget (self)
		self.widget.TextAlign = Drawing.ContentAlignment.MiddleLeft
		return self.widget

class RLabelView (LabelViewBase):
	def __init__ (self, caption):
		LabelViewBase.__init__ (self, caption)
		
	def createWidget (self):
		LabelViewBase.createWidget (self)
		self.widget.TextAlign = Drawing.ContentAlignment.MiddleRight
		return self.widget
		
class CLabelView (LabelViewBase):
	def __init__ (self, caption):
		LabelViewBase.__init__ (self, caption)
		
	def createWidget (self):
		LabelViewBase.createWidget (self)
		self.widget.TextAlign = Drawing.ContentAlignment.MiddleCenter
		return self.widget
		
class FillerView (CLabelView):
	def __init__ (self):
		if application.designMode:
			caption = '[FILLER VIEW]'
		else:
			caption = ''
			
		CLabelView.__init__ (self, caption)

class StretchView (ViewBase):
	def __init__ (self):
		self.stretchHeight = True
				
	def createWidget (self):
		self.widget = Forms.Panel ()
		self.widget.Dock = Forms.DockStyle.Fill
		return self.widget		
		
class ButtonViewBase (ViewBase):
	def __init__ (self, action = None, caption = None, icon = None):
		self.actionNode = getNode (action)
		self.captionNode = getNode (caption)
		self.iconNode = getNode (icon)
		
	def createWidget (self):
		self.actionLink = Link (self.actionNode, lambda params: self.actionNode.change (None, True), None)
		self.widget = tki.Button (self.parentView.widget, command = self.actionLink.read)
		
		if self.captionNode:
			self.captionLink = Link (self.captionNode, None, lambda: self.widget.configure (text = str (self.captionNode.new)))
			self.captionLink.write ()
		
		if self.iconNode:
			self.iconLink = Link (self.iconNode, None, lambda: assignImage (self.widget, getImage (self.iconNode.new)))
			self.iconLink.write ()
			
		return self.widget
		
class ButtonView (ButtonViewBase):
	def createWidget (self):
		self.stretchHeight = False
		return ButtonViewBase.createWidget (self)
	
class StretchButtonView (ButtonViewBase):
	def createWidget (self):
		self.stretchHeight = True
		return ButtonViewBase.createWidget (self)
		
class TextViewBase (ViewBase):
	def __init__ (self, value = ''):
		self.valueNode = getNode (value)
	
	def createWidget (self):			
		self.link = Link (self.valueNode, lambda params: self.valueNode.change (str (self.widget.Text)), lambda: (self.widget.delete (self.beginMarker, 'end'), self.widget.insert (self.beginMarker, str (self.valueNode.new))))
		self.link.write ()
		return self.widget
		
	def terminate (self):
		self.link.read ()
		
class TextView (TextViewBase):
	def createWidget (self):
		self.stretchHeight = False
		self.beginMarker = 0
		self.widget = tki.Entry (master = self.parentView.widget)						
		return TextViewBase.createWidget (self)		
		
class StretchTextView (TextViewBase):
	def createWidget (self):
		self.stretchHeight = True
		self.beginMarker = 1.0
		self.widget = tki.Text (master = self.parentView.widget, height = 1)
		return TextViewBase.createWidget (self)		
		
class GridView (ViewBase):
	def __init__ (self, childViews):
		self.childViews = childViews
				
		for childViewRow in self.childViews:
			for childView in childViewRow:
				childView.parentView = self
				
	def createWidget (self):
		self.stretchHeight = True			
		self.widget = tki.Frame (master = self.parentView.widget, background = 'yellow')
		
		maxNrOfColumns = 0
		for rowIndex, childViewRow in enumerate (self.childViews):
			stretchRowHeight = False
			maxNrOfColumns = max (maxNrOfColumns, len (childViewRow))
			for columnIndex, childView in enumerate (childViewRow):			
				if not childView.__class__ in [HExtensionView, VExtensionView, EmptyView]:
					sentryRowIndex = rowIndex + 1
					try:
						while self.childViews [sentryRowIndex] [columnIndex] .__class__ is VExtensionView:
							sentryRowIndex += 1
					except:
						pass
					rowSpan = sentryRowIndex - rowIndex					
					
					sentryColumnIndex = columnIndex + 1		
					try:
						while childViewRow [sentryColumnIndex] .__class__ is HExtensionView:
							sentryColumnIndex += 1
					except:
						pass
					columnSpan = sentryColumnIndex - columnIndex
					
					childView.createWidget ()
					childView.configCell (rowIndex, columnIndex, rowSpan, columnSpan)
											
					if childView.stretchHeight:
						stretchRowHeight = True
						
			if True or stretchRowHeight:
				self.stretchRow (rowIndex)
				self.stretchHeight = True
		
		for columnIndex in range (maxNrOfColumns):
			self.stretchColumn (columnIndex)			
						
		return self.widget		
		
class HGridView (GridView):
	def __init__ (self, childViews):
		GridView.__init__ (self, [childViews])
		
class VGridView (GridView):
	def __init__ (self, childViews):
		childRows = []
		for childView in childViews:
			childRows.append ([childView])
			
		GridView.__init__ (self, childRows)
		
class HExtensionView:
	pass
	
class VExtensionView:
	pass
	
class EmptyView:
	pass
		
class MainView (ViewBase):
	def __init__ (
		self,
		clientView,
		caption,
		key = None
	):
		self.clientView = clientView
		self.captionNode = getNode (caption)
		
		self.clientView.parentView = self
		application.mainView = self
		
		self.viewStoreFileName = 'views.store'
		currentViewStore () .add (self, key)
	
	def createWidget (self):
		self.widget = tki.Tk ()
		
		self.clientView.createWidget ()
		self.clientView.configCell ()
		self.stretchRow ()
		self.stretchColumn ()
		
		return self.widget
		
	def execute (self):
		mainViewStore.load (self.viewStoreFileName)
		self.createWidget ()
		application.initializing = False
		self.widget.mainloop ()
		mainViewStore.save ()

	def exit (self):
		self.widget.Close ()
