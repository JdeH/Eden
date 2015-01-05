# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

from org.qquick.eden import *

store = Store ()

# --- 2 Dimensional grid page plus modal and modeless dialogs

x1 = store.add (Node (10.), 'x1')
x2 = Node ()
x3 = Node ()

x1.dependsOn ([x3], lambda: x3.new / 3)
x2.dependsOn ([x1], lambda: x1.new * 2)
x3.dependsOn ([x2], lambda: x2.new / 2 * 3)

captionRoot = store.add (Node ('number'), 'captionRoot')
twoDGridCaption = Node ('')
twoDGridCaption.dependsOn ([captionRoot], lambda: '2 D grids (' + captionRoot.new + ')')

x1Caption = Node ()
x1Caption.dependsOn ([captionRoot], lambda: captionRoot.new + ' times 1')

x2Caption = Node ()
x2Caption.dependsOn ([captionRoot], lambda: captionRoot.new + ' times 2')

x3Caption = Node ()
x3Caption.dependsOn ([captionRoot], lambda: captionRoot.new + ' times 3')

modalCaption = Node ()
modalCaption.dependsOn ([captionRoot, x1, x2, x3], lambda: captionRoot.new + ' modal ' + str (x1.new) + ' ' + str (x2.new) + ' ' + str (x3.new))
modalView = ModalView (HGridView ([RLabelView ('Caption root'), TextView (captionRoot)]), modalCaption)
doModal = Node (None)
doModal.action = modalView.execute

modelessCaption = Node ()
modelessCaption.dependsOn ([captionRoot, x1, x2, x3], lambda: captionRoot.new + ' modeless ' + str (x1.new) + ' ' + str (x2.new) + ' ' + str (x3.new))
modelessView = ModelessView (HGridView ([RLabelView ('Caption root'), TextView (captionRoot)]), modelessCaption)
doModeless = Node (None)
doModeless.action = modelessView.execute

twoDGridPage = GridView ([
	[RLabelView (x1Caption),								HExtensionView (),												TextView (x1, hint = lambda: 'One times ' + captionRoot.new),		LLabelView ('cats')	],
	[RLabelView (x2Caption),								HExtensionView (),												TextView (x2, hint = lambda: 'Two times ' + captionRoot.new),		LLabelView ('dogs')	],
	[RLabelView (x3Caption),								HExtensionView (),												TextView (x3, hint = lambda: 'Three times ' + captionRoot.new),		LLabelView ('frogs')],
	[ButtonView (doModal, modalCaption, hint = 'modal'),	HExtensionView (),												HExtensionView (),													EmptyView ()		],
	[EmptyView (),											ButtonView (doModeless, modelessCaption, hint = 'modeless'),	HExtensionView (),													HExtensionView ()	]
])

# --- Listviews & splitters page

nrOfItems = store.add (Node (20), 'nrOfItems')
columnCaptions = store.add (Node (['columnA', 'columnB', 'columnC']), 'columnCaptions')
selectedCaptions = Node ([])

captionToInsert = Node ('')
insertCaption = Node (None)
deleteCaption = Node (None)

columnCaptions.dependsOn ([insertCaption, deleteCaption],	lambda:
	ifCall (insertCaption.touched, lambda: insertList (columnCaptions.old, selectedCaptions.old, [captionToInsert.old]), lambda:
	shrinkList (columnCaptions.old, selectedCaptions.old))
) 

insertCaptionView = ModelessView (GridView ([
	[RLabelView ('Caption to insert'), TextView (captionToInsert)],
	[ButtonView (insertCaption, 'Insert')]
]), 'Insert caption')

showInsertCaptionView = Node (None)
showInsertCaptionView.action = insertCaptionView.execute

listContextMenuView = ContextMenuView ([MenuButtonView (showInsertCaptionView, 'Insert'), MenuButtonView (deleteCaption, 'Delete')])

aList = Node ()

aList.dependsOn ([columnCaptions, nrOfItems], lambda: [['item_' + str (itemIndex) + '_' + str (columnCaption) for columnCaption in columnCaptions.new] for itemIndex in range (nrOfItems.new)])

selectedList = Node ([])
checkedList = Node ([])

