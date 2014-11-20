# EditableLabel is from tito's post on the wiki: http://wiki.kivy.org/Editable%20Label

# Used in the kivy/examples/widgets/lists/list_composite.py (See notes at bottom about
# how it was modified for selection.):

from kivy.adapters.dictadapter import DictAdapter
from kivy.uix.listview import ListItemButton, ListItemLabel, \
        CompositeListItem, ListView
from kivy.uix.gridlayout import GridLayout

from fixtures import integers_dict

from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.properties import BooleanProperty, ObjectProperty

class EditableLabel(ListItemLabel):
    edit = BooleanProperty(False)

    textinput = ObjectProperty(None, allownone=True)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.edit:
            self.edit = True
            self.select()
        return super(EditableLabel, self).on_touch_down(touch)

    def on_edit(self, instance, value):
        if not value:
            if self.textinput:
                self.remove_widget(self.textinput)
            return
        self.textinput = t = TextInput(
                text=self.text, size_hint=(None, None),
                font_size=self.font_size, font_name=self.font_name,
                pos=self.pos, size=self.size, multiline=False)
        self.bind(pos=t.setter('pos'), size=t.setter('size'))
        self.add_widget(self.textinput)
        t.bind(on_text_validate=self.on_text_validate, focus=self.on_text_focus)

    def on_text_validate(self, instance):
        self.text = instance.text
        self.edit = False
        self.deselect()

    def on_text_focus(self, instance, focus):
        if focus is False:
            self.text = instance.text
            self.edit = False
            self.deselect()


class MainView(GridLayout):
    '''Uses :class:`CompositeListItem` for list item views comprised by two
    :class:`ListItemButton`s and one :class:`ListItemLabel`. Illustrates how
    to construct the fairly involved args_converter used with
    :class:`CompositeListItem`.
    '''

    def __init__(self, **kwargs):
        kwargs['cols'] = 2
        kwargs['size_hint'] = (1.0, 1.0)
        super(MainView, self).__init__(**kwargs)

        # This is quite an involved args_converter, so we should go through the
        # details. A CompositeListItem instance is made with the args
        # returned by this converter. The first three, text, size_hint_y,
        # height are arguments for CompositeListItem. The cls_dicts list contains
        # argument sets for each of the member widgets for this composite:
        # ListItemButton and ListItemLabel.
        args_converter = \
            lambda row_index, rec: \
                {'text': rec['text'],
                 'size_hint_y': None,
                 'height': 25,
                 'cls_dicts': [{'cls': ListItemButton,
                                'kwargs': {'text': rec['text']}},
                               {'cls': EditableLabel,
                                'kwargs': {'text': "Middle-{0}".format(rec['text']),
                                           'is_representing_cls': True}},
                               {'cls': ListItemButton,
                                'kwargs': {'text': rec['text']}}]}

        item_strings = ["{0}".format(index) for index in xrange(100)]

        dict_adapter = DictAdapter(sorted_keys=item_strings,
                                   data=integers_dict,
                                   args_converter=args_converter,
                                   selection_mode='single',
                                   allow_empty_selection=False,
                                   cls=CompositeListItem)

        # Use the adapter in our ListView:
        list_view = ListView(adapter=dict_adapter)

        self.add_widget(list_view)


if __name__ == '__main__':
    from kivy.base import runTouchApp
    runTouchApp(MainView(width=800))


# Selection can be tricky, and easy to get "out of sync," if that is the proper phrasing.
# In the example above, EditableLabel is given calls to self.select() whenever self.edit
# is set to True, and self.deselect() whenever self.edit is set to False. This was after
# the experimenting, and finding out that if you call select() "manually," but don't call
# deselect() at the appropriate times, the single selection operations of the listview
# get broken. The rule might be, "If you alter selection, learn about and work with the
# built-in selection operations".

# ListItemLabel class
#
#    def select(self, *args):
#        self.bold = True
#        if type(self.parent) is CompositeListItem:
#            self.parent.select_from_child(self, *args)
#
#    def deselect(self, *args):
#        self.bold = False
#        if type(self.parent) is CompositeListItem:
#            self.parent.deselect_from_child(self, *args)

# So, our added calls to self.select in EditableLabel(ListItemLabel) will call the 
# parent CompositeListItem's select_ and deselect_from_child() methods:

# CompositeListItem class
#
#    def select_from_child(self, child, *args):
#        for c in self.children:
#            if c is not child:
#                c.select_from_composite(*args)
#
#    def deselect_from_child(self, child, *args):
#        for c in self.children:
#            if c is not child:
#                c.deselect_from_composite(*args)

# And, those, in turn, will essentially do a "sibling selection/deselection" when
# a label is edited, which is done via calls back down to the select_ and
# deselect_from_composite() methods of children. Those only set bold for labels
# and selected color for buttons. Override them for different visual effects.

# You could do the same sort of thing for a label that you do not want to be
# editable, but want to behave as a button would for some reason.