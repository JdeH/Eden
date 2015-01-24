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

from org.qquick.eden import *

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

textNode = Node ('hello')
textNode.trace ('textNode1')

text2Node = Node ('goodbye')

resultNode = Node () .dependsOn ([textNode, text2Node], lambda: textNode.new + ' ' + text2Node.new)

selectedPathNode = Node ([])

selectedTreeNode = Node ()
selectedTreeNode.dependsOn ([selectedPathNode, treeNode], lambda: cloneTree (treeNode.new, selectedPathNode.new))

MainView (VGridView ([
	TreeView (rootNode = resultNode, treeNode = treeNode, selectedPathNode = selectedPathNode), 7,
	LabelView ('Try editing the nodes in the textview below.'),
	TextView (treeNode, multiLine = True), 
	TreeView (rootNode = 'Selected branch', treeNode = selectedTreeNode), 7,
	TextView (textNode, multiLine = False),
	TextView (text2Node, multiLine = False)
]), selectedTreeNode) .execute ()
