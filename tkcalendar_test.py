from tkinter import Tk
from tkcalendar import *

root = Tk()

c = TkCalendar(root)
c.grid(row=1, column=0, columnspan=7)

root.mainloop()
