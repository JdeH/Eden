# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# localMenus.py

from org.qquick.eden import *
menuIndices = range (5)

def getNodes (kind):
	currentItemsNode = Node ([])
	
	# === Menu
	
	openMenuNode = Node (None)
	optionNodes = [Node (None) for i in menuIndices]
	closeMenuNode = Node () .dependsOn (optionNodes)
	
	resultNode = Node (''). dependsOn (
		[closeMenuNode],
		lambda: 'Action {0} done on:\n\n{1}'.format (
			# Attribute 'touched' of a node is True if it triggered or depended upon the most recent event
			[index for index, node in enumerate (optionNodes) if node.touched][0],
			' of ' .join (reversed (currentItemsNode.new)) if kind == 'tree' else '\n'.join (currentItemsNode.new)
		)
	)

	menuView = ModalView (
		VGridView ([ButtonView (actionNode = optionNodes [i], captionNode = 'Option {0}'.format (i)) for i in menuIndices]),
		closeNode = closeMenuNode,
		captionNode = Node () .dependsOn ([currentItemsNode], lambda: 'Menu for {0}, item {1}'.format (kind, currentItemsNode.new)),
		relativeSize = (0.3, 0.5)
	)
	
	openMenuNode.addAction (menuView.execute)
		
	# === Dialog
		
	openDialogNode = Node (None)
	closeDialogNode = Node (None)

	dialogView = ModalView (
		VGridView ([
			LabelView (captionNode = 'This may be a dialog\n of arbitrary complexity'),
			ButtonView (actionNode = closeDialogNode, captionNode = 'Close')
		]),
		closeNode = closeDialogNode,
		captionNode = Node () .dependsOn ([currentItemsNode], lambda: 'Dialog for {0}, item {1}'.format (kind, currentItemsNode.new)),
		relativeSize = (0.5, 0.4)
	)
	
	openDialogNode.addAction (dialogView.execute)
	
	return {'currentItems': currentItemsNode, 'openMenu': openMenuNode, 'openDialog': openDialogNode, 'result': resultNode}
	
pointedListNodes = getNodes ('pointed list')
selectedListNodes = getNodes ('selected list')	
treeNodes = getNodes ('tree')	
	
mainView = MainView (
	HSplitView ([
		VSplitView ([
			ListView (
				headerNode = ['One pointed star'],
				listNode = ['Alamak', 'Mirach', 'Sirrah'],
				pointedListNode = pointedListNodes ['currentItems'],
				actionNode = pointedListNodes ['openMenu'],
				otherActionNode = pointedListNodes ['openDialog']
			),
			LabelView (captionNode = pointedListNodes ['result'])
		]),
		VSplitView ([
			ListView (
				headerNode = ['Multiple selected planets'],
				listNode = ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune'],
				selectedListNode = selectedListNodes ['currentItems'],
				actionNode = selectedListNodes ['openMenu'],
				otherActionNode = selectedListNodes ['openDialog']
			),
			LabelView (captionNode = selectedListNodes ['result'])
		]),
		VSplitView ([
			TreeView (
				rootNode = 'One path from sun',
				treeNode = [('Earth', ['Moon']), ('Mars', ['Phoebos', 'Deimos']), ('Jupiter', ['Io', 'Europa', 'Ganymede', 'Callisto']), ('Saturn', ['Dione', 'Tethys', 'Rhea', 'Titan'])],
				pointedPathNode = treeNodes ['currentItems'],
				actionNode = treeNodes ['openMenu'],
				otherActionNode = treeNodes ['openDialog']
			),
			LabelView (captionNode = treeNodes ['result'])
		])
	]),
	captionNode = 'Double or triple click c.q. tap on items to lauch local menus and context dialogs',
	fontScale = 2
).execute ()

