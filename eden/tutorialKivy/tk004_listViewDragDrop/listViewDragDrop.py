# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# listViewDragDrop.py

import random as rd
from org.qquick.eden import *

columnIndices = range (3)

# === General nodes

itemKindNode = Node ('thingy')

nrOfItemsNode = Node (50) .addException (
	lambda currentValue: currentValue < 0 or currentValue > 200,
	Objection,
	'Nr of items should be in range 0..200'
)

headerNode = Node () .dependsOn (
	[itemKindNode],
	lambda: ['{0} col {1}'.format (itemKindNode.new.upper (), i + 1) for i in columnIndices]
)

# === Nodes for lists on the left

leftListNode = Node () .dependsOn (
	[itemKindNode, nrOfItemsNode],
	lambda: [
		['Left {0}'.format (rd.randint ((i + 1) * 1000, (i + 1) * 1000 + nrOfItemsNode.new)) for i in columnIndices]
		for index in range (nrOfItemsNode.new)
	]
)

leftSelectedListNode = Node ([])
leftPointedListNode = Node ([])

# === Nodes for lists on the right

rightListNode = Node () .dependsOn (
	[itemKindNode, nrOfItemsNode],
	lambda: [
		['Right {0}'.format (rd.randint ((i + 1) * 1000, (i + 1) * 1000 + nrOfItemsNode.new)) for i in columnIndices]
		for index in range (nrOfItemsNode.new)
	]
)

rightSelectedListNode = Node ([])
rightPointedListNode = Node ([])

# === Views

MainView (GridView ([
	[LabelView (
'''
You can:
- Change the item kind and the total nr of items in the edit widgets
  (Having > 200 items will give an error message in the console window)
- Adjust the column size by moving the splitters
- Scroll items by moving the pointer up and down over the list contents
- Sort ascending or descending per column by clicking the column headers 
- Select multiple items from the main lists by clicking on them
- After selecting items, drag them from one main list to the other main list by starting to move the pointer to left or right
- Turn a drag move into a drag copy by waiting a second close to the starting point of the drag
- Reorder the main lists by drag and drop
'''
	), 41], 6,
	[	TextView (itemKindNode), 20,
		LabelView (),
		TextView (nrOfItemsNode), 20
	],
	[LabelView ('\n Main lists\n'), 41],
	[
		ListView (headerNode = headerNode, listNode = leftListNode, pointedListNode = leftPointedListNode, selectedListNode = leftSelectedListNode), 20,
		LabelView (),
		ListView (headerNode = headerNode, listNode = rightListNode, pointedListNode = rightPointedListNode, selectedListNode = rightSelectedListNode), 20,
	], 8,
	[LabelView ('\n Lists of items that pointer moves over while touching\n'), 41],
	[
	 ListView (headerNode = headerNode, listNode = leftPointedListNode), 20,
	 LabelView (),
	 ListView (headerNode = headerNode, listNode = rightPointedListNode), 20,
	], 5,
	[LabelView ('\n List of selected items\n'), 41],
	[
	 ListView (headerNode = headerNode, listNode = leftSelectedListNode), 20,
	 LabelView (),
	 ListView (headerNode = headerNode, listNode = rightSelectedListNode), 20,
	], 5,
]), 'ListView') .execute ()