settingsView = VGridView ([
	ListView (columnCaptions, ['Column Captions'], contextMenuView = listContextMenuView, selectedListNode = selectedCaptions),
	HGridView ([RLabelView ('Items'), TextView (nrOfItems)]),
])

listPage = VSplitView (
	HSplitView (
		settingsView,
		HSplitView (
			VGridView ([
				LLabelView ('Selected'),
				ListView (selectedList, columnCaptions)
			]),
			VGridView ([
				LLabelView ('Checked'),
				ListView (checkedList, columnCaptions)
			])
		)
	),
	HSplitView (
		ListView (aList, columnCaptions, selectedListNode = selectedList, checkedListNode = checkedList),
		ListView (aList, columnCaptions, selectedListNode = selectedList, checkedListNode = checkedList)
	)	
)

# --- Treeviews & splitters page

labelRoot = store.add (Node ('bike'), 'labelRoot')
nrOfLevels = store.add (Node (3), 'nrOfLevels')
branching = store.add (Node (10), 'branching')

leafToInsert = Node ('')
insertLeaf = Node (None)
deleteSubTree = Node (None)

def createTree (labelRoot, nrOfLevelsToGo, branching):
	nrOfLevelsToGo -= 1
	tree = []
	for branchIndex in range (branching):
		label = labelRoot + '_' + str (branchIndex + 1)
		if nrOfLevelsToGo == 0:
			tree.append (label)
		else:
			tree.append ((label, createTree (label, nrOfLevelsToGo, branching)))
	return tree

tree = Node (createTree (labelRoot.new, nrOfLevels.new, branching.new))
selectedPath = Node ([])

tree.dependsOn ([insertLeaf, deleteSubTree, labelRoot, nrOfLevels, branching], lambda:
	ifCall (insertLeaf.touched, lambda: insertBranch (tree.old, selectedPath.old, [leafToInsert.old]), lambda:
	ifCall (deleteSubTree.touched, lambda: removeBranch (tree.old, selectedPath.old), lambda:
	createTree (labelRoot.new, nrOfLevels.new, branching.new)))
) 

def getNrOfNodes (tree, countedNodes):
	for branch in tree:		
		countedNodes = getNrOfNodes (tupleFromBranch (branch) [1], countedNodes) + 1
	return countedNodes

nrOfNodes = Node ()
nrOfNodes.dependsOn ([tree], lambda: 'Tree has: ' + str (getNrOfNodes (tree.new, 0)) + ' nodes')

insertLeafView = ModelessView (GridView ([
	[RLabelView ('Leaf to insert'), TextView (leafToInsert)],
	[ButtonView (insertLeaf, 'Insert')]
]), 'Insert leaf')

showInsertLeafView = Node (None)
showInsertLeafView.action = insertLeafView.execute

treeContextMenuView = ContextMenuView ([MenuButtonView (showInsertLeafView, 'Insert'), MenuButtonView (deleteSubTree, 'Delete')])

treeControlView = VGridView ([
	HGridView ([RLabelView ('Label root'), TextView (labelRoot)]), 
	HGridView ([RLabelView ('Levels'), TextView (nrOfLevels)]), 
	HGridView ([RLabelView ('Branching'), TextView (branching)]),
	CLabelView (nrOfNodes)
])

treePage = VSplitView (
	HGridView ([treeControlView, HSplitView (ListView (selectedPath, ['Selected path']), ListView (selectedPath, ['Selected path'])), HExtensionView ()]),
	TreeView (tree, selectedPathNode = selectedPath, contextMenuView = treeContextMenuView, expansionLevel = nrOfLevels)
)

# --- Paired lists page

listOperationsEnabled = Node (True)

def listClipboardGetter (mainListNode, selectedListNode, cutEventNode, copyEventNode, pasteEventNode, deleteEventNode):
	if cutEventNode.touched:
		clipboard.write (selectedListNode.old)
		return shrinkList (mainListNode.old, selectedListNode.old)
	elif copyEventNode.touched:
		clipboard.write (selectedListNode.old)
		return mainListNode.old
	elif pasteEventNode.touched:
		return insertList (mainListNode.old, selectedListNode.old, clipboard.read ())
	elif deleteEventNode.touched:
		return shrinkList (mainListNode.old, selectedListNode.old)
	else:
		return None
		
