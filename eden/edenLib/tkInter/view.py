# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

import TkinterDnD2 as tkd
import Tkinter as tki
import ttk
from copy import deepcopy
	
from ..node import *
from ..store import *

tkd.tkd = tkd.TkinterDnD

mainViewStore = Store ()
currentViewStore = CallableValue (mainViewStore)	# All applicable views will add themselves to currentViewStore ()
		
dragAction = None
dragModifiers = None
dragWidgetX = 0
dragWidgetY = 0
dragTreeViewTopMargin = 30
		
class MoverBase:
	def registerMove (self, actions = ('copy', 'move', 'link'), getTypes = ['text'], putTypes = ['text']):	# Currently only one getType and one putType
		self.actions = actions
		self.getTypes = getTypes
		self.putTypes = putTypes
		
		self.widget.drag_source_register (1, self.codeTypes (self.getTypes) [0])
		self.widget.drop_target_register (self.codeTypes (self.putTypes) [0])
		
		self.widget.dnd_bind ('<<DragInitCmd>>', self.dragInit)
		self.widget.dnd_bind ('<<DragEndCmd>>', self.dragEnd)
		self.widget.dnd_bind ('<<DropEnter>>', self.dropEnter)
		self.widget.dnd_bind ('<<DropPosition>>', self.dropPosition)
		self.widget.dnd_bind ('<<DropLeave>>', self.dropLeave)
		self.widget.dnd_bind ('<<Drop>>', self.drop)
		
		self.dragging = False
				
	def codeTypes (self, types):
		codedTypes = []
		for type in types:
			if type == 'text':
				codedTypes.append ('CF_TEXT')
			elif type == 'files':
				codedTypes.append ('DND_Files')
			else:
				codedTypes.append (type)
		return codedTypes
		
	def setDragAction (self, event):
		global dragAction
		dragAction = 'copy' if 'ctrl' in event.modifiers else 'move'
		# print 'Drag action: {0}'.format (dragAction)

	def dragInit (self, event):
		self.dragging = True
		return (self.actions, self.codeTypes (self.getTypes) [0], self.getPayload ())
						
	def dragEnd (self, event):
		if event.action == 'move':
			self.removePayload ()
	# print 'Drag end: {0}'.format (event.action)

	def dropEnter (self, event):
		global dragWidgetX
		dragWidgetX = event.widget.winfo_rootx ()

		global dragWidgetY
		dragWidgetY = event.widget.winfo_rooty ()
		
		return dragAction
	
	def dropPosition (self, event):
		self.xPosition = event.x_root - dragWidgetX
		self.yPosition = event.y_root - dragWidgetY
		
		self.setDragAction (event)
		# print event.actions, event.commonsourcetypes
		
		global dragModifiers
		dragModifiers = event.modifiers
		
		self.adaptPutPosition ()
		return dragAction
		
	def dropLeave (self, event):
		return dragAction
	
	def drop (self, event):
		if event.action == 'move':	# Remove after dropping since not ambiguous when dropped
			self.markForRemoval
		self.putPayload (event.data)
		return dragAction
		
	def getPayload (self): 
		return ''

	def adaptPutPosition (self):
		pass
			
	def putPayload (self, payload):
		pass
	
	def removePayload (self):
		pass
		
class ViewBase:
	def configCell (self, rowIndex = 0, columnIndex = 0, rowSpan = 1, columnSpan = 1):
		self.widget.grid (row = rowIndex, column = columnIndex, rowspan = rowSpan, columnspan = columnSpan, sticky = 'nsew' if self.stretch else 'new')
		
	def initWidget (self):
		self.stretch = False
		self.createWidget ()
		
		try:
			self.registerMove ()
		except:
			pass	# Does not inherit from Mover
	
		if hasattr (self, 'tweaker') and self.tweaker:
			tweaker (self)
		
class LabelViewBase (ViewBase):
	def __init__ (self, captionNode = None):
		self.captionNode = getNode (captionNode)
	
	def createWidget (self):
		self.widget = ttk.Label ()
		
		if self.captionNode:
			self.link = Link (self.captionNode, None, lambda: self.widget.config (text = str (self.captionNode.new)))
			self.link.write ()

		self.align ()
		
class LabelView (LabelViewBase):
	def align (self):
		pass
				
