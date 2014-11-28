# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# listView.py

import random as rd
from eden import *

positions = ('left', 'in the middle', 'right')
nrOfItems = 100

headerNode = Node (['Something ' + position for position in positions])

listNode = Node ([
	['{0} {1} {0}'.format (position, rd.randint (1000, 1000 + nrOfItems)) for position in positions]
	for index in range (nrOfItems)
])

pointedListNode = Node ([])
selectedListNode = Node ([])

list2Node = Node ([
	['{0} {1} {0}'.format (position, rd.randint (2000, 2000 + nrOfItems)) for position in positions]
	for index in range (nrOfItems)
])

pointedList2Node = Node ([])
selectedList2Node = Node ([])

mainView = MainView (GridView ([
	[TextView (headerNode), 41], 3,
	[
		ListView (headerNode = headerNode, listNode = listNode, pointedListNode = pointedListNode, selectedListNode = selectedListNode), 20,
		LabelView (),
		ListView (headerNode = headerNode, listNode = list2Node, pointedListNode = pointedList2Node, selectedListNode = selectedList2Node), 20,
	], 15,
	[LabelView (), 41],
	[
	 ListView (headerNode = headerNode, listNode = pointedListNode), 20,
	 LabelView (),
	 ListView (headerNode = headerNode, listNode = pointedList2Node), 20,
	], 10,
	[LabelView (), 41],
	[
	 ListView (headerNode = headerNode, listNode = selectedListNode), 20,
	 LabelView (),
	 ListView (headerNode = headerNode, listNode = selectedList2Node), 20,
	], 10,
]), 'ListView')

mainView.execute ()
