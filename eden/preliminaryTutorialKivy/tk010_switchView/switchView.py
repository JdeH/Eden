# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# dropDownView.py

from eden import *
from collections import OrderedDict

nodeStore = Store ()

# === Nodes

# Eden was designed with serious, long lived, maintainable, modular applications in mind.
# In line with this, application LOGIC is considered far more important and far less volatile than application LOOKS.
#
# Hence a logical characteristic like mutual exclusiveness is in the NODES, not in the VIEWS.
# Maybe your app will not only be GUI driven, but e.g. also scriptable, or it has an HTML front-end, or it can also be controlled from the command line.
# Everything that's in the NODES rather than in the VIEWS will still work in all those cases.
#
# Standard radiobutton logic is rather limited.
# Why 1 out of n buttons, why not 2 or 3 out of n, or only certain meaningful combinations?
# With node dependcies you can code it all.

groupSize = 5

groupNodes = [Node (True)] + [Node (False) for i in range (1, groupSize)]	# Select one initially
freeNodes = [Node (False) for i in range (groupSize)]	# Select none initially

for groupNode in groupNodes:
	groupNode.dependsOn (groupNodes, lambda groupNode = groupNode: groupNode.triggered)	# Make nodes mutually exclusive	
	groupNode.addException (lambda groupNode = groupNode: groupNode.triggered and groupNode.old, Objection, 'Deselect only by selecting another')	# Block explicit deselection
	
captionNode = Node () .dependsOn (groupNodes + freeNodes, lambda: [node.new for node in (groupNodes + freeNodes)])
	
# === Views

def l (i):
	return 'Blahblah {0}'.format (i)

mainView = MainView (
	VGridView ([
		LabelView ('\nSelect one row'),
		HGridView ([
			VGridView ([SwitchView (stateNode = groupNodes [i], captionNode = l (i), kind = 'radio') for i in range (groupSize)]),
			VGridView ([SwitchView (stateNode = groupNodes [i], captionNode = l (i), kind = 'toggle') for i in range (groupSize)]),
			VGridView ([SwitchView (stateNode = groupNodes [i], captionNode = l (i), kind = 'check') for i in range (groupSize)]),
		]), 5,
		LabelView ('\nSelect / deselect any rows'),
		HGridView ([
			VGridView ([SwitchView (stateNode = freeNodes [i], captionNode = l (i), kind = 'radio') for i in range (groupSize)]),
			VGridView ([SwitchView (stateNode = freeNodes [i], captionNode = l (i), kind = 'toggle') for i in range (groupSize)]),
			VGridView ([SwitchView (stateNode = freeNodes [i], captionNode = l (i), kind = 'check') for i in range (groupSize)])
		]), 5
	]),
	captionNode = captionNode,
	fontScale = 1.5
)

nodeStore.load ()
mainView.execute ()
nodeStore.save ()
