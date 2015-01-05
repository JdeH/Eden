# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# helloDependsOn.py

from org.qquick.eden import *

nodeStore = Store ()

textNode1 = nodeStore.add (Node ('Hello'))
textNode2 = nodeStore.add (Node ('World'))

captionNode = Node ()
captionNode.dependsOn ([textNode1, textNode2], lambda: textNode1.new + ' ' + textNode2.new)

mainView = MainView (
	GridView ([
		[StretchView ()],
		[FillerView (), LLabelView ('First word'), TextView (textNode1), HExtensionView (), FillerView ()],
		[FillerView (), LLabelView ('Second word'), TextView (textNode2), HExtensionView (), FillerView ()],
		[StretchView ()]
	]), captionNode
)

nodeStore.load ('nodes.store')
mainView.execute ()
nodeStore.save ()