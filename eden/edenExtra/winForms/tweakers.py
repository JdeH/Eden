# Copyright (C) 2005, 2006 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

import clr

clr.AddReference ('System.Drawing')
clr.AddReference ('System.Windows.Forms')

from System import Drawing
from System.Windows import Forms

from eden.edenLib.base import *
from eden.edenLib.util import *
from eden.edenLib.view import *

class Font:
	Families = [Drawing.FontFamily.GenericMonospace, Drawing.FontFamily.GenericSansSerif, Drawing.FontFamily.GenericSerif]
	Fixed, PropSansSerif, PropSerif  = range (len (Families))
	
	Styles = [Drawing.FontStyle.Bold, Drawing.FontStyle.Italic, Drawing.FontStyle.Regular, Drawing.FontStyle.Strikeout, Drawing.FontStyle.Underline]
	Bold, Italic, Regular, StrikeOut, Underlined = range (len (Styles))
	
class Color:
	PlatformColors = [
		Drawing.Color.Black,
		Drawing.Color.Blue,
		Drawing.Color.Cyan,
		Drawing.Color.Gray,
		Drawing.Color.Green,
		Drawing.Color.Magenta,
		Drawing.Color.Orange,
		Drawing.Color.Red,
		Drawing.Color.White,
		Drawing.Color.Yellow,
	]
	
	PortableColorRange = range (len (PlatformColors))
	
	(
		Black,
		Blue,
		Cyan,
		Gray,
		Green,
		Magenta,
		Orange,
		Red,
		White,
		Yellow
	) = PortableColorRange

def tweakFont (view, family = Font.Fixed, size = 10, styles = [Font.Regular]):
	styleCombi = Font.Styles [styles [0]]
	
	for style in styles [1:]:
		styleCombi |= Font.Styles [style]
		
	view.widget.Font = Drawing.Font (Font.Families [family], size, styleCombi)

def tweakListViewColumnColors (listView, foregroundColors = None, backgroundColors = None, active = True):
	activeNode = getNode (active)
	
	def getPlatformColor (color):
		if color is None:
			return None
		elif color in Color.PortableColorRange:
			return Color.PlatformColors [color]
		else:
			return color
			
	if foregroundColors:
		foregroundColors = [getPlatformColor (color) for color in foregroundColors]

	if backgroundColors:
		backgroundColors = [getPlatformColor (color) for color in backgroundColors]	

	def tweakListViewItems ():
		if activeNode.new:
			for listViewItem in list (listView.widget.Items):
				listViewItem.UseItemStyleForSubItems = False
				
				for index, listViewSubItem in enumerate (list (listViewItem.SubItems)):				
					if index < len (foregroundColors) and foregroundColors [index] is not None:
						listViewSubItem.ForeColor = foregroundColors [index]

					if index < len (backgroundColors) and backgroundColors [index] is not None:
						listViewSubItem.BackColor = backgroundColors [index]
					
	listView.tweakListViewItems = tweakListViewItems

	def writeActive ():
		if activeNode.new:
			tweakListViewItems ()
		else:
			for listViewItem in list (listView.widget.Items):
				listViewItem.UseItemStyleForSubItems = True

		try:	# Fails if no items
			listView.widget.RedrawItems (0, listView.widget.Items.Count - 1, False)
		except:
			pass
			
	activeLink = Link (activeNode, None, writeActive)

def tweakListViewColumnLabelsOff (listView):
	listView.widget.HeaderStyle = Forms.ColumnHeaderStyle.None
	
def tweakToolBarViewMenu (toolBarView):
	toolBarView.widget.RenderMode = Forms.ToolStripRenderMode.Professional

	