def getPairContextMenuView (cutEventNode, copyEventNode, pasteEventNode, deleteEventNode):
	return ContextMenuView ([
		MenuButtonView (cutEventNode, 'Cut', enabled = listOperationsEnabled),
		MenuButtonView (copyEventNode, 'Copy', enabled = listOperationsEnabled),
		MenuButtonView (pasteEventNode, 'Paste', enabled = listOperationsEnabled),
		MenuButtonView (deleteEventNode, 'Delete', enabled = listOperationsEnabled)
	])

# - Copy pair

copyLabel1 = store.add (Node ('Fruit'), 'copyLabel1')
copyLabel2 = store.add (Node ('Color'), 'copyLabel2')

copyLabels = Node ()
copyLabels.dependsOn ([copyLabel1, copyLabel2], lambda: [copyLabel1.new, copyLabel2.new])

leftCopyList = Node ([['apple', 'green'], ['orange', 'orange'], ['tomato', 'red'], ['banana', 'yellow']])
leftCopySelectedList = Node ([])
leftCopyHoverList = Node ([])

rightCopyList = store.add (Node ([]), 'rightCopyList')
rightCopySelectedList = Node ([])
rightCopyHoverList = Node ([])

addSelected = Node (None)
removeSelected = Node (None)

cutLeftCopy = Node (None)
copyLeftCopy = Node (None)
pasteLeftCopy = Node (None)
deleteLeftCopy = Node (None)

cutRightCopy = Node (None)
copyRightCopy = Node (None)
pasteRightCopy = Node (None)
deleteRightCopy = Node (None)

leftCopyList.dependsOn ([cutLeftCopy, copyLeftCopy, pasteLeftCopy, deleteLeftCopy], lambda:
	listClipboardGetter (leftCopyList, leftCopySelectedList, cutLeftCopy, copyLeftCopy, pasteLeftCopy, deleteLeftCopy)
)

rightCopyList.dependsOn ([addSelected, removeSelected, cutRightCopy, copyRightCopy, pasteRightCopy, deleteRightCopy], lambda:
	ifCall (addSelected.touched, lambda: appendList (rightCopyList.old, leftCopySelectedList.old), lambda:
	ifCall (removeSelected.touched, lambda: shrinkList (rightCopyList.old, rightCopySelectedList.old), lambda:
	listClipboardGetter (rightCopyList, rightCopySelectedList, cutRightCopy, copyRightCopy, pasteRightCopy, deleteRightCopy)))
)

rightCopyListView = None

leftCopyListView = ListView (
	listNode = leftCopyList,
	columnLabels = copyLabels,
	selectedListNode = leftCopySelectedList,
	contextMenuView = getPairContextMenuView (cutLeftCopy, copyLeftCopy, pasteLeftCopy, deleteLeftCopy),
		
	dragObjectGetter = lambda: leftCopySelectedList.new,
	dragResultGetter = lambda: leftCopyList.new,
	dropResultGetter = lambda afterItem:
		ifCall (dragObject.reflexive, lambda: reorderList (leftCopyList.new, afterItem, dragObject.value), lambda:
		ifCall (dragObject.imported, lambda: insertList (leftCopyList.new, afterItem, dragObject.value), lambda:
		leftCopyList.new)),		
	dropActionGetter = lambda:
		ifExpr (dragObject.reflexive, DropActions.Move,
		ifExpr (dragObject.imported or dragObject.sourceView is rightCopyListView, DropActions.Copy,
		DropActions.Null)),
		
	hoverListNode = leftCopyHoverList,
	hintGetter = lambda: leftCopyHoverList.new [0]
)

