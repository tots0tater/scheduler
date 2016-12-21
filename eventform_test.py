from tkinter import *
from eventform import EventForm

def create_event_callback(d):
	for key, value in d.items():
		print(repr(key), ':', repr(value))

root = Tk()
EventForm(root, create_event_callback).pack()
root.mainloop()
