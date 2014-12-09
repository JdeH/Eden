# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# filePathDialog.py

from eden import *

fileListNode = Node ([])
doFileDialogNode = Node (None)

pathNode = Node ('c:/')
doPathDialogNode = Node (None)

mainView = MainView (
	VGridView ([
		ListView (fileListNode, ['Files']),
		HGridView ([
			ButtonView (doFileDialogNode, 'File dialog'),
			FillerView (), FillerView (),
		]),
		FillerView (),
		HGridView ([
			LLabelView ('Path'),
			TextView (pathNode),
			HExtensionView (),
		]),
		HGridView ([
			ButtonView (doPathDialogNode, 'Path dialog'),
			FillerView (), FillerView (),
		]),
	]),
	'File and path dialog',
)

doFileDialogNode.action = lambda: OpenFileView.show (fileListNode, 'Select bubble file', [
	('All bubble files (*.bubble)', ['.bubble']),
	('Only white and blue bubble files (*.white.bubble, *.blue.bubble)', ['.white.bubble', '.blue.bubble'])
], multiSelect = True)

doPathDialogNode.action = lambda: SelectPathView.show (pathNode, 'Select path')

mainView.execute ()

