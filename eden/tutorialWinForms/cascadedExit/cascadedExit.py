from eden import *

do1Node = Node (None)
do2Node = Node (None)

view2 = ModalView (FillerView (), '2')
view1 = ModalView (ButtonView (do2Node, '2'), '1')
mainView = MainView (ButtonView (do1Node, '1'), '0')

do1Node.action = view1.execute

def do2 ():
	view2.execute ()
	view1.exit ()
	
do2Node.action = do2

mainView.execute ()
