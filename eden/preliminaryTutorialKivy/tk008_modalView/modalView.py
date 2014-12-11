# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# modalView.py

from eden import *

application.debug = True	# Request detailed exeption reports, handy while experimenting

# ====== Nodes to launch and close modal views

closeMainNode = Node (None)

launch0Node = Node (None)	# A node initialized with None is an "event only" node, just meant to trigger an action but carrying no value
ok0Node = Node (None)
cancel0Node = Node (None)
close0Node = Node () .dependsOn ([ok0Node, cancel0Node])	# No evaluation function needed, since we're dealing with event only nodes

launch1Node = Node (None)
ok1Node = Node (None)
cancel1Node = Node (None)
close1Node = Node () .dependsOn ([ok1Node, cancel1Node])

# ====== Nodes to count the number of times the views were OK'ed or Canceled

countNode = Node ([0, 0, 0, 0])
captionNode = Node ()	# Not initialized, so this must be a dependent node

def getCount ():	# You can test if a node originated the current event (triggered) or if it was touched by the current event (touched).
	count = countNode.old
	if ok0Node.triggered:
		count [0] += 1
	elif cancel0Node.triggered:
		count [1] += 1
	elif ok1Node.triggered:
		count [2] += 1
	elif cancel1Node.triggered:
		count [3] += 1
	return count

countNode.dependsOn (
	[ok0Node, cancel0Node, ok1Node, cancel1Node],
	getCount
) .trace ('countNode')	# Use 'trace' to obtain debugging info about the successive contents of a node

captionNode.dependsOn (
	[countNode],
	lambda: 'Dialog 0: okayed {0} times, canceled {1} times\nDialog 1: okayed {2} times, canceled {3} times'.format (*countNode.new)
)

# ====== Views

mainView = MainView (
	GridView ([
		[], 3,
		[EmptyView (), ButtonView (captionNode = 'Press to launch dialog 0', actionNode = launch0Node), 2, EmptyView ()],
		[EmptyView (), LabelView (captionNode = captionNode), 2], 2,
		[], 3,
		[ButtonView (captionNode = 'Exit', actionNode = closeMainNode)]
	]),
	captionNode = 'Main window',
	closeNode = closeMainNode,
	fontScale = 2
)

dialog0 = ModalView (
	GridView ([
		[], 3,
		[EmptyView (), ButtonView (captionNode = 'Press to launch dialog 1', actionNode = launch1Node), 2, EmptyView ()],
		[], 4,
		[ButtonView (captionNode = 'OK', actionNode = ok0Node), ButtonView (captionNode = 'Cancel', actionNode = cancel0Node)]
	]),
	closeNode = close0Node,
	captionNode = 'Dialog 0'
)

dialog1 = ModalView (
	GridView ([
		[
			ListView (headerNode = ['eat', 'drink'], listNode = [['meat', 'red wine'], ['fish', 'white wine']]), 20,
			ListView (headerNode = ['mange', 'boive'], listNode = [['pain', 'lait'], ['soup', 'none']]), 20,
		], 8,
		[ButtonView (captionNode = 'OK', actionNode = ok1Node), 10, ButtonView (captionNode = 'Cancel', actionNode = cancel1Node), 10]
	]),
	closeNode = close1Node,
	captionNode = 'Dialog 1'
)

# ====== Actions

launch0Node.addAction (dialog0.execute)
launch1Node.addAction (dialog1.execute)

mainView.execute ()