class ButtonViewBase (ViewBase):
	def __init__ (self, actionNode = None, captionNode = None, iconNode = None, tweaker = None):
		self.actionNode = getNode (actionNode)
		self.captionNode = getNode (captionNode)
		self.iconNode = getNode (iconNode)
		self.tweaker = tweaker
		
	def createWidget (self):
		self.widget = ttk.Button (self.parentView.widget, width = 1)
		
		if self.actionNode:
			self.actionLink = Link (self.actionNode, lambda params: self.actionNode.change (None, True), None)
			self.widget.config (command = self.actionLink.read)
		
		if self.captionNode:
			self.captionLink = Link (self.captionNode, None, lambda: self.widget.configure (text = str (self.captionNode.new)))
			self.captionLink.write ()
		
		if self.iconNode:
			self.iconLink = Link (self.iconNode, None, lambda: assignImage (self.widget, getImage (self.iconNode.new)))
			self.iconLink.write ()
		
class ButtonView (ButtonViewBase):
	pass
	
class StretchButtonView (ButtonViewBase):
	def initWidget (self):
		ButtonViewBase.initWidget (self)
		self.stretch = True
		
class TextViewBase (ViewBase):
	def __init__ (self, valueNode = None):
		self.valueNode = getNode (valueNode)
	
	def createWidget (self):
		self.createSpecializedWidget ()
		
		if self.valueNode:
			self.link = Link (self.valueNode, lambda params: self.valueNode.change (str (self.widget.Text)), lambda: (self.widget.delete (self.beginMarker, 'end'), self.widget.insert (self.beginMarker, str (self.valueNode.new))))
			self.link.write ()
		
	def terminate (self):
		self.link.read ()
		
class TextView (TextViewBase):
	def createSpecializedWidget (self):
		self.beginMarker = 0
		self.widget = ttk.Entry (master = self.parentView.widget, width = 1)
	
class StretchTextView (TextViewBase):
	def createSpecializedWidget (self):
		self.beginMarker = 1.0
		self.widget = tki.Text (master = self.parentView.widget, height = 1, width = 1)
		self.stretch = True
		
# <tree> = [<branch>, ...]
# <branch> = <item> | (<item>, <tree>)
# <item> = <field> | [<field>, ...]
# Each item has to be unique in its nearest enclosing tree

