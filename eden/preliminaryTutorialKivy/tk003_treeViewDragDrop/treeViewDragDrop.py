# Copyright (C) 2005 - 2014 Jacques de Hooge, Geatec Engineering
#
# This program is free software.
# You can use, redistribute and/or modify it, but only under the terms stated in the QQuickLicence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the QQuickLicence for details.

# treeViewDragDrop.py

from org.qquick.eden import *

nodeStore = Store ()

topTreeNode = nodeStore.add (Node ([
	('City', [
		('Buildings', [
			('Houses', ['Flats', 'Bungalows', 'Campers']),
			('Business estate', ['Shops', 'Offices', 'Factories']),
			('Religious buildings', ['Churches', 'Mosques', 'Synagogues'])
		]), 
		('Roads', [
			('Roads for cars', ['Highways', 'Main roads', 'Streets']),
			('Roads for bikes', ['Smooth bike roads', 'Bumpy bike roads', 'Muddy trails']),
			('Roads for pedestrians', ['Sidewalks', 'Promenades', 'Stairs'])
		]),
		('Nature', [
			('Public parks', ['Grass to play on', 'Trees to climb in', 'Robust flowers']),
			('Private parks', ['Grass to look at', 'Trees to sit under', 'Delicate flowers']),
			('Gardens', ['Grass for domestic animals', 'Small trees', 'Exotic flowers'])
		])
	])
]), 'topTree')

bottomTreeNode = nodeStore.add (Node ([
	('Subjects', [
		('Big subjects', [
			('Noisy', ['Jet', 'Steel mill', 'Freight train']),
			('Audible', ['Elephant', 'Truck', 'Whale']),
			('Silent', ['Mountain', 'Tree', 'Cloud'])
		]), 
		('Not so big subjects', [
			('Noisy', ['Motor bike', 'Chain saw', 'PA system']),
			('Audible', ['Human being', 'Cat',	'Dish washer']),
			('Silent', ['Lamp post', 'Brick', 'Plant'])
		]),
		('Rather small subjects', [
			('Noisy', ['Cricket', 'Wasp', 'Whistle']),
			('Audible', ['Mosquito', 'Mouse', 'Music box']),
			('Silent', ['Strawberry', 'Glas of water', 'Piece of cake'])
		])
	])
]), 'bottomTree')

mainView = MainView (VGridView ([
	LabelView (
'''
Expand some tree branches and start dragging any of them sideways.
Wait a second close to the starting point of a drag to copy rather than move.
Wait a second close to the end point of a drag to insert a child rather than a sibling.
You may also reorder trees by dragging and dropping.
Note that the tree contents are persistent between invocations of the program.
If you want to have the original trees back, just delete the 'nodes.store' file.'''
	),
	TreeView (rootNode = 'Top Tree', treeNode = topTreeNode), 4,
	TreeView (rootNode = 'Bottom Tree', treeNode = bottomTreeNode), 4
]), 'Drag & Drop between TreeViews')

nodeStore.load ()
mainView.execute ()
nodeStore.save ()

