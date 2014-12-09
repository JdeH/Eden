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

from eden import *

nodeStore = Store ()

nameNode = nodeStore.add (Node ('Change this'))
shownNode = nodeStore.add (Node ([1, 2, 3, 4]))
nrNode = nodeStore.add (Node (1))

# A tab with no text hides the page
tabsNode = Node () .dependsOn ([nameNode, shownNode], lambda: ['{0} {1}'.format (nameNode.new, index + 1) if index + 1 in shownNode.new else '' for index in range (4)])

# Mutual dependencies are OK here.
indexNode = Node () .dependsOn ([nrNode], lambda: nrNode.new - 1)
nrNode.dependsOn ([indexNode], lambda: indexNode.new + 1)

mainView = MainView (
	VGridView ([
		TabbedView (
			pageViews = [
				LabelView ('Long, long ago, in a far away land\n(Change page list below to hide pages, change number to switch page)'),
				TreeView (treeNode = [('there', ['was', 'a', 'king']), ('who', ['had', 'three', 'sons'])]),
				ListView (headerNode = ['Name', 'Character'], listNode = [['John', 'Brave'], ['William', 'Noble'], ['Jack', 'Strong']]),
				LabelView ('And they lived long and happy on the beach of Waikiki')
			],
			tabsNode = tabsNode,
			indexNode = indexNode
		), 10,
		HGridView ([
			TextView (valueNode = nameNode),
			TextView (valueNode = shownNode),
			TextView (valueNode = nrNode)
		])
	]),
	fontScale = 2
)

nodeStore.load ()
mainView.execute ()
nodeStore.save ()
