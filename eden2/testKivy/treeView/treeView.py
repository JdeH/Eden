# Copyright (C) 2005, 2006 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# hello.py

from eden import *

treeNode = Node ([
	('ape', [
		('note', [
			'mice'
		]),
		('vim', [
			'sus',
			'jet'
		])
	])
])

selectedPathNode = Node ([])

selectedTreeNode = Node ()
selectedTreeNode.dependsOn ([selectedPathNode], lambda: cloneTree (treeNode.new, selectedPathNode.new))

mainView = MainView (VGridView ([
	TreeView (treeNode, selectedPathNode),
	TreeView (treeNode, selectedPathNode),
	TextView (treeNode),
	TreeView (selectedTreeNode),
	TextView (selectedTreeNode)
]), selectedTreeNode)

mainView.execute ()
