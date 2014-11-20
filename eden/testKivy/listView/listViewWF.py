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

from eden import *

positions = ('left', 'in the middle', 'right')

headerNode = Node (['Something ' + position for position in positions])

listNode = Node ([
	['{0} {1} {0}'.format (position, index) for position in positions]
	for index in range (10)
])

selectedListNode = Node ([])

mainView = MainView (VGridView ([
	ListView (listNode, ['a', 'b', 'c'], selectedListNode = selectedListNode)
]), 'ListView')

mainView.execute ()
