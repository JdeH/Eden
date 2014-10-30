# Copyright (C) 2005, 2006 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

import kivy
kivy.require('1.8.0') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout

from eden.edenLib.node import *
from eden.edenLib.store import *

class EmptyView:
	def createWidget (self):
		self.widget = Label (text = 'Empty')
		
	def adaptFontSize (self):
		pass

class LabelView:
	def __init__ (self, captionNode = None):
		self.captionNode = getNode (captionNode)
		
	def setText (self, text):
		self.widget.text = str (text)
		
	def createWidget (self):
		self.widget = Label ()
		
		if self.captionNode:
			self.link = Link (self.captionNode, None, lambda: self.setText (self.captionNode.new))
			self.link.write ()
			
		return self.widget
		
	def adaptFontSize (self):
		self.widget.font_size = self.widget.height / 1.5

class ButtonView :
	def __init__ (self, actionNode = None, captionNode = None):
		self.actionNode = getNode (actionNode)
		self.captionNode = getNode (captionNode)

	def setText (self, text):
		self.widget.text = str (text)
		
	def createWidget (self):
		self.widget = Button ()
		
		if self.actionNode:
			self.actionLink = Link (self.actionNode, lambda params: self.actionNode.change (None, True), None)
			self.widget.on_press = self.actionLink.read
		
		if self.captionNode:
			self.captionLink = Link (self.captionNode, None, lambda: self.setText (self.captionNode.new))
			self.captionLink.write ()		
		
		return self.widget
		
	def adaptFontSize (self):
		self.widget.font_size = self.widget.height / 1.5
		
class TextView:
	def __init__ (self, valueNode = None):
		self.valueNode = getNode (valueNode)
		
	def setText (self, text):
		self.widget.text = str (text)
		
	def createWidget (self):
		self.widget = TextInput ()
		
		if self.valueNode:
			self.link = Link (self.valueNode, lambda params: self.valueNode.change (str (self.widget.Text)), lambda: self.setText (self.valueNode.new))
			self.link.write ()		
		
		return self.widget
		
	def adaptFontSize (self):
		pass
		
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
		
class GridView:
	def __init__ (self, childViews):
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
						
	def createWidget (self):
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
				self.stretch = True
			else:
				# self.nrOfRowCells += 1
				self.nrOfRowCells += rowIndex
				
		return self.widget
		
class HGridView (GridView):
	def __init__ (self, childViews):
		GridView.__init__ (self, [childViews])
		
class VGridView (GridView):
	def __init__ (self, childViews):
		weightedRows = []
		for viewOrWeight in childViews:
			if isinstance (viewOrWeight, ViewBase):		
				weightedRows.append ([viewOrWeight])
			elif viewOrWeight == None:
				weightedRows.append ([])
			else:
				weightedRows.append (viewOrWeight)
		GridView.__init__ (self, weightedRows)
		
class MainView (App):
	def __init__ (
		self,
		clientView = None,
		captionNode = '',
	):
		App.__init__ (self)
		self.clientView = clientView
		application.mainView = self
	
	def createWidget (self):
		self.widget = RelativeLayout ()
		self.widget.add_widget (self.clientView.createWidget ())
		return self.widget
		
	def build (self):
		return self.createWidget ()
		
	def execute (self):
		self.run ()
