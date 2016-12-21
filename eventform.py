# The widgets used
from tkinter import Button, Frame, Entry, Label, Spinbox, Text, IntVar, Checkbutton
# Keywords from tkinter used
from tkinter import WORD, NORMAL, END

# The calendar widget
from tkcalendar import TkCalendar
import calendar, datetime, tzlocal

class EventForm(Frame):
	"""
	A form for gathering Google Calendar data to create an
	event. Once all the required entries are filled, 
	clicking on the Create Event button will return a dictionaray
	associating the labels with the values

	Required input:
		parent -- The parent which our EventForm will belong to.
			This will be used for drawing.

	Keyword arguments:
		create_event_callback -- a callback function that handles
			the returned event dictionary. 
	"""
	def __init__(self, parent, create_event_callback=lambda d: print(d)):
		super().__init__(parent)

		self.create_event_callback = create_event_callback

		self.__setup_form_widgets()

		# A TkCalendar that will be placed to the right 
		# of our input form.
		self.tkcalendar = TkCalendar(self, self.__handle_date)
		self.create_event = Button(self, text="Create Event", command=self.__handle_callback)
		self.__draw_widgets()

	def __setup_form_widgets(self):
		# The frame which will draw our form
		self.form = Frame(self)

		entry_width = 30

		self.event_label = Label(self.form, text="Event Name: ")
		self.event = Entry(self.form, width=entry_width)

		self.time_label = Label(self.form, text="Start Time: ")
		self.time = Time(self.form)

		self.available_days_label = Label(self.form, text="Available Days: ")
		self.available_days = DaysToggle(self.form)

		# Start and end dates are entered by the user pressing
		# on a calander day. This way, we can ensure consistent
		# input that's in a format we always know
		self.start_label = Label(self.form, text="Start Date: ")
		self.start = DateEntry(
			self.form, 
			width=entry_width, 
			state='readonly',
			cursor='arrow',
			readonlybackground='',
			foreground='white',
			background='DeepSkyBlue4',
		)
		self.start.bind('<Button-1>', self.__set_focus)
		self.focus_date = self.start

		self.end_label = Label(self.form, text="End Date: ")
		self.end = DateEntry(
			self.form, 
			width=entry_width, 
			state='readonly',
			cursor='arrow',
			readonlybackground='',
			background='DarkSlateGray2',
		)
		self.end.bind('<Button-1>', self.__set_focus)


		self.hours_label = Label(self.form, text="Hours Needed: ")
		self.hours = Spinbox(self.form, from_=1, to=100, width=5)
		
		self.location_label = Label(self.form, text="Location: ")
		self.location = Entry(self.form, width=entry_width)
		
		self.description_label = Label(self.form, text="Description: ")
		self.description = Text(self.form, height=5, width=entry_width, font='TkDefaultFont', wrap=WORD)

		self.form_widgets = [
			(self.event_label, self.event), 
			(self.time_label, self.time),
			(self.available_days_label, self.available_days),
			(self.start_label, self.start), 
			(self.end_label, self.end), 
			(self.hours_label, self.hours), 
			(self.location_label, self.location), 
			(self.description_label, self.description),
		] 

	def __set_focus(self, event):
		self.focus_date.config(background='DarkSlateGray2', foreground='black')
		self.focus_date = event.widget
		self.focus_date.config(background='DeepSkyBlue4', foreground='white')

	def __draw_widgets(self):
		for row, widget in enumerate(self.form_widgets):
			widget[0].grid(sticky='E', row=row, column=0)
			widget[1].grid(sticky='W', row=row, column=1, pady=5)
		self.form.grid(row=0, column=0, padx=10)

		self.tkcalendar.grid(sticky='N', row=0, column=1, columnspan=7, pady=5)
		self.create_event.grid(row=1, column=0)

	def __handle_date(self, date):
		self.focus_date.date = date

		self.focus_date.config(state=NORMAL)
		self.focus_date.delete(0, END)
		self.focus_date.insert(0, str(date))
		self.focus_date.config(state='readonly')

	def __handle_callback(self):
		d = self.get_form_data()
		self.create_event_callback(d)

	def get_form_data(self):
		"""
		Returns a dictionary containing keys that correspond to
		a CalendarEvent. 
		"""
		# Make sure they made an event name
		if self.event.get() == '':
			raise Exception("ERROR. Enter event name.")
		# Must ensure our dates are valid
		if not self.start.date:
			raise Exception("ERROR. Select a start date.")
		if not self.end.date:
			raise Exception("ERROR. Select an end date.")
		if self.start.date >= self.end.date:
			raise Exception("ERROR. End date must be after start date.")
		if self.start.date < self.tkcalendar.today:
			raise Exception("ERROR. Cannot schedule event starting in the past.")

		d = {
			'summary' : self.event.get(),
			'location' : self.location.get(),
			'description' : self.description.get("1.0", END),
			'start' : { 
				'dateTime' : self.start.date.isoformat(), 
				'timeZone' : str(tzlocal.get_localzone()),
			},
			'end' : { 
				# Our task will end on the same day since we
				# will be allocating hours over a recurring 
				# number of days
				'dateTime' : self.start.date.isoformat(), 
				'timeZone' : str(tzlocal.get_localzone()),
			},

			'hoursNeeded' : self.hours.get(),
			'availableDays' : self.available_days.selected_days(),
			'startTime' : self.time.get_time(),
			'endDate' : self.end.date,
		}

		# End date is when we need the task completed by
		return d

