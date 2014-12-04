# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# treeView.py

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
selectedTreeNode.dependsOn ([selectedPathNode, treeNode], lambda: cloneTree (treeNode.new, selectedPathNode.new))

MainView (VGridView ([
	TreeView (rootNode = 'Whole tree', treeNode = treeNode, selectedPathNode = selectedPathNode), 7,
	LabelView ('Try editing the nodes in the textview below.'),
	TextView (treeNode), 
	TreeView (rootNode = 'Selected branch', treeNode = selectedTreeNode), 7
]), selectedTreeNode) .execute ()
