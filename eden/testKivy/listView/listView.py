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

rd.seed ()

positions = ('left', 'in the middle', 'right')

headerNode = Node (['Something ' + position for position in positions])

nrOfItems = 50

listNode = Node ([
	['{0} {1} {0}'.format (position, rd.randint (1000, 1000 + nrOfItems)) for position in positions]
	for index in range (nrOfItems)
])

selectedListNode = Node ([])

mainView = MainView (VGridView ([
	TextView (headerNode),
	ListView (headerNode = headerNode, listNode = listNode, selectedListNode = selectedListNode), 2,
	TextView (headerNode),
	ListView (headerNode = headerNode, listNode = selectedListNode)
]), 'ListView')

mainView.execute ()