class DateEntry(Entry):
	"""
	A simple class that inherits from Entry and 
	contains a datetime object named date.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.date = None

class Time(Frame):
	"""
	A tkinter widget for setting and getting a time. The 
	get_time method will return a datetime.time object
	based off of the input in the entries.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		width = 3
		self.hours = Entry(self, width=width)
		self.hours.insert(0, "10")
		self.hours.bind("<FocusOut>", self.__verify_hours)
		self.hours.grid(row=0, column=0)
		Label(self, text=":").grid(row=0, column=1)

		self.minutes = Entry(self, width=width)
		self.minutes.insert(0, "00")
		self.minutes.bind("<FocusOut>", self.__verify_minutes)
		self.minutes.grid(row=0, column=2)

		self.am_pm = Label(self, text='AM', cursor='hand2')
		self.am_pm.bind("<Button-1>", 
			lambda e: e.widget.config(text='AM' if e.widget.cget('text') == 'PM' else 'PM')
		)
		self.am_pm.grid(row=0, column=3)

	def __set_entry(self, entry, value):
		entry.delete(0, END)
		entry.insert(0, value)

	def __verify_hours(self, event):
		try:
			num = int(event.widget.get())
			if num < 1 or num > 12:
				raise Exception()

			self.__set_entry(event.widget, str(num))
		except:
			self.__set_entry(event.widget, '')

	def __verify_minutes(self, event):
		try:
			num = int(event.widget.get())
			if num < 0 or num > 59:
				raise Exception()

			if num < 10:
				self.__set_entry(event.widget, "0{}".format(num))
			else:
				self.__set_entry(event.widget, str(num))
		except:
			self.__set_entry(event.widget, '')

	def get_time(self):
		if not all(( self.hours.get(), self.minutes.get()) ):
			raise Exception("ERROR. Enter a time.")

		# No need to verify our hours and minutes are ints;
		# we already did that checking on input
		hours = int(self.hours.get())

		if self.am_pm.cget('text') == 'PM' and hours != 12:
			hours += 12
		elif self.am_pm.cget('text') == 'AM' and hours == 12:
			hours -= 12

		return datetime.time(hours, int(self.minutes.get()))

class DaysToggle(Frame):
	def __init__(self, master):
		super().__init__(master)

		self.mon_var = IntVar()
		self.tue_var = IntVar()
		self.wed_var = IntVar()
		self.thu_var = IntVar()
		self.fri_var = IntVar()
		self.sat_var = IntVar()
		self.sun_var = IntVar()

		self.int_vars = (
			self.mon_var, self.tue_var, self.wed_var, self.thu_var, 
			self.fri_var, self.sat_var, self.sun_var
		)
		
		row, col = 0, 0
		for day, var in zip(('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'), self.int_vars):
			cb = Checkbutton(self, text=day, variable=var)
			cb.grid(row=row, column=col, sticky='w')
			cb.toggle()

			col += 1
			if col % 4 == 0:
				row += 1
				col = 0

	def selected_days(self):
		"""
		Returns a list of the toggled days in RFC 5545
		day name format
		"""
		days = []
		for day, var in zip(('MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'), self.int_vars):
			if var.get(): 
				days.append(day)

		if len(days) == 0:
			raise Exception("ERROR. Toggle at least one day.")

		return days

