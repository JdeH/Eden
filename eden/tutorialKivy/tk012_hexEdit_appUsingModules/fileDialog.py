# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# fileDialog.py

import os

from org.qquick.eden import *

# This example shows some important strategies to manage cyclic dependecies between nodes.

class FileDialog (Module):
# In a real world app maybe this module would just encapsulate a 3rd party file dialog.
# But with nodes and views it takes only little code to roll your own.
# Click on directories and files and see the button and label captions change.

	def __init__ (self, moduleName, save):
		Module.__init__ (self, moduleName)
		self.save = save
		
		# If you're using modules, all nodes of a module can be traced by adding a single statement:
		# Tracing mutiple nodes is especially handy in case you're debugging a infinitely recursive node evaluation.
		# Currently tracing is done to a console window, eventually it will be optionally done to a log file.
		#
		self.trace = True
		#
		# In general, dependencies look like: aNode.dependsOn (aWatchedNodeList, anEvaluationFunction).
		# If a node in aWatchedNodeList is touched by the current event, anEvaluationFunction will be called to compute aNode.new.
		# Ff node A is in aWatchedNodeList of node B and node B is in aWatchedNodeList of node A, this is called cyclic dependency.
		# Cycles can involving more than two nodes are called indirect cyclic dependencies.
		#
		# Cyclic dependencies are allowed, but may require special measures with regard to anEvaluationFunction.
		# If this call is (directly or indirectly) infinitely recursive, an 'Recursive node evaluation' exception will be generated.
		# To deal with this, there are three solutions:
		#
		# In many cases this function will compute the new value from aNode from the new values of the nodes in aWatchedNode list.
		# But this does not have to be the case.
		#
		# Solution 1. In some cases the old rather than new values of the watched nodes can be used in the anEvaluationFunction.
		# Since these don't require computing, recursion is avoided.
		#
		# Solution 2. It is possible to watch for nodes in aWatchedNodeList to change, but to compute anEvaluationFunction from a different set of nodes.
		# So although nodes may watch each other mutually, the anEvaluationFunction need not be (directly or indirectly) recursive.
		#
		# Solution 3. Yet another way to avoid recursive evalution is to make the way use conditions in anEvaluationFunction.
		# The result is then made dependent on which node triggered the current event, or which nodes were touched by it.
		# This is in fact the classical way of 'conditionally' terminating recursion.
		#
		# Examples of all three approaches are in the code below in the defineDepencencies clause.
		
	def defineNodes (self):
		self.addNode (Node (None), 'openNode')
		self.addNode (Node (), 'closeNode')
		self.addNode (Node (), 'fileListNode')
		self.addNode (Node (), 'selectedFileListNode')
		
		self.addNode (Node (os.getcwd () .replace ('\\', '/')), 'directoryNode', app.nodeStore)
		self.addNode (Node ('..'), 'fileNameNode', app.nodeStore)
		self.addNode (Node (), 'pathNode')
		self.addNode (Node (), 'pathIsDirectoryNode')
		
		self.addNode (Node (), 'labelCaptionNode')
		self.addNode (Node (None), 'okNode')
		self.addNode (Node (), 'okCaptionNode')
		self.addNode (Node (None), 'cancelNode')
		
		self.addNode (Node (None), 'dirChangedNode')
		
	def defineDependencies (self):
		self.closeNode.dependsOn (	# Example of solution 1, using an old rather than a new node value.
			[self.okNode, self.cancelNode],
			lambda: Pass if self.okNode.triggered and self.pathIsDirectoryNode.old else None
		)
		# If a node gets value Pass, its actions are not executed.
		# In this case the dialog isn't closed if only a change of directory is performed.
		# Typically, Pass is used for 'event only' nodes, so nodes initialized with None, directly or via a dependency.
		
		self.fileListNode.dependsOn (
			[self.directoryNode],
			lambda: ['..'] + os.listdir (self.directoryNode.new)
		)
		
		self.selectedFileListNode.dependsOn (	# Example of solution 3, only using fileNameNode if the change wasn't caused by a changing fileListNode
			[self.fileListNode, self.fileNameNode],
			lambda: defaultSelectedList (self.fileListNode, self.selectedFileListNode, False) if self.fileListNode.touched else [self.fileNameNode.new]
		)
		# If a listNode changed, function defaultSelectedList (listNode, selectedListNode, multiSelect) will return the items that should be selected.
		# In most cases these are all the previously selected items that are still in the list.
		# The effect is that selections are maintained, even if the list changes.
		# If no explicit dependency is present for ListView.selectedListNode, function defaultSelectedList will be used implicitly.
		# So by default, a ListView maintain its selection if its list changes.
		
		self.directoryNode.dependsOn (	# Example of a combination of solution 1 and solution 2, okNode is not used in the evaluation and old values are used.
			[self.okNode],
			lambda: self.pathNode.old if self.pathIsDirectoryNode.old else self.directoryNode.old
		)
		
		self.fileNameNode.dependsOn (	# Example of a combination of solution 1 and solution 3.
			[self.selectedFileListNode],
			lambda: self.selectedFileListNode.new [0] if self.selectedFileListNode.triggered or self.fileListNode.touched else self.fileNameNode.old
		)
		
		self.pathNode.dependsOn (
			[self.directoryNode, self.fileNameNode],
			lambda: os.path.normpath ('{0}/{1}'.format (self.directoryNode.new, self.fileNameNode.new))
		)
		
		self.pathIsDirectoryNode.dependsOn (
			[self.pathNode], lambda: os.path.isdir (self.pathNode.new)
		)
		
		self.labelCaptionNode.dependsOn (
			[self.pathIsDirectoryNode],
			lambda: 'Directory' if self.pathIsDirectoryNode.new else 'File'
		)
		
		self.okCaptionNode.dependsOn (
			[self.pathIsDirectoryNode],
			lambda: 'Change' if self.pathIsDirectoryNode.new else 'Save' if self.save else 'Load'
		)
		
	def defineViews (self):
		def transform (fileName):
			if fileName == '..':
				return [fileName, '', 'directory']
			else:
				return (fileName.split ('.') + ['']) [0:2] + ['directory' if os.path.isdir ('{0}/{1}'.format (self.directoryNode.new, fileName)) else 'file']
	
		self.listView = ListView (
			headerNode = ['Name', 'Extension', 'Type'],
			listNode = self.fileListNode,
			selectedListNode = self.selectedFileListNode,
			transformer = transform,
			actionNode = self.okNode,
			multiSelect = False
		)
	
		return ModalView (
			VGridView ([
				self.listView, 15,
				HGridView ([
					LabelView (captionNode = self.labelCaptionNode),
					TextView (valueNode = self.fileNameNode), 6,
					ButtonView (captionNode = self.okCaptionNode, actionNode = self.okNode),
					ButtonView (captionNode = 'Cancel', actionNode = self.cancelNode)
				])
			]),
			captionNode = self.pathNode,
			closeNode = self.closeNode,
			relativeSize = (0.5, 0.7)
		)
		
	def defineActions (self):
		self.openNode.addAction (self.getView () .execute)
		# Actions are performed after all node evaluations are completed.
		# So any action can benefit from updated node values.
		
		def onOk ():
			if self.pathIsDirectoryNode.old:	# If a directory was selected before the button connected to okNode was clicked (so the old value, before the current event),
				os.chdir (self.pathNode.old)	# then the old path, visible in the header of the dialog before the curent event, is used as the new working directory.
		
		self.okNode.addAction (onOk) 
		