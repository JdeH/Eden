# Copyright (C) 2005, 2006 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# layoutDesignOriginal.py

from eden import *

application.designMode = True

# --- Local nodes

selectedPositiveNumbersNode = Node ([])
selectedNegativeNumbersNode = Node ([])

doFixedSizeDialog = Node (None)

# --- Views

negativeNumberLabels = ['-i', '10 * -i', '100 * -i']

fixedSizeDialog = ModelessView (
	HSplitView (
		ListView (
			Node ([[-i, 10 * -i, 100 * - i] for i in range (100)]),
			negativeNumberLabels,
			selectedListNode = selectedNegativeNumbersNode,
			key = 'dialogLeft'

		),
		ListView (
			selectedNegativeNumbersNode,
			negativeNumberLabels,
			key = 'dialogRight'
		),
		key = 'dialogSplit'
	),
	'Fixed size dialog, select items to fill second ListView',
	fixedSize = True,
	key = 'dialog'
)

positiveNumberLabels = ['i', '10 * i', '100 * i']

mainView = MainView (
	VGridView ([
		FillerView (),
		HGridView ([FillerView (), ButtonView (doFixedSizeDialog, 'Show fixed size dialog'), FillerView ()]),
		FillerView (),
		HSplitView (
			ListView (
				Node ([[i, 10 * i, 100 * i] for i in range (100)]),
				positiveNumberLabels,
				selectedListNode = selectedPositiveNumbersNode,
				key = 'mainLeft'
			),
			ListView (
				selectedPositiveNumbersNode,
				positiveNumberLabels,
				key = 'mainRight'
			),
			key = 'mainSplit'
		)
	]),
	'Original, select items to fill second ListView',
	key = 'main'
)

# --- Actions

doFixedSizeDialog.action = fixedSizeDialog.execute

mainView.execute ()
