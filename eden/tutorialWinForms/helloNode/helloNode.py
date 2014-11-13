# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# helloNode.py

from eden import *

textNode = Node ('Hello, World')

mainView = MainView (
	GridView ([
		[StretchView ()],
		[FillerView (), CLabelView (textNode)],
		[CLabelView (textNode), TextView (textNode), CLabelView (textNode)],
		[FillerView (), CLabelView (textNode)],
		[StretchView ()]
	]), textNode
)

mainView.execute ()
