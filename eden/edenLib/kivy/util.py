# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

import os
from copy import *
from string import *

from eden.edenLib.base import *

try:
	from random import *
except:
	rand = -1
	
	def randint (fromInt, toInt):
		global rand
		
		rand += 1
				
		if rand > 20000:
			rand = 0
			
		return rand % (toInt - fromInt)

# --- Platform dependent imports

from platform import *

# --- File handling

def fileExists (fileName):
	try:
		file = open (fileName, 'r')
		file.close ()
		return True
	except:
		return False

# --- Some handy types

class CallableValue:
	def __init__ (self, value = None):
		self.value = value
		
	def __call__ (self):
		return self.value
	
class UniqueNumber (CallableValue):
	def __init__ (self, startValue = 0):
		CallableValue.__init__ (self)
		self.startValue = startValue
		self.reset ()
		
	def getNext (self):
		self.value += 1
		
		if hasattr (self, 'traceName'):
			print self.traceName, '=', self.value

		return self.value
		
	def reset (self):
		self.value = self.startValue
		
	def trace (self, traceName):
		self.traceName = traceName

class Keyed (object):
	def __init__ (self):
		self.keyNameList = []
		
	def setKey (self, keyName, value):
		setattr (self, keyName, value)
		self.keyNameList.append (keyName)
		
	keyValueList = property (lambda self: [getattr (self, keyName) for keyName in self.keyNameList])

	def __cmp__ (self, other):
		return cmp (self.keyValueList, other.keyValueList)
		
	def __repr__ (self):
		return self.keyValueList.__repr__ ()

# --- Some handy functions

def fullString (value):
	if value.__class__ == str:
		return value
	else:
		return (repr (value))
			
def lastItemFromList (aList, resultIfEmpty = None):
	length = len (aList)
	if length:
		return aList [length - 1]
	else:
		return resultIfEmpty
		
# --- Exception handling 

class Break (Exception):
	pass

app.remarkCaption = 'Remark'
app.remarkIcon = 'information'

app.objectionCaption = 'Objection'
app.objectionIcon = 'exclamation'

app.warningCaption = 'Warning'
app.warningIcon = 'warning'

app.errorCaption = 'Error'
app.errorIcon = 'error'

app.fatalErrorCaption = 'Fatal error'
app.fatalErrorIcon = 'error'

StackTraceUnavailable = '\n   at ??? (Stack trace not yet implemented for this exception type)'

class Notification (Exception):	# Rollback: no, precooked caption and icon: no
	def __init__ (self, message, caption, icon = '', report = ''):
		self.message = message
		self.caption = caption
		self.icon = icon
		self.report = report
	
class Remark (Notification): # Rollback: no, precooked label and icon: yes
	def __init__ (self, message, caption = app.remarkCaption, icon = app.remarkIcon, report = ''):
		Notification.__init__ (self, message, caption, icon, report)

class Refusal (Notification): # Rollback: yes, precooked caption and icon: no
	def __init (self, message, caption, icon = '', report = ''):
		Notification.__init__ (self, message, caption, icon, report)
	
class Objection (Refusal): # Rollback: yes, precooked caption and icon: yes
	def __init__ (self, message, caption = app.objectionCaption, icon = app.objectionIcon, report = ''):
		Refusal.__init__ (self, message, caption, icon, report)
	
class Warning (Objection): # Rollback: yes, precooked caption and icon: yes
	def __init__ (self, message, caption = app.warningCaption, icon = app.warningIcon, report = ''):
		Objection.__init__ (self, message, caption, icon, report)
		
class Error (Warning): # Rollback: yes, precooked caption and icon: yes
	def __init__ (self, message, caption = app.errorCaption, icon = app.errorIcon, report = ''):
		Warning.__init__ (self, message, caption, icon, report)

class FatalError (Error): # Rollback: yes, precooked caption and icon: no, will exit application.
	def __init__ (self, message, caption = app.fatalErrorCaption, icon = app.fatalErrorIcon, report = ''):
		Error.__init__ (self, message, caption, icon, report)

