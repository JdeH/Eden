from TkinterDnD2 import *
from Tkinter import *

root = TkinterDnD.Tk()

l = Listbox(root)
l.pack(fill='both', expand=1)
root.update()

# make the listbox a drop target
l.drop_target_register('*')

def drop_enter(event):
    l.focus_force()
    print 'Entering widget: %s' % event.widget
    return event.action

def drop_position(event):
    print 'Position: x %d, y %d' %(event.x_root, event.y_root)
    return event.action

def drop_leave(event):
    print 'Leaving %s' % event.widget,event.data
    return event.action

def drop(event):
    print 'Dropped file(s):', event.data
    if event.data:
        try:
            files = event.data.split()
            for f in files:
                l.insert('end', f)
        except:
            pass
    return COPY

l.dnd_bind('<<DropEnter>>', drop_enter)
l.dnd_bind('<<DropPosition>>', drop_position)
l.dnd_bind('<<DropLeave>>', drop_leave)
l.dnd_bind('<<Drop>>', drop)


# make the listbox a drag source

l.drag_source_register(1, CF_TEXT)

def drag_init(event):
    data = ''
    if l.curselection():
        data = l.get(l.curselection()[0])
    print 'Dragging :', data
    # this does not work yet, probably this return value is the problem
    return (COPY, CF_TEXT, data)

def drag_end(event):
    print 'Drag end, data:', event.data



l.dnd_bind('<<DragInitCmd>>', drag_init)
l.dnd_bind('<<DragEndCmd>>', drag_end)



root.mainloop()