rightCopyListView = ListView (
	listNode = rightCopyList,
	columnLabels = copyLabels,
	selectedListNode = rightCopySelectedList,
	contextMenuView = getPairContextMenuView (cutRightCopy, copyRightCopy, pasteRightCopy, deleteRightCopy),

	dragObjectGetter = lambda: rightCopySelectedList.new,	
	dragResultGetter = lambda:
		ifCall (dragObject.reflexive or dragObject.exported, lambda: rightCopyList.new,	lambda:
		shrinkList (rightCopyList.new, dragObject.value)),		
	dropResultGetter = lambda afterItem:
		ifCall (dragObject.reflexive, lambda: reorderList (rightCopyList.new, afterItem, dragObject.value), lambda:
		insertList (rightCopyList.new, afterItem, dragObject.value)),
	dropActionGetter = lambda:
		ifExpr (dragObject.reflexive, DropActions.Move,
		ifExpr (dragObject.imported or dragObject.sourceView is leftCopyListView, DropActions.Copy,
		DropActions.Null)),
		
	hoverListNode = rightCopyHoverList,
	hintGetter = lambda: rightCopyHoverList.new [0]
)

copyPairView = HGridView ([
	leftCopyListView, HExtensionView (),
	VGridView ([
		CLabelView ('Copy'),
		ButtonView (addSelected, icon = 'rightArrowPlus', enabled = listOperationsEnabled, hint = 'Add selection to right list'),
		ButtonView (removeSelected, icon = 'leftCrossMinus', enabled = listOperationsEnabled, hint = 'Remove selection from right list')
	]),
	rightCopyListView, HExtensionView ()
])

# - Move pair

moveLabel1 = store.add (Node ('Weather'), 'moveLabel1')
moveLabel2 = store.add (Node ('Temp'), 'moveLabel2')

moveLabels = Node ()
moveLabels.dependsOn ([moveLabel1, moveLabel2], lambda: [moveLabel1.new, moveLabel2.new])

leftMoveList = store.add (Node ([['sun', 30], ['snow', 0], ['rain', 9], ['wind', 20]]), 'leftMoveList')
leftMoveSelectedList = Node ([])
leftMoveHoverList = Node ([])

rightMoveList = store.add (Node ([]), 'rightMoveList')
rightMoveSelectedList = Node ([])
rightMoveHoverList = Node ([])

moveSelection = Node (None)
moveSelectionBack = Node (None)

cutLeftMove = Node (None)
copyLeftMove = Node (None)
pasteLeftMove = Node (None)
deleteLeftMove = Node (None)

cutRightMove = Node (None)
copyRightMove = Node (None)
pasteRightMove = Node (None)
deleteRightMove = Node (None)

leftMoveList.dependsOn ([moveSelection, moveSelectionBack, cutLeftMove, copyLeftMove, pasteLeftMove, deleteLeftMove], lambda:
	ifCall (moveSelection.touched, lambda: shrinkList (leftMoveList.old, leftMoveSelectedList.old), lambda:
	ifCall (moveSelectionBack.touched, lambda: appendList (leftMoveList.old, rightMoveSelectedList.old), lambda:
	listClipboardGetter (leftMoveList, leftMoveSelectedList, cutLeftMove, copyLeftMove, pasteLeftMove, deleteLeftMove)))
)

rightMoveList.dependsOn ([moveSelection, moveSelectionBack, cutRightMove, copyRightMove, pasteRightMove, deleteRightMove], lambda:
	ifCall (moveSelection.touched, lambda: appendList (rightMoveList.old, leftMoveSelectedList.old), lambda:
	ifCall (moveSelectionBack.touched, lambda: shrinkList (rightMoveList.old, rightMoveSelectedList.old), lambda:
	listClipboardGetter (rightMoveList, rightMoveSelectedList, cutRightMove, copyRightMove, pasteRightMove, deleteRightMove)))
)

rightMoveListView = None

leftMoveListView = ListView (
	listNode = leftMoveList,
	columnLabels = moveLabels,
	selectedListNode = leftMoveSelectedList,
	contextMenuView = getPairContextMenuView (cutLeftMove, copyLeftMove, pasteLeftMove, deleteLeftMove),
	
	dragObjectGetter = lambda: leftMoveSelectedList.new,
	dragResultGetter = lambda:
		ifCall (dragObject.reflexive or dragObject.exported, lambda: leftMoveList.new, lambda:
		shrinkList (leftMoveList.new, dragObject.value)),
	dropResultGetter = lambda afterItem:
		ifCall (dragObject.reflexive, lambda: reorderList (leftMoveList.new, afterItem, dragObject.value), lambda:
		insertList (leftMoveList.new, afterItem, dragObject.value)),		
	dropActionGetter = lambda:
		ifExpr (dragObject.reflexive or dragObject.sourceView is rightMoveListView, DropActions.Move,
		ifExpr (dragObject.imported, DropActions.Copy,
		DropActions.Null)),
		
	hoverListNode = leftMoveHoverList,
	hintGetter = lambda: leftMoveHoverList.new [0]
)