def printNotificationReport (notification):
	print notification.caption + ':', notification.report
	
app.notificationLogger = printNotificationReport
app.logNotifications = False

def printNotificationMessage (notification):
	print notification.caption + ':', notification.message
	
app.notificationShower = printNotificationMessage
app.showNotifications = True

app.handlingNotification = False
	
def defaultNotificationHandler (notification):
	app.handlingNotification = True
	
	if app.logNotifications and not notification.report is None:	# Passing None will avoid logging
		if not notification.report:
			notification.report = exReport (notification)
		app.notificationLogger (notification)
		
	if app.showNotifications and not notification.message is None:	# Passing None will avoid showing
		app.notificationShower (notification)

	app.handlingNotification = False

app.notificationHandler = defaultNotificationHandler

def handleNotification (notification):
	app.notificationHandler (notification)

def exReport (exception):
	report = str (exception) .capitalize ()
		
	try:
		report += '\n' + getStackTrace (exception)
	except:
		report += StackTraceUnavailable

	return report

def exMessage (exception):
	return str (exception) .capitalize ()
	
# --- Circumventing lambda function limitations before the introduction of conditional expressions

def ifExpr (condition, trueExpression, falseExpression):
	if condition:
		return trueExpression
	else:
		return falseExpression

def ifCall (condition, trueFunction, falseFunction):
	if condition:
		return trueFunction ()
	else:
		return falseFunction ()

def chainCall (procedure, function):
	procedure ()
	return function ()

# --- Automatic conversion

def getFunction (valueOrFunction, resultIfNone = None):
	if valueOrFunction is None:
		return resultIfNone
	else:
		if callable (valueOrFunction):
			return valueOrFunction
		else:
			return lambda: valueOrFunction
		
def getList (valueOrList, resultIfNone = None):
	if valueOrList is None:
		return resultIfNonde
	else:
		if valueOrList.__class__ == list:
			return valueOrList
		else:
			return [valueOrList]
		
def getAsTarget (value, targetClass):
	if value.__class__ == targetClass:
		return value
	elif value.__class__ == str and targetClass in [tuple, list, dict, set, bool]:	# Note the bool case
		return eval (value)
	else:
		return targetClass (value)													# Numbers to strings, strings to numbers
	
# --- List manipulation

def insertList (listToInsertInto, listToInsertAfter, listToInsert, inPlace = False, skipDupplicates = False):
	if skipDupplicates:
		localListToInsert = shrinkList (listToInsert, listToInsertInto)
	else:
		localListToInsert = listToInsert

		for item in localListToInsert:
			if item in listToInsertInto:
				raise Objection ('Can not insert dupplicate into list')
	
	if inPlace:
		localListToInsertInto = listToInsertInto
	else:
		localListToInsertInto = listToInsertInto [:]
	
	try:
		indexToInsertBefore = localListToInsertInto.index (listToInsertAfter [len (listToInsertAfter) - 1]) + 1
	except IndexError:
		indexToInsertBefore = 0
		
	localListToInsertInto [indexToInsertBefore : indexToInsertBefore] = localListToInsert
	
	return localListToInsertInto

def reorderList (listToReorder, listToMoveAfter, listToMove):
	localListToMove = [(None, item) for item in listToMove]
	localListToReorder = insertList (listToReorder, listToMoveAfter, localListToMove)
	shrinkList (localListToReorder, listToMove, True)
	
	for index, item in enumerate (localListToReorder):
		if item.__class__ == tuple and item [0] is None:
			localListToReorder [index] = item [1]
			
	return localListToReorder			

def appendList (listToAppendTo, listToAppend, inPlace = False, skipDupplicates = False):
	if skipDupplicates:
		localListToAppend = shrinkList (listToAppend, listToAppendTo)
	else:
		localListToAppend = listToAppend
		
		for item in localListToAppend:
			if item in listToAppendTo:
				raise Objection ('Can not append dupplicate to list')
			
	if inPlace:
		localListToAppendTo = listToAppendTo
	else:
		localListToAppendTo = listToAppendTo [:]
		
	localListToAppendTo.extend (localListToAppend)
	return localListToAppendTo

