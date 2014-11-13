# Copyright (C) 2005, 2006 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# focusDirection.py

from eden import *

Mountain, Valley = range (2)
radioNode = Node (0)

viewTupples = [
	(Keys.D1, TextView (Node ('Ocean'))),
	(Keys.D2, ComboView (Node ('Fox'), ['Fox', 'Dog'])),
	(Keys.D3, DeltaView (Node (0))),
	(Keys.D4, RadioButtonView (radioNode, 'Mountain', Mountain)),
	(Keys.D5, RadioButtonView (radioNode, 'Valley', Valley)),
	(Keys.D6, CheckView (Node (False), 'Inhabited')),
	(Keys.D7, ListView (Node (['Apple', 'Orange', 'Peach']), ['Fruit'])),
	(Keys.D8, TreeView (Node ([('Insects', ['Ants', 'Bugs', 'Bees'])])))
]

keysDownNode = Node (set ([]))

def onKeysDown ():
	if Keys.Alt in keysDownNode.new:
		for i in range (len (viewTupples)):
			if viewTupples [i][0] in keysDownNode.new:
				viewTupples [i][1] .focus ()

keysDownNode.action = onKeysDown

mainView = MainView (
	GridView ([[RLabelView (i + 1), viewTupples [i][1]] + 10 * [HExtensionView ()] for i in range (len (viewTupples))]),
	'Press [Alt] + <number> to direct the focus',
	keysDownNode = keysDownNode
)

mainView.execute ()