rightMoveListView = ListView (
	listNode = rightMoveList,
	columnLabels = moveLabels,
	selectedListNode = rightMoveSelectedList,
	contextMenuView = getPairContextMenuView (cutRightMove, copyRightMove, pasteRightMove, deleteRightMove),
		
	dragObjectGetter = lambda: rightMoveSelectedList.new,
	dragResultGetter = lambda:
		ifCall (dragObject.reflexive or dragObject.exported, lambda: rightMoveList.new, lambda:
		shrinkList (rightMoveList.new, dragObject.value)),
	dropResultGetter = lambda afterItem:
		ifCall (dragObject.reflexive, lambda: reorderList (rightMoveList.new, afterItem, dragObject.value), lambda:
		insertList (rightMoveList.new, afterItem, dragObject.value)),		
	dropActionGetter = lambda:
		ifExpr (dragObject.reflexive or dragObject.sourceView is leftMoveListView, DropActions.Move,
		ifExpr (dragObject.imported, DropActions.Copy,
		DropActions.Null)),
		
	hoverListNode = rightMoveHoverList,
	hintGetter = lambda: rightMoveHoverList.new [0]
)

movePairView = HGridView ([
	leftMoveListView, HExtensionView (),
	VGridView ([
		CLabelView ('Move'),
		ButtonView (moveSelection, icon = 'rightArrow', enabled = listOperationsEnabled, hint = 'Move selection from left list to right list'),
		ButtonView (moveSelectionBack, icon = 'leftArrow', enabled = listOperationsEnabled, hint = 'Move selection from right list to left list')
	]),
	rightMoveListView, HExtensionView ()
])

# - Whole page

pairedListsPage = VGridView ([
	HGridView ([TextView (copyLabel1), TextView (copyLabel2), TextView (moveLabel1), TextView (moveLabel2)]),
	VSplitView (copyPairView, movePairView),
	CheckView (listOperationsEnabled, 'Enable list operations')
])

# --- Paired trees page

leftTree = store.add (Node ([
	('City', [
		('Buildings', [
			('Houses', ['Flats', 'Bungalows', 'Campers']),
			('Business estate', ['Shops', 'Offices', 'Factories']),
			('Religious buildings', ['Churches', 'Mosques', 'Synagogues'])
		]), 
		('Roads', [
			('Roads for cars', ['Highways', 'Main roads', 'Streets']),
			('Roads for bikes', ['Smooth bike roads', 'Bumpy bike roads', 'Muddy trails']),
			('Roads for pedestrians', ['Sidewalks', 'Promenades', 'Stairs'])
		]),
		('Nature', [
			('Public parks', ['Grass to play on', 'Trees to climb in', 'Robust flowers']),
			('Private parks', ['Grass to look at', 'Trees to sit under', 'Delicate flowers']),
			('Gardens', ['Grass for domestic animals', 'Small trees', 'Exotic flowers'])
		])
	])
]), 'leftTree')

rightTree = store.add (Node ([
	('Subjects', [
		('Big subjects', [
			('Noisy', ['Jet', 'Steel mill', 'Freight train']),
			('Audible', ['Elephant', 'Truck', 'Whale']),
			('Silent', ['Mountain', 'Tree', 'Cloud'])
		]), 
		('Not so big subjects', [
			('Noisy', ['Motor bike', 'Chain saw', 'PA system']),
			('Audible', ['Human being', 'Cat',	'Dish washer']),
			('Silent', ['Lamp post', 'Brick', 'Plant'])
		]),
		('Rather small subjects', [
			('Noisy', ['Cricket', 'Wasp', 'Whistle']),
			('Audible', ['Mosquito', 'Mouse', 'Music box']),
			('Silent', ['Strawberry', 'Glas of water', 'Piece of cake'])
		])
	])
]), 'rightTree')

