from kivy.uix.listview import ListView, ListItemButton
from kivy.uix.boxlayout import BoxLayout
from kivy.adapters.dictadapter import ListAdapter
from kivy.uix.button import Button
from random import randint

class MainView(BoxLayout):
    def __init__(self, **kwargs):
        kwargs['cols'] = 2
        super(MainView, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.list_adapter = ListAdapter(data=["Item #{0}".format(i) for i in range(10)], cls=ListItemButton, sorted_keys=[])
        self.list_adapter.bind(on_selection_change=self.selection_change)
        list_view = ListView(adapter=self.list_adapter)
        self.add_widget(list_view)
        self.add_widget(Button(text="select random item", on_press=self.callback))

    def callback(self, instance):
        index = randint(0, 9)
        self.change_from_code = True
        if not self.list_adapter.get_view(index).is_selected:
            self.list_adapter.get_view(index).trigger_action(duration=0)
        self.change_from_code = False

    def selection_change(self, adapter, *args):
        if self.change_from_code:
            print "selection change from code"
        else:
            print "selection changed by click"

if __name__ == '__main__':
    from kivy.base import runTouchApp
    runTouchApp(MainView(width=800))