class TreeView (ViewBase, MoverBase):
	def __init__ (
		self,
		rootNode = None,
		tree = [],
		selectedBranches = [],	# Holds a list of references to selected branches
		columnHeaders = [],
		columnIndices = None,	# Display order of columns, should always contain column 0, e.g. [0, 3, 1]
		expansionLevel = 0		# Only root items visible
	):
		self.treeNode = getNode (treeNode)
		self.selectedBranchesNode = getNode (selectedBranches)
		self.columnHeadersNode = getNode (columnHeaders)
		self.columnIndicesNode = getNode (columnIndices)
		self.expansionLevelNode = getNode (expansionLevel)
		
		self.focusBranchNode = Node (None)
		self.expandedBranchesNode = Node ([])
		
		self.adornedTreeNode = Node ()
		
		self.adornedTreeNode.dependsOn (self.treeNode, self.selectedBranchesNode, self.focusBranchNode, self.expandedBranchesNode)
		self.selectedBranchesNode.dependsOn (self.adornedTreeNode)
		self.expandedBranchesNode.depensOn (self.adornedTreeNode)
		
		self.sortReverse = []
				
	def createWidget (self):
		self.widget = ttk.Treeview ()
		self.stretch = True
		
		self.treeLink = Link (self.treeNode, None, self.bareWriteTree)			
		self.selectionRootIdsLink = Link (self.selectionRootIdsNode, self.bareReadSelectionRootIds, None)
		self.focusIdLink = Link (self.focusIdNode, self.bareReadFocusId)
		self.columnHeadersLink = Link (self.columnHeadersNode, None, self.bareWriteTree)
			
		if self.columnIndicesNode:
			self.visibleColumnsLink = Link (self.columnIndicesNode, None, self.bareWriteTree)

		self.treeLink.write ()
	
		self.widget.bind ('<<TreeviewSelect>>', self.onTreeViewSelect)
		self.widget.bind ('<ButtonPress-1>', self.onButtonPress1)
				
	def bareWriteTree (self):
		# print 'Write'
		if len (self.sortReverse) != len (self.columnHeadersNode.new):
			self.sortReverse = [False for columnHeader in self.columnHeadersNode.new]
	
		if self.columnIndicesNode == None:
			columnIndices = range (len (self.columnHeadersNode.new))
		else:
			columnIndices = self.columnIndicesNode.new
	
		self.widget.delete (*self.widget.get_children ())
		self.widget.config (columns = ['#{0}'.format (index) for index in range (1, len (self.columnHeadersNode.new))], displaycolumns = ['#{0}'.format (index) for index in columnIndices [1:]])
		for iIndex, index in enumerate (columnIndices):
			self.widget.heading ('#{0}'.format (iIndex), text = self.columnHeadersNode.new [index], command = lambda index = index: self.sortTree (index))
			self.widget.column ('#{0}'.format (iIndex), anchor = 'center')
		self.branchDict = {}
		self.writeTreeRecursively (self.treeNode.new, '')
		# print 'End write'
		
	def writeTreeRecursively (self, tree, parentId):
		for branch in tree:
			if type (branch) == tuple:
				childItem = branch [0]
			else:
				childItem = branch
				
			if type (childItem) == list:
				childId = self.widget.insert (parentId, 'end', text = str (childItem [0]), values = childItem [1:])
			else:
				childId = self.widget.insert (parentId, 'end', text = str (childItem))
					
			self.branchDict [childId] = branch
				
			if type (branch) == tuple:
				self.writeTreeRecursively (branch [1], childId)

	def sortTree (self, columnIndex):
		newTree, newBranches = deepcopy (self.treeNode.new, self.selectedBranchesNode.new)
		self.sortTreeRecursively (newTree, columnIndex)
		self.sortReverse [columnIndex] = not self.sortReverse [columnIndex]
		self.treeNode.change (newTree)
		self.selectedBranchesNode.change (newBranches)
		
	def getColumn (self, item, columnIndex):
		try:
			return item [columnIndex]
		except:
			return None
		
	def sortTreeRecursively (self, newTree, columnIndex):
		newTree.sort (key = lambda branch:
			(	self.getColumn (branch [0], columnIndex)
				if type (branch [0]) == list else
				branch [0]
			) if type (branch) == tuple else (
				self.getColumn (branch, columnIndex)
				if type (branch) == list else
				branch
			),
			reverse = self.sortReverse [columnIndex]
		)
		for branch in newTree:
			if type (branch) == tuple:
				self.sortTreeRecursively (branch [1], columnIndex)
								
	def onButtonPress1 (self, event):
		self.xPosition = event.x
		self.yPosition = event.y
		self.setFocus ()
		self.focusIdLink.read ()
					
	def focus (self):
		focusId = self.identify_row
		self.widget.focus (self.identify_row (self.yPosition))
					
	def bareReadFocusId (self, params):
		return self.widget.identify_row (self.yPosition)
		
	def getFocusPath (self):
		focusBranch = None # ...
								
	def onTreeViewSelect (self, event):
		self.selectionRootIdsLink.read ()
				
	def bareReadSelectionRootIds (self, params):
		originalIds = self.widget.selection ()
		rootIds = [id for id in originalIds if not self.widget.parent (id) in originalIds]
		
		# Adapt view to always selecting complete branch
		closedIds = set (rootIds)
		self.addDescendantsRecursively (closedIds, originalIds)
		if closedIds != set (originalIds):
			self.widget.selection_set (' '.join (list (closedIds)))
			
		self.selectionRootIdsNode.change (rootIds)
			
	def addDescendantsRecursively (self, closedIds, parentIds):
		for parentId in parentIds:
			childIds = self.widget.get_children (parentId)
			closedIds.update (childIds)
			if childIds:
				self.addDescendantsRecursively (closedIds, childIds)
				
	def getSelectedBranches (self):
		return [self.branchDict [id] for id in self.selectionRootIdsNode.new]
		
	def getSelectionPaths (self):
		selectionPaths = []
		
		for rootId in self.selectionRootIdsNode.new:
			selectionPaths.append ([rootId])
			parentId = self.widget.parent (rootId)
			while parentId:
				selectionPaths [-1] .append (parentId)
				parentId = self.widget.parent (parentId)
			selectionPaths [-1].reverse ()
				
		return [[self.branchDict [id] for id in selectionPath] for selectionPath in selectionPaths]
				
	def removeSelectedBranches (self):
		newTree = deepcopy (self.treeNode.new)
				
		for selectionPath in self.selectionPathsNode.new:
			parentTree = newTree
			for selectionBranch in selectionPath [:-1]:
				for currentBranch in parentTree:
					if currentBranch [0] == selectionBranch [0]:	# Allways True for exactly one currentBranch in parentTree
						parentTree = currentBranch [1]
						break	# Advance one selectionBranch in the selectionPath
			parentTree.remove (selectionPath [-1])
					
		self.treeNode.change (newTree)
								
	def getPayload (self):
		return str (self.selectedBranchesNode.new)
		
	def adaptPutPosition (self):
		self.focus ()
	
	def putPayload (self, payload):
		originalFocusBranch = None
		originalParentBranch = None
		if not self.putId in ('top', 'bottom'):
			originalFocusBranch = self.branchDict [self.putId]
			parentId = self.widget.parent (self.putId)
			if parentId:
				originalParentBranch = self.branchDict [parentId]
			
		markedTree = deepcopy ((self.treeNode.new, originalFocusBranch, originalParentBranch))
		
		newTree = markedTree [0]
		focusBranch = markedTree [1]
		parentBranch = markedTree [2]
	
		branchesToInsert = eval (payload) # Only the first selected branch will be inserted
		
		if self.putId == 'top':	# Prepend new node as sibling to root node list (that may be empty)
			newTree [0:0] = branchesToInsert
		elif self.putId == 'bottom':	# Append new node as sibling to root node list (that may be empty)
			newTree += branchesToInsert
		else:		
			if 'shift' in dragModifiers:	# Prepend new node as first child of focus node
				if type (focusBranch) == tuple:	# Focus node has children already, prepend
					focusBranch [1][0:0] = branchesToInsert
				else:	# Turn focus node into a tuple so that it can have children
					if parentBranch:
						parentBranch [1][parentBranch [1] .index (focusBranch)] = (focusBranch, branchesToInsert)
					else:
						newTree [newTree.index (focusBranch)] = (focusBranch, branchesToInsert)
			else:	# Append node as sibling after focus node
				if parentBranch:
					index = parentBranch [1] .index (focusBranch) + 1
					parentBranch [1][index:index] = branchesToInsert
				else:
					index = newTree.index (focusBranch) + 1
					newTree [index:index] = branchesToInsert
			
		self.treeNode.change (newTree)
		
	def removePayload (self):
		self.removeSelectedBranches ()
		