leftSelectedPath = Node ([])
rightSelectedPath = Node ([])

leftHoverPath = Node ([])
rightHoverPath = Node ([])

def treeClipboardGetter (mainTreeNode, selectedBranchNode, cutEventNode, copyEventNode, pasteEventNode, deleteEventNode):
	if cutEventNode.touched:
		clipboard.write (cloneBranch (mainTreeNode.old, selectedBranchNode.old))
		return removeBranch (mainTreeNode.old, selectedBranchNode.old)
	elif copyEventNode.touched:
		clipboard.write (cloneBranch (mainTreeNode.old, selectedBranchNode.old))
		return mainTreeNode.old
	elif pasteEventNode.touched:
		return insertBranch (mainTreeNode.old, selectedBranchNode.old, clipboard.read ())
	elif deleteEventNode.touched:
		return removeBranch (mainTreeNode.old, selectedBranchNode.old)
	else:
		return None
		
def getTreePairContextMenuView (cutTreeEventNode, copyTreeEventNode, pasteTreeEventNode, deleteTreeEventNode):
	return ContextMenuView ([
		MenuButtonView (cutTreeEventNode, 'Cut'),
		MenuButtonView (copyTreeEventNode, 'Copy'),
		MenuButtonView (pasteTreeEventNode, 'Paste'),
		MenuButtonView (deleteTreeEventNode, 'Delete')
	])

cutLeftTree = Node (None)
copyLeftTree = Node (None)
pasteLeftTree = Node (None)
deleteLeftTree = Node (None)

cutRightTree = Node (None)
copyRightTree = Node (None)
pasteRightTree = Node (None)
deleteRightTree = Node (None)

moveTreeToRight = Node (None)
moveTreeToLeft = Node (None)
copyTreeToRight = Node (None)
copyTreeToLeft = Node (None)

leftTree.dependsOn ([moveTreeToRight, moveTreeToLeft, copyTreeToLeft, cutLeftTree, copyLeftTree, pasteLeftTree, deleteLeftTree], lambda:
	ifCall (moveTreeToRight.touched, lambda: removeBranch (leftTree.old, leftSelectedPath.old), lambda:
	ifCall (moveTreeToLeft.touched or copyTreeToLeft.touched, lambda: insertBranch (leftTree.old, leftSelectedPath.old, cloneBranch (rightTree.old, rightSelectedPath.old)), lambda:
	treeClipboardGetter (leftTree, leftSelectedPath, cutLeftTree, copyLeftTree, pasteLeftTree, deleteLeftTree)))
)

rightTree.dependsOn ([moveTreeToRight, moveTreeToLeft, copyTreeToRight, cutRightTree, copyRightTree, pasteRightTree, deleteRightTree], lambda:
	ifCall (moveTreeToLeft.touched, lambda: removeBranch (rightTree.old, rightSelectedPath.old), lambda:
	ifCall (moveTreeToRight.touched or copyTreeToRight.touched, lambda: insertBranch (rightTree.old, rightSelectedPath.old, cloneBranch (leftTree.old, leftSelectedPath.old)), lambda:
	treeClipboardGetter (rightTree, rightSelectedPath, cutRightTree, copyRightTree, pasteRightTree, deleteRightTree)))
)

rightTreeView = None

leftTreeView = TreeView (
	treeNode = leftTree,
	selectedPathNode = leftSelectedPath,
	contextMenuView = getTreePairContextMenuView (cutLeftTree, copyLeftTree, pasteLeftTree, deleteLeftTree),
	
	dragObjectGetter = lambda: (leftSelectedPath.new, cloneBranch (leftTree.new, leftSelectedPath.new)),
	dragResultGetter = lambda:
		ifCall (dragObject.dropAction == DropActions.Move and not dragObject.reflexive, lambda:	removeBranch (leftTree.new, leftSelectedPath.new), lambda:
		leftTree.new),
	dropResultGetter = lambda targetPath, after: 
		ifCall (dragObject.reflexive, lambda: reorderTree (leftTree.new, dragObject.value [0], targetPath, after), lambda:
		insertBranch (leftTree.new, targetPath, dragObject.value [1], after)),
	dropActionGetter = lambda:
		ifExpr (Keys.Control in dragObject.modifiers, 
			ifExpr (dragObject.sourceView is rightTreeView, 
				DropActions.Copy,
				DropActions.Null),
			DropActions.Move),
		
	hoverPathNode = leftHoverPath,	
	hintGetter = lambda: leftHoverPath.new
)

