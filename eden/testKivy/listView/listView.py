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

listNode = Node ([
	['ape', 'aap', 'affe', 'singe'],
	['note', 'noot', 'nusz', 'detresse'],
	['mice', 'mies', 'maus', 'mais'],
	['vim', 'wim', 'wilhelm', 'schleifmittel'],
	['sus', 'zus', 'schwester', 'sous'],
	['jet', 'jet', 'duesenflugzeug', 'concorde'],
])

selectedPathNode = Node ([])

mainView = MainView (VGridView ([
	ListView (listNode = listNode)
]), 'ListView')

mainView.execute ()
