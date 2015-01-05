# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# layoutDesignAltered.py

from org.qquick.eden import *

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
		VGridView ([
			StretchView (),
			CLabelView ('ListView \'dialogRight\' gone'),
			StretchView ()
		]),
		key = 'dialogSplit'
	),
	'Fixed size dialog',
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
			VGridView ([
				StretchView (),
				CLabelView ('ListView \'mainLeft\' gone'),
				StretchView ()
			]),
			ListView (
				selectedPositiveNumbersNode,
				positiveNumberLabels,
				key = 'mainRight'
			),
			key = 'mainSplit'
		)
	]),
	'Altered',
	key = 'main'
)

# --- Actions

doFixedSizeDialog.action = fixedSizeDialog.execute

mainView.execute ()