rightTreeView = TreeView (
	treeNode = rightTree,
	selectedPathNode = rightSelectedPath,
	contextMenuView = getTreePairContextMenuView (cutRightTree, copyRightTree, pasteRightTree, deleteRightTree),
	
	dragObjectGetter = lambda: (rightSelectedPath.new, cloneBranch (rightTree.new, rightSelectedPath.new)),
	dragResultGetter = lambda:
		ifCall (dragObject.dropAction == DropActions.Move and not dragObject.reflexive, lambda: removeBranch (rightTree.new, rightSelectedPath.new), lambda:
		rightTree.new),
	dropResultGetter = lambda targetPath, after:
		ifCall (dragObject.reflexive, lambda: reorderTree (rightTree.new, dragObject.value [0], targetPath, after), lambda:
		insertBranch (rightTree.new, targetPath, dragObject.value [1], after)),
	dropActionGetter = lambda:
		ifExpr (Keys.Control in dragObject.modifiers, 
			ifExpr (dragObject.sourceView is leftTreeView, 
				DropActions.Copy,
				DropActions.Null),
			DropActions.Move),
			
	hoverPathNode = rightHoverPath,	
	hintGetter = lambda: rightHoverPath.new
)

pairedTreesPage = HGridView ([
	leftTreeView, HExtensionView (),
	VGridView ([
		CLabelView ('Copy'),
		ButtonView (copyTreeToRight, icon = 'rightArrowPlus', hint = 'Copy selected branch to right tree'),
		ButtonView (copyTreeToLeft, icon = 'leftArrowPlus', hint = 'Copy selected branch to left tree'),
		EmptyView (),
		CLabelView ('Move'),
		ButtonView (moveTreeToRight, icon = 'rightArrow', hint = 'Move selected branch to right tree'),
		ButtonView (moveTreeToLeft, icon = 'leftArrow', hint = 'Move selected branch to left tree')
	]),
	rightTreeView, HExtensionView ()
])

# --- Checkboxes and radio buttons page

itRainsOutside = store.add (Node (True), 'itRainsOutside')
iWearAnUmbrella = store.add (Node (False), 'iWearAnUmbrella')
iGetWet = Node ()

iGetWet.dependsOn ([itRainsOutside, iWearAnUmbrella], lambda: itRainsOutside.new and not iWearAnUmbrella.new) 

foodLabels = ['Meat', 'Fish', 'Vegetarian']
foodMarker = store.add (Node (foodLabels [0]), 'foodMarker')

drinkLabels = ['Coffee', 'Tea', 'Water']
drinkMarker = store.add (Node (drinkLabels [0]), 'drinkMarker')

showWhatLabels = ['Food', 'Drink']
showWhatMarker = store.add (Node (showWhatLabels [0]), 'showWhatMarker')

foodOrDrinkOptions = Node ()
foodOrDrinkOptions.dependsOn ([showWhatMarker], lambda: ifExpr (showWhatMarker.new == 'Food', foodLabels, drinkLabels))

def evaluateFoodOrDrink ():
	if triggerNode () == foodMarker:
		if showWhatMarker.old == 'Food':
			return foodMarker.new
	elif triggerNode () == drinkMarker:
		if showWhatMarker.old == 'Drink':
			return drinkMarker.new
	else:
		if showWhatMarker.new == 'Food':
			return foodMarker.old
		else:
			return drinkMarker.old
	return foodOrDrink.old
	
foodOrDrink = Node ()
foodOrDrink.dependsOn ([showWhatMarker, foodMarker, drinkMarker], evaluateFoodOrDrink)

