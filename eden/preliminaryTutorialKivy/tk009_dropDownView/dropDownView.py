# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# dropDownView.py

from eden import *
from collections import OrderedDict

nodeStore = Store ()

# === Nodes

# Options have ids that are language independent.
# The names of the options may change, depending on the language.
# It's the selected id that is persistent with a DropDownView, not the name, since that may change.
# In general, terminology directly showing up in a user interface often changes and should not determine program logic.

languageIdNode = nodeStore.add (Node ('en'))

animalsNode = Node () .dependsOn (
	[languageIdNode],
	lambda: OrderedDict (
			{'cat': 'Cat', 'dog': 'Dog', 'bird': 'Bird'}
		if languageIdNode.new == 'en' else
			{'cat': 'Chat', 'dog': 'Chien', 'bird': 'Oiseau'}
	)
)

animalIdNode = nodeStore.add (Node ('dog'))

animalNameNode = Node () .dependsOn ([animalIdNode, animalsNode], lambda: (animalsNode.new [animalIdNode.new] + ' ') * 10)

# === Views

mainView = MainView (
	GridView ([
		[LabelView (animalNameNode), 10], 5,
		[EmptyView (), 4, DropDownView (optionsNode = OrderedDict ({'en': 'English', 'fr': 'Francais'}), selectedOptionIdNode = languageIdNode), 2, EmptyView (), 4],
		[EmptyView ()],
		[EmptyView (), 4, DropDownView (optionsNode = animalsNode, selectedOptionIdNode = animalIdNode), 2, EmptyView (), 4],
		[LabelView (animalNameNode), 10], 5
	]),
	captionNode = 'Try the dropdown menu buttons. And try persistence by restarting the app.',
	fontScale = 2
)

nodeStore.load ()
mainView.execute ()
nodeStore.save ()
