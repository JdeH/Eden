# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# circleSingleCycle.py

from math import *
from eden import *

nodeStore = Store ()

# --- Local nodes

radiusNode = nodeStore.add (Node (1.0))
perimeterNode = Node ()
areaNode = Node ()

# --- Dependencies

radiusNode.dependsOn ([areaNode], lambda: sqrt (areaNode.new / pi))
perimeterNode.dependsOn ([radiusNode], lambda: 2 * pi * radiusNode.new)
areaNode.dependsOn ([perimeterNode], lambda: pi * (perimeterNode.new / (2 * pi)) ** 2)

# --- Views

mainView = MainView (
	GridView ([
		[StretchView ()],
		[FillerView (), LLabelView ('Radius'), TextView (radiusNode), HExtensionView (), FillerView ()],
		[FillerView (), LLabelView ('Perimeter'), TextView (perimeterNode), HExtensionView (), FillerView ()],
		[FillerView (), LLabelView ('Area'), TextView (areaNode), HExtensionView (), FillerView ()],
		[StretchView ()]
	]), 'CircleSingleCycle'
)

nodeStore.load ('nodes.store')
mainView.execute ()
nodeStore.save ()