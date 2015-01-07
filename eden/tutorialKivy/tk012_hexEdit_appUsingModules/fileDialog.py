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

class FileDialog (Module):
# In a real world app maybe this module would just encapsulate a 3rd party file dialog.
# But with nodes and views it takes only little code to roll your own.
# Click on directories and files and see the button and label captions change.

	def __init__ (self, moduleName, save):
		Module.__init__ (self, moduleName)
		self.save = save
		
	def defineNodes (self):
		self.addNode (Node (), 'dialogCaptionNode')
		self.addNode (Node (None), 'openNode')
		self.addNode (Node (), 'closeNode')
		self.addNode (Node (), 'fileListNode')
		self.addNode (Node (), 'selectedFileListNode')
		
		self.addNode (Node (), 'directoryNode')
		self.addNode (Node (), 'fileNameNode', app.nodeStore)
		self.addNode (Node (), 'isDirNode')
		
		self.addNode (Node (), 'labelCaptionNode')
		self.addNode (Node (None), 'okNode')
		self.addNode (Node (), 'okCaptionNode')
		self.addNode (Node (None), 'cancelNode')
		
	def defineDependencies (self):
		self.dialogCaptionNode.dependsOn ([self.directoryNode, self.fileNameNode], lambda: self.directoryNode.new + '/' + self.fileNameNode.new)
		self.closeNode.dependsOn ([self.okNode, self.cancelNode], lambda: Pass if self.okNode.triggered and self.isDirNode.new else None)	# If a node gets value Pass, its actions are not executed.
		self.fileListNode.dependsOn ([self.directoryNode], lambda: ['..'] + os.listdir (self.directoryNode.new))
		self.selectedFileListNode.dependsOn ([self.fileListNode], lambda: self.fileListNode.new)
		
		self.directoryNode.dependsOn ([self.okNode], lambda: os.getcwd () .replace ('\\', '/'))
		self.fileNameNode.dependsOn ([self.selectedFileListNode], lambda: self.selectedFileListNode.new)
		self.isDirNode.dependsOn ([self.fileNameNode], lambda: os.path.isdir (self.fileNameNode.new))
		
		self.labelCaptionNode.dependsOn ([self.fileNameNode], lambda: 'Directory' if self.isDirNode.new else 'File')
		self.okCaptionNode.dependsOn ([self.fileNameNode], lambda: 'Change' if self.isDirNode.new else 'Save' if self.save else 'Load')
		
	def defineViews (self):
		def transform (fileName):
			if fileName == '..':
				return [fileName, '', 'directory']
			else: 
				return (fileName.split ('.') + ['']) [0:2] + ['directory' if os.path.isdir (fileName) else 'file']
	
		return ModalView (
			VGridView ([
				ListView (
					headerNode = ['Name', 'Extension', 'Type'],
					listNode = self.fileListNode,
					selectedListNode = self.selectedFileListNode,
					transformer = transform,
					actionNode = self.okNode,
					multiSelect = False
				), 15,
				HGridView ([
					LabelView (captionNode = self.labelCaptionNode),
					TextView (valueNode = self.fileNameNode), 6,
					ButtonView (captionNode = self.okCaptionNode, actionNode = self.okNode),
					ButtonView (captionNode = 'Cancel', actionNode = self.cancelNode)
				])
			]),
			captionNode = self.dialogCaptionNode,
			closeNode = self.closeNode,
			relativeSize = (0.5, 0.7)
		)
		
	def defineActions (self):
		self.openNode.addAction (self.getView () .execute)
		
		def onOk ():
			if self.isDirNode.new:
				os.chdir (self.fileNameNode.new)
		
		self.okNode.addAction (onOk) 
		