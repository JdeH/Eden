# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# calculatorPush.py

from org.qquick.eden import *

def safeDivide (x, y):
	if y: return x / y
	else: raise Objection ('Divide by zero')	

# --- Local nodes

operand1Node = Node (0.0)
operand2Node = Node (0.0)
resultNode = Node (0.0)

doAddNode = Node (None)
doSubtractNode = Node (None)
doMultiplyNode = Node (None)
doDivideNode = Node (None)

# --- Views

mainView = MainView (
	VGridView ([
		HGridView ([
			LLabelView ('Result'),
			TextView (resultNode, editable = False),
			HExtensionView ()
		]),
		HGridView ([
			ButtonView (doAddNode, '+'),
			ButtonView (doSubtractNode, '-'),
			ButtonView (doMultiplyNode, '*'),
			ButtonView (doDivideNode, '/')
		]),
		HGridView ([
			LLabelView ('Operand 1'),
			TextView (operand1Node),
			HExtensionView ()
		]),
		HGridView ([
			LLabelView ('Operand 2'),
			TextView (operand2Node),
			HExtensionView ()
		])
	]), 'Push Calculator'
)

# --- Actions

doAddNode.action = lambda: resultNode.follow (operand1Node.new + operand2Node.new)
doSubtractNode.action = lambda: resultNode.follow (operand1Node.new - operand2Node.new)
doMultiplyNode.action = lambda: resultNode.follow (operand1Node.new * operand2Node.new)
doDivideNode.action = lambda: resultNode.follow (safeDivide (operand1Node.new, operand2Node.new))

mainView.execute ()
