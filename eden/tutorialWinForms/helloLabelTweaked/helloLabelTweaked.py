# Copyright (C) 2005, 2006 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# helloLabelTweaked.py

from eden import *

# --- Definition of a simple tweaker

def tweak (view, color):
	view.widget.BackColor = color

# --- The above tweaker and two tweakers from eden.edenExtra/tweakers.py combined into one example

text = 'Who\'se afraid of red, yellow and green...'

mainView = MainView (
	VGridView ([
		FillerView (),
		CLabelView (
			text,
			tweaker = lambda view: chainCall (
				lambda: tweak (view, Drawing.Color.Red),
				lambda: tweakFont (view, family = Font.Fixed, size = 20, styles = [Font.Underlined, Font.Italic]),
			),
		),
		FillerView (),
		ListView (
			Node ([[row + col for col in range (3)] for row in range (10)]),
			['a', 'b', 'c'],
			tweaker = lambda listView: tweakListViewColumnColors (
				listView,
				[None, Color.Green, Drawing.Color.Blue],
				[None, Color.Orange, Drawing.Color.Yellow],
			),
		),
		FillerView ()
	]),
	text,
	tweaker = lambda view: tweak (view, Drawing.Color.LightGreen),
)

mainView.execute ()