foodMarker.dependsOn ([foodOrDrink], lambda: ifCall (showWhatMarker.new == 'Food', lambda: foodOrDrink.new, lambda: foodMarker.old))
drinkMarker.dependsOn ([foodOrDrink], lambda: ifCall (showWhatMarker.new == 'Drink', lambda: foodOrDrink.new, lambda: drinkMarker.old))

checksRadiosCombosPage = HGridView ([
	VGridView ([
		CheckView (itRainsOutside, 'It rains outside', hint = 'As often in the Netherlands'),
		CheckView (iWearAnUmbrella, 'I wear an umbrella', hint = 'As often in Brittain'),
		CheckView (iGetWet, 'I get wet', hint = 'Just like under the shower'),
		GroupView (VGridView ([
			RadioButtonView (showWhatMarker, 'Food', hint = 'If you are hungry'),
			RadioButtonView (showWhatMarker, 'Drink', hint = 'If you are thirsty')
		]), 'combo shows'),
		ComboView (foodOrDrink, foodOrDrinkOptions, hint = 'Another way to choose')
	]),
	VGridView ([
		GroupView (VGridView ([
			RadioButtonView (foodMarker, foodLabels [0], hint = 'No ' + foodLabels [1] + ' or ' + foodLabels [2]),
			RadioButtonView (foodMarker, foodLabels [1], hint = 'No ' + foodLabels [0] + ' or ' + foodLabels [2]),
			RadioButtonView (foodMarker, foodLabels [2], hint = 'No ' + foodLabels [0] + ' or ' + foodLabels [1])
		]), 'food'),
		GroupView (VGridView ([
			RadioButtonView (drinkMarker, drinkLabels [0], hint = 'No ' + drinkLabels [1] + ' or ' + drinkLabels [2]),
			RadioButtonView (drinkMarker, drinkLabels [1], hint = 'No ' + drinkLabels [0] + ' or ' + drinkLabels [2]),
			RadioButtonView (drinkMarker, drinkLabels [2], hint = 'No ' + drinkLabels [0] + ' or ' + drinkLabels [1])
		]), 'drinks')
	])
])

# --- Main view
	
tabbedView = TabbedView ([
	PageView (twoDGridPage, captionRoot),
	PageView (listPage, 'lists & splitters'),
	PageView (treePage, 'trees & splitters'),
	PageView (pairedListsPage, 'paired lists'),
	PageView (pairedTreesPage, 'paired trees'),
	PageView (checksRadiosCombosPage, 'checks & radios & combos')
])

cat = Node (None)
dog = Node (None)
greekLandTurtle = Node (None)
boxTurtle = Node (None)
sunFlower = Node (None)
rose =  Node (None)

menuBarView = MenuBarView ([
	MenuListView ([
		MenuButtonView (cat, 'Cat'),
		MenuButtonView (dog, 'Dog'),
		MenuSeparatorView (),
		MenuListView ([
			MenuButtonView (greekLandTurtle, 'Greek land turtle'),
			MenuButtonView (boxTurtle, 'Box turtle')		
		], 'Turtle')
	], 'Animals'),
	MenuListView ([
		MenuButtonView (sunFlower, 'Sun flower'),
		MenuButtonView (rose, 'Rose')
	], 'Plants')
])

captionNode = Node ('Eden - Demo')

captionNode.dependsOn ([cat, dog, greekLandTurtle, boxTurtle, sunFlower, rose], lambda:
	ifExpr (cat.touched, 'The cat climbs into the tree', 
	ifExpr (dog.touched, 'The dog barks and wags its tail',
	ifExpr (greekLandTurtle.touched, 'The greek land turtle likes eating leaves',
	ifExpr (boxTurtle.touched, 'The box turtle has a curved neck',
	ifExpr (sunFlower.touched, 'The sunflower makes the landscape look sunny',
	'The rose has lend its name to many girls')))))
)

mainView = MainView (tabbedView, captionNode, menuBarView, application.projectDirectory + '/views.store')

store.load (application.projectDirectory + '/nodes.store')
mainView.execute ()
store.save (application.projectDirectory + '/nodes.store')