def shrinkList (listToSubtractFrom, listToSubtract, inPlace = False):
	if inPlace:
		localListToSubtractFrom = listToSubtractFrom
	else:
		localListToSubtractFrom = listToSubtractFrom [:]
		
	for item in listToSubtract:
		try:
			localListToSubtractFrom.remove (item)
		except ValueError:	# Removing an item that is not in the list is ok, shrinkList computes the 'set difference'
			pass
		
	return localListToSubtractFrom

def sortList (listToSort, columnNumber, transformer = None, inPlace = False):
	if transformer and len (listToSort):
		try:
			transformer (listToSort [0], 0)
			transformerHas2ndParam = True
		except TypeError:
			transformerHas2ndParam = False

	def compare (item1, item2):
		if columnNumber < 0:
			item1, item2 = item2, item1
			
		columnIndex = abs (columnNumber) - 1
		
		if transformer:
			if transformerHas2ndParam:
				transformedItem1 = transformer (item1, columnIndex)
				transformedItem2 = transformer (item2, columnIndex)
			else:
				transformedItem1 = transformer (item1)
				transformedItem2 = transformer (item2)

			return cmp (transformedItem1 [columnIndex], transformedItem2 [columnIndex])
		elif item1.__class__ == list:
			return cmp (item1 [columnIndex], item2 [columnIndex])
		else:
			return cmp (item1, item2)
						
	if inPlace:
		listToSort.sort (compare)
		return listToSort
	else:
		aList = sorted (listToSort, compare)
		return aList
		
def replaceList (listToReplaceIn, replacedList, replacementList, inPlace = False):
	if len (replacedList) == len (replacementList):
		if inPlace:
			localListToReplaceIn = listToReplaceIn
		else:
			localListToReplaceIn = listToReplaceIn [:]
			
		for replacedItemIndex, replacedItem in enumerate (replacedList):
			replacementItem = replacementList [replacedItemIndex]
			
			if replacementItem == replacedItem:
				continue
			elif replacementItem in localListToReplaceIn:
				raise Objection ('Can not add dupplicate to list')
			else:
				try:
					localListToReplaceIn [localListToReplaceIn.index (replacedItem)] = replacementItem
				except:
					raise Objection ('Can not replace item that is not in list')
		
		return localListToReplaceIn
	else:
		raise Objection ('Can not replace sublist by differently sized one')
			
def uniqueListId (aList, columnIndex = -1):
	if len (aList):
		if columnIndex == -1:
			columnIndex = len (aList [0]) - 1
			
		while True:
			candidate = randint (0, 10000)
			
			for item in aList:
				if item [columnIndex] == candidate:
					break	
			else:
				return candidate
	else:
		return 0
	
def uniqueIdList (aList, columnIndex = -1, inPlace = False):
	if inPlace:
		localList = aList
	else:
		localList = aList [:]

	if len (localList):			
		if columnIndex == -1:
			columnIndex = len (localList [0]) - 1
			
		for itemIndex, item in enumerate (localList):
			item [columnIndex] = itemIndex
	
	return localList
	
def flowFromList (aList, removeIdColumn = False):
	if removeIdColumn:
		sliceEnd = -1
	else:
		sliceEnd = None

	return join ([join ([fullString (field) for field in item [0 : sliceEnd]], '\t') for item in aList], '\n')

def listFromFlow (flow, fieldTypes, appendIdColumn = False):
	words = split (flow)
	nrOfColumns = len (fieldTypes)
	nrOfRows = len (words) / nrOfColumns
	wordIndex = 0
	rows = []
	
	for rowIndex in range (nrOfRows):
		row = []
		
		for columnIndex in range (nrOfColumns):
			row.append (fieldTypes [columnIndex] (words [wordIndex]))
			wordIndex += 1
			
		if appendIdColumn:
			row.append (None)
			
		rows.append (row)

	return rows
	
# --- Tree manipulation

def tupleFromBranch (branch):
	if branch.__class__ == tuple:
		return branch
	else:
		return (branch, [])
		
