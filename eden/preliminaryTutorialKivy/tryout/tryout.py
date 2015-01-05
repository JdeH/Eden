from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout

class MainApp (App):
	def build (self):
		def showMainCoords (*args):
			print 'Main:', args [1] .pos
	
		def showRelativeLayoutCoords (*args):
			print 'RelativeLayout:', args [1] .pos
			
		relativeLayout0 = RelativeLayout ()
		button = Button (text = 'Launch dialog', on_press = lambda *args: popup.open ())
		relativeLayout0.add_widget (button)
	
		popup = Popup (size_hint = (0.5, 0.5), title = 'A popup')
		relativeLayout = RelativeLayout ()
		popup.add_widget (relativeLayout)
		button2 = button = Button (text = 'Dialog')
		relativeLayout.add_widget (button2)
		
		button2.bind (on_touch_move = showMainCoords)
		
		return relativeLayout0

if __name__ == '__main__':
	MainApp () .run ()