class EmptyView (ViewBase):
	def initWidget (self):
		self.widget = ttk.Frame ()
		
class GridView (ViewBase):
	def __init__ (self, childViews):
		self.rows = []
		for rowOrWeight in childViews:
			if isinstance (rowOrWeight, int):
				self.rows [-1][1] = rowOrWeight
			elif rowOrWeight:
				self.rows.append ([[], 0])
				for viewOrSpan in rowOrWeight:
					if isinstance (viewOrSpan, int):
						self.rows [-1][0][-1][1] = viewOrSpan				
					elif viewOrSpan:
						self.rows [-1][0] .append ([viewOrSpan, 1])
					else:
						self.rows [-1][0] .append ([EmptyView (), 1])
			else:
				self.rows.append ([[[EmptyView (),1]], 0])
				
		for row in self.rows:
			for element in row [0]:
				element [0] .parentView = self

	def createWidget (self):
		self.widget = ttk.Frame (master = self.parentView.widget)
		
		maxNrOfColumns = 0
		for rowIndex, row in enumerate (self.rows):
			columnIndex = 0
			for element in row [0]:
				element [0] .initWidget ()
				element [0] .configCell (rowIndex, columnIndex, 1, element [1])
				columnIndex += element [1]
				maxNrOfColumns = max (maxNrOfColumns, columnIndex)
				
			self.widget.rowconfigure (rowIndex, weight = row [1], minsize = 22)
			if row [1]:
				self.stretch = True
				
		for columnIndex in range (maxNrOfColumns):
			self.widget.columnconfigure (columnIndex, weight = 1, minsize = 22)
		
class HGridView (GridView):
	def __init__ (self, childViews):
		GridView.__init__ (self, [childViews])
		
class VGridView (GridView):
	def __init__ (self, childViews):
		weightedRows = []
		for viewOrWeight in childViews:
			if isinstance (viewOrWeight, ViewBase):		
				weightedRows.append ([viewOrWeight])
			elif viewOrWeight == None:
				weightedRows.append ([])
			else:
				weightedRows.append (viewOrWeight)
		GridView.__init__ (self, weightedRows)
		
class MainView (ViewBase):
	def __init__ (
		self,
		clientView = EmptyView (),
		captionNode = '',
		key = None,
		fontScale = None,
	):
		self.clientView = clientView
		self.captionNode = getNode (captionNode)
		
		self.clientView.parentView = self
		application.mainView = self
		
		self.viewStoreFileName = 'views.store'
		currentViewStore () .add (self, key)
	
	def createWidget (self):
		self.widget = tkd.tkd.Tk ()
		self.clientView.initWidget ()
		self.clientView.configCell ()
		self.widget.rowconfigure (0, weight = 1)		
		self.widget.columnconfigure (0, weight = 1)
		
	def execute (self):
		mainViewStore.load (self.viewStoreFileName)
		self.initWidget ()
		application.initializing = False
		self.widget.mainloop ()
		mainViewStore.save ()

	def exit (self):
		self.widget.Close ()