def itemFromBranch (branch):
	if branch.__class__ == tuple:
		return branch [0]
	else:
		return branch
		
def cloneTree (tree, path = None):
	if path == None:	# Clone whole tree, deepcopy may clone to much
		treeClone = []
		for branch in tree:
			if branch.__class__ == tuple:
				treeClone.append ((branch [0], cloneTree (branch [1])))
			else:
				treeClone.append (branch)
		return treeClone
	elif path == []:	# Clone empty tree
		return []
	else:	# Clone subtree, or whole tree if path == [rootItem]
		for item in path:
			for index in range (len (tree)):
				if tree [index].__class__ == tuple and item == tree [index][0]:
					branch = tree [index]
					tree = tree [index][1]
					break
				elif item == tree [index]:
					branch = tree [index]
					break		
		return cloneTree ([branch])
	
def cloneBranch (tree, path):
	return cloneTree (tree, path) [0]
	
def containsRoot (tree, branch):
	for treeBranch in tree:
		if itemFromBranch (treeBranch) == itemFromBranch (branch):
			return True
	return False

def insertBranch (treeToInsertInto, insertionPath, branchToInsert, asChild = False, inPlace = False):
	if inPlace:
		localTreeToInsertInto = treeToInsertInto
	else:
		localTreeToInsertInto = cloneTree (treeToInsertInto)
		
	tree = localTreeToInsertInto
	parentTree = None
	for item in insertionPath:
		for index in range (len (tree)):
			if tree [index] .__class__ == tuple and item == tree [index] [0]:
				break
			elif item == tree [index]:
				tree [index] = (tree [index], [])
				break
		parentTree = tree					
		tree = parentTree [index][1]
	
	if asChild:
		if containsRoot (tree, branchToInsert):
			raise Objection ('Can not insert dupplicate into tree')
		tree.insert (0, branchToInsert)	# Prepend to children of insertion node
	else:
		if parentTree is None:
			raise Objection ('Can not insert anything here')
		elif containsRoot (parentTree, branchToInsert):
			raise Objection ('Can not insert dupplicate into tree')
		parentTree.insert (index + 1, branchToInsert)	# Insert as sibling after insertionNode
	
	return localTreeToInsertInto
		
def editTree (treeToEdit, originPath, insertionPath, asChild = False, copy = False):
	if insertionPath [:len (originPath)] == originPath:
		if copy:
			raise Objection ('Cannot copy branch into itself')
		else:
			raise Objection ('Cannot move branch into itself')

	branchToMove = cloneBranch (treeToEdit, originPath)
	if copy:
		editedTree = cloneTree (treeToEdit)
	else:
		editedTree = removeBranch (treeToEdit, originPath)
	insertBranch (editedTree, insertionPath, branchToMove, asChild, True)
	return editedTree

def removeBranch (treeToRemoveFrom, removalPath):
	localTreeToRemoveFrom = cloneTree (treeToRemoveFrom)
	
	tree = localTreeToRemoveFrom
	for item in removalPath:
		for index in range (len (tree)):
			if tree [index].__class__ == tuple and item == tree [index][0]:
				parentTree = tree
				tree = tree [index][1]
				break
			elif item == tree [index]:
				parentTree = tree
				break							
	del parentTree [index]
	return localTreeToRemoveFrom
	
def insertPath (tree, insertionPath):
	lastItemIndex = len (insertionPath) - 1
	
	for itemIndex, item in enumerate (insertionPath):
		nonLeaf = itemIndex < lastItemIndex

		for branchIndex, branch in enumerate (tree):
			if branch.__class__ == tuple:
				if branch [0] == item:
					break
			elif branch == item:
				if nonLeaf:
					branch = tupleFromBranch (branch)
					tree [branchIndex] = branch
					break
				else:
					break
		else:
			if nonLeaf:
				branch = tupleFromBranch (item)				
			else:
				branch = item
			tree.append (branch)
			
		if nonLeaf:
			tree = branch [1]
			
def sortTree (tree):
	tree.sort ()
	for branch in tree:
		if branch.__class__ == tuple:
			sortTree (branch [1])
