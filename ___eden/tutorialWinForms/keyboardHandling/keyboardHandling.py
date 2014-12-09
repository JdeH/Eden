# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# keyboardHandling.py

from eden import *

keysDownNode = Node (set ([]))
keysDownEventCountNode = Node (0)
keysDownEventCountNode.dependsOn ([keysDownNode], lambda: keysDownEventCountNode.old + 1)

keyCharNode = Node ('')
keyCharEventCountNode = Node (0)
keyCharEventCountNode.dependsOn ([keyCharNode], lambda: keyCharEventCountNode.old + 1)

keysUpNode = Node (set ([]))
keysUpEventCountNode = Node (0)
keysUpEventCountNode.dependsOn ([keysUpNode], lambda: keysUpEventCountNode.old + 1)


mainView = MainView (
	GridView ([
		[StretchView ()],
		[FillerView (), LLabelView ('Type something'), TextView (Node ('')), TextView (Node ('')), FillerView ()],
		[FillerView (), LLabelView ('Keys down'), LLabelView (keysDownNode), HExtensionView (), LLabelView (keysDownEventCountNode), FillerView ()],
		[FillerView (), LLabelView ('Keys up'), LLabelView (keysUpNode), HExtensionView (), LLabelView (keysUpEventCountNode), FillerView ()],
		[FillerView (), LLabelView ('Key char'), LLabelView (keyCharNode), HExtensionView (), LLabelView (keyCharEventCountNode), FillerView ()],
		[StretchView ()]
	]),
	'Keys a, b, and c never reach the TextView',
	keysDownNode = keysDownNode,
	keysUpNode = keysUpNode,
	keyCharNode = keyCharNode,
	keysHandled = lambda: keysDownNode.new & set ([Keys.A, Keys.B, Keys.C, Keys.Tab])
)

mainView.execute ()
