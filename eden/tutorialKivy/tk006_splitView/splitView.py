# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# splitView.py

from org.qquick.eden import *

MainView (
	VSplitView ([
		HSplitView ([
			LabelView ('Move'),
			LabelView ('The'),
			LabelView ('Splitters')
		]),
		HSplitView ([
			LabelView ('To'),
			LabelView ('See'),
			LabelView ('What')
		]),
		HSplitView ([
			LabelView ('Will'),
			LabelView ('Happen')
		]),
		HSplitView ([
			TextView (
				valueNode =
'''SPLITTER POSITIONS ARE PERSISTENT. Try closing and restarting this application.

Note that in the listview the first list column can be sorted alphanumerically, the second one numerically, without any special coding.

Unless you move your splitters in left to right and top down order, they suffer from entanglement and spooky action at a distance. Awaiting a new version of Kivy for these non-local effects to disappear.''',
				multiLine = True
			),
			TreeView (treeNode = [('o', ['be', 'a']), ('fine', ['girl', 'kiss','me'])]),
			ListView (headerNode = ['Animal', 'Legs'], listNode = [['Millipede', 1000], ['Centipede', 100], ['Ant', 6], ['Cow', 4], ['Chicken', 2], ['Snail', 1], ['Snake', 0]])
		])
	])
) .execute ()
