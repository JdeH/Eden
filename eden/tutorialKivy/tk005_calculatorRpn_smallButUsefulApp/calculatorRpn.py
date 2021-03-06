# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# calculatorRpn.py

from org.qquick.eden import *

# --- Constants

digits = '0123456789'
operators = '+-*/'
open, terminated, entered = range (3)

# --- Persistence

nodeStore = Store ()

# --- Local nodes

doDigitNodes = [Node (None) .tagged (digit) for digit in digits]
doOperatorNodes = [Node (None) .tagged (operator) for operator in operators]
doDotNode = Node (None) .tagged ('.')
doChangeSignNode = Node (None) .tagged ('+/-')
doEnterNode = Node (None) .tagged ('enter')
doClearNode = Node (None) .tagged ('C')

doKeyNodes = doDigitNodes + doOperatorNodes + [doDotNode, doChangeSignNode, doEnterNode, doClearNode]

inputNode = Node ('')
stackNode = nodeStore.add (Node (['0', '0', '0', '0']))
stateNode = Node (terminated)
displayNode = Node ()

# --- Dependencies

inputNode.dependsOn (doKeyNodes, lambda: triggerNode () .tag)

def getStack ():
	o = stackNode.old
	if inputNode.new == '+/-': return [str (-1 * eval (o [0])), o [1], o [2], o [3]]
	elif inputNode.new in operators: return [str (eval ('1.*' + o [1] + inputNode.new + o [0])), o [2], o [3], o [3]]
	elif inputNode.new in digits + '.':
		if stateNode.old == terminated: return [inputNode.new, o [0], o [1], o [2]]
		elif stateNode.old == entered: return [inputNode.new, o [1], o [2], o [3]]
		else: return [o [0] + inputNode.new, o [1], o [2], o [3]]
	elif inputNode.new == 'enter': return [o [0], o [0], o [1], o [2]]
	else: return ['', o [1], o [2], o [3]]

stackNode.dependsOn ([inputNode], getStack)

def getState ():
	if inputNode.new in operators: return terminated
	elif inputNode.new == 'enter': return entered
	elif inputNode.new == '+/-': return stateNode.old
	else: return open
		
stateNode.dependsOn ([inputNode], getState)

displayNode.dependsOn ([stackNode], lambda: stackNode.new [0])

# --- Views

def key (tag):
	for doKeyNode in doKeyNodes:
		if doKeyNode.tag == tag:
			return ButtonView (doKeyNode, tag)
			
mainView = MainView (
	GridView ([
		[LabelView ('Press e.g.:   7 enter 8 *'), 4],
		[TextView (displayNode), 4],
		[key ('enter'), 2, key ('+/-'), 2], 2,
		[key (tag) for tag in '789/'],
		[key (tag) for tag in '456*'],
		[key (tag) for tag in '123-'],
		[key (tag) for tag in '0.C+']
	]), captionNode = 'RPN Calculator', fontScale = 5
)

nodeStore.load ()
mainView.execute ()
nodeStore.save ()

