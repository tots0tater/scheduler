from tkinter import Frame, Button, Label
import calendar, datetime

class TkCalendar(Frame):
	"""
	A tkinter calendar that displays a month. All days on the
	calendar are buttons that when pressed return a date 
	object to the designated callback function.
	
	Required arguments:
		master -- the parent which TkCalendar will belong to.
			This is primarily used for drawing.
	
	Keyword arguments:
		date_callback -- a callback function that all dates on
			a calendar subscribe to when clicked on. The 
			returned function handles the returned date object
		today_color -- color if the day on the calendar is today
		current_month_color -- color if day lies within current
			month. (default 'white')
		other_month_color -- color if day lies outside current
			month. (default 'gray93')
		year -- the year our calendar is initialized to 
			(default datetime.date.today().year)
		month -- the month our calendar is initialized to
			(default datetime.date.today().month)
	"""
	def __init__(
			self, 
			master, 
			date_callback=lambda date: print(date),
			today_color='light cyan',
			current_month_color='white',
			other_month_color='gray93',
			year=datetime.date.today().year, 
			month=datetime.date.today().month):

		self.master = master
		super().__init__(self.master)

		# Where we'll draw the calendar
		self.calendar_frame = Frame(self)

		# The date callback function used for when a user clicks on
		self.date_callback = date_callback

		# Information to default our calendar month to
		self.today = datetime.date.today()
		self.year = year
		self.month = month
		
		# Colors for our calendar
		self.today_color = today_color
		self.current_month_color = current_month_color
		self.other_month_color = other_month_color

		# Internal calendar for getting a month date calendar
		self.c = calendar.Calendar()

		self.header = Label(self, text='', width=20)
		self.previous_month = Button(
			self, text="<== previous", command=self.__prev_month, width=10
		)
		self.next_month = Button(
			self, text="next ==>", command=self.__next_month, width=10
		)

		self.__get_calendar()

	def __prev_month(self):
		self.month -= 1
		if 0 == self.month:
			self.month = 12
			self.year -= 1
		self.__get_calendar()

	def __next_month(self):
		self.month += 1
		if 13 == self.month:
			self.month = 1
			self.year += 1
		self.__get_calendar()

	def set_year(self, year):
		self.year = year
		self.__get_calendar()

	def set_month(self, month):
		self.month = month
		self.__get_calendar()

	def __get_calendar(self, width=5):
		# Remove all of our internal widgets for our calendar
		# This is because we're updating our buttons
		for widget in self.calendar_frame.winfo_children():
			widget.destroy()

		# Update our header
		self.header.config(text="{} {}".format(calendar.month_name[self.month], self.year))

		self.header.grid(row=0, column=3)
		self.previous_month.grid(row=0, column=0)
		self.next_month.grid(row=0, column=6)

		# Draw our day names
		for col, name in enumerate(calendar.day_name):
			Label(self.calendar_frame, text=name[:3], width=width).grid(row=0, column=col)

		# Get our iterable month
		calendar_month = self.c.monthdatescalendar(self.year, self.month)
		for row, week in enumerate(calendar_month):
			for col, day in enumerate(week):
				# The function our button will go to when pressed
				def date_handler(day=day):
					self.date_callback(day)

				background = None
				if self.today == day:
					background = self.today_color
				elif day.month == self.month:
					background = self.current_month_color
				else:
					background = self.other_month_color

				# A button for the current day in our calendar.
				# When pressed, it will pass the date object
				# to the initialized date_callback function
				Button(
					self.calendar_frame, 
					text=str(day.day), 
					width=width, 
					background=background,
					borderwidth=0,
					command=date_handler,
				).grid(row=row + 1, column=col)
		self.calendar_frame.grid(row=1, column=0, columnspan=7)
