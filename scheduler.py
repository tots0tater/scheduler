# tk widget for displaying our event form
from eventform import EventForm
from tkinter import *

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime, calendar

import argparse

import re
import math

class Unimplemented(Exception):
	pass

class CalendarEvent():
	"""
	Creates a JSON event from passed in parameters. 
	"""
	def __init__(self, **kwargs):
		self.calendar_id = 'primary'

		# Pre-initialize our dictionary before editing it
		self.__setup_options()

		self.hours_needed = None
		if kwargs.get('hoursNeeded'):
			try:
				self.hours_needed = int(kwargs['hoursNeeded'])
				del kwargs['hoursNeeded']
			except TypeError:
				raise TypeError()

		self.end_date = None
		if kwargs.get('endDate'):
			assert isinstance(kwargs['endDate'], datetime.date), (
				"ERROR. 'endDate' must be of type date."
			)
			self.end_date = kwargs['endDate']
			del kwargs['endDate']

		self.start_time = None
		if kwargs.get('startTime'):
			assert isinstance(kwargs['startTime'], datetime.time), (
				"ERROR. 'startTime' must be of type time."
			)
			self.start_time = kwargs['startTime']
			del kwargs['startTime']

		self.available_days = None
		if kwargs.get('availableDays'):
			assert isinstance(kwargs['availableDays'], list), (
				"ERROR. 'availableDays' must be of type list."
			)
			self.available_days = kwargs['availableDays']
			del kwargs['availableDays']

		for key, value in kwargs.items():
			if key not in self.options:
				print("ERROR. Unsupported or invalid option '{}'.".format(key))
			else:
				self.options[key] = value

		self.set_recurrence(self.hours_needed)

	def __setup_options(self):
		self.options = {
			'summary' : '',
			'location' : '',
			'description' : '',
			'start' : { 'dateTime' : '', 'timeZone' : '' },
			'end' : { 'dateTime' : '', 'timeZone' : '' },
			'recurrence' : [],
		}

	def __set_str(self, option, s):
		if not isinstance(s, str):
			print("ERROR. '{}' must be of type str.".format(option))
		else:
			self.options[option] = s

	def set_summary(self, summary):
		"""
		Sets the summary field in the options dictionary.
		"""
		self.__set_str('summary', summary)

	def set_location(self, location):
		"""
		Sets the location field in the options dictionary.
		"""
		self.__set_str('location', location)

	def set_description(self, description):
		"""
		Sets the description field in the options dictionary.
		"""
		self.__set_str('description', description)

	def __valid_date(self, date_time, time_zone):
		valid = True
		if not isinstance(date_time, datetime.date):
			print("ERROR. 'date_time' must be of type datetime.date.")
			valid = False
		if not isinstance(time_zone, datetime.date):
			print("ERROR. 'time_zone' must be of type datetime.timzeone.")
			valid = False

		return valid

	def __set_date(self, start_or_end, date_time, time_zone):
		if self.__valid_date(date_time, time_zone):
			self.options[start_or_end]['dateTime'] = date_time.isoformat()
			self.options[start_or_end]['timeZone'] = str(time_zone)

	def set_start(self, date_time, time_zone):
		self.__set_date('start', date_time, time_zone)

	def set_end(self, date_time, time_zone):
		self.__set_date('end', date_time, time_zone)

	def __get_task_end(self, start_date, start_time, hours_a_day):
		# If we, for example, start an event at 11PM and it takes 2 hours a 
		# day, then the end date for the task is an additional day
		additional_day = 1 if (start_time.hour + hours_a_day > 23) else 0

		print("start_time.hour + hours_a_day: ", start_time.hour + hours_a_day)
		print("additional_day: ", additional_day)

		end_date = None
		# Three special (but unlikely) cases:
		#	1 -- the end date is the next day
		try:
			end_date = datetime.date(
				start_date.year, 
				start_date.month, 
				start_date.day + additional_day
			)
		#	2 -- the end date is the start of the next month
		except:
			try:
				end_date = datetime.date(
					start_date.year,
					start_date.month + 1,
					1
				)
		# 	3 -- the end date is the start of the next year
			except:
				end_date = datetime.date(
					start_date.year + 1,
					1,
					1
				)

		print(end_date)

		return end_date

	def set_recurrence(self, hours_needed):
		"""
		Based off our current date and end date, set_recurrence 
		calculates the number of hours needed per day to finish
		a task from the passed in overall hours needed. 
		"""
		if not isinstance(hours_needed, int):
			raise TypeError("ERROR. 'hours_needed' needs to be of type int, not {}.".format(type(hours_needed)))

		start_date = None
		try:
			sd_string = self.options['start']['dateTime']
			# Gets it into a datetime
			sdt = datetime.datetime.strptime(sd_string, '%Y-%m-%d')
			start_date = datetime.date(sdt.year, sdt.month, sdt.day)
		except:
			raise Exception("ERROR. Invalid date format.")


		"""
		The idea of the algorithm:

		Mon 	Tue 	Wed 	Thu 	Fri 	Sat 	Sun
		 X 		  		 X 		 X

		days between: 10
		
		# NOTE: This doesn't take into account the day we
		# start our task, nor does it respect the end day
		# ceiling(10 / 7) represents the number of weeks
		max work days: 3 * ceiling(10 / 7)
		max work days == 6

		From the start day, subtract how many days come 
		before that in available days ... ie. if we 
		start on a Thursday and our available days are
		Monday, Wednesday, and Thursday, subtract 2
		from max work days

		Next, do the same process for the end date--
		subtract the number of avaiable days after
		our end date. ie. if we end on Tuesday, 
		subtract 1 from our max work days	
		"""

		# Number of days between start and end date
		days_between = (self.end_date - start_date).days
		weeks = math.ceil(days_between / 7)
		# Number of days available a week to work
		max_work_days = len(self.available_days) * (int(days_between / 7) + 1)
		days = max_work_days

		day_value = {}
		for day, value in zip(('MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'), range(7)):
			day_value[day] = value

		for day in self.available_days:
			if day_value[day] < start_date.weekday():
				days -= 1

		for day in self.available_days:
			if day_value[day] > self.end_date.weekday():
				days -= 1

		hours_a_day, leftover = divmod(hours_needed, days)
		minutes_a_day = 0 if leftover == 0 else (leftover * 60 // days)

		# If the user, for example, has a task tarting at 10:30 and we
		# need 50 minutes a day ... this will rollover the hour.
		minutes_overlap = 1 if self.start_time.minute + minutes_a_day > 60 else 0

		end_time = datetime.time(
			(self.start_time.hour + hours_a_day + minutes_overlap) % 24, 
			(self.start_time.minute + minutes_a_day) % 60,
		)

		task_end = self.__get_task_end(start_date, self.start_time, hours_a_day)

		start_datetime = datetime.datetime.combine(start_date, self.start_time)
		end_datetime = datetime.datetime.combine(task_end, end_time)

		# Inclusive_date ensures that time gets allocated for the
		# last day; without, we will only allocated time up to the
		# last day
		inclusive_date = self.__get_task_end(self.end_date, datetime.time(23), 2)
		# Repeat our event weekly until our last day; this string
		# is in RFC3339 format without punctuation
		until_s = datetime.datetime.combine(inclusive_date, datetime.time(0)).isoformat('T')
		until_s = re.sub('[-:]', '', until_s) + 'Z'

		recurrence_s = 'RRULE:FREQ=WEEKLY;INTERVAL=1;UNTIL={};BYDAY={}'.format(
			until_s, ','.join(self.available_days), 
		)

		self.options['start']['dateTime'] = start_datetime.isoformat('T')
		self.options['end']['dateTime'] = end_datetime.isoformat('T')
		self.options['recurrence'] = [recurrence_s]

	def create_event(self):
		"""
		From the data inside the class, this method creates an event
		on the passed in calendar id
		"""
		if not CalendarCredentials.logged_in():
			raise Exception("ERROR. User must be logged in to create an event.")

		event = CalendarCredentials.service.events().insert(calendarId=self.calendar_id, body=self.options).execute()
		print("Event created: {}".format(event.get('htmlLink')))

	def __str__():
		return str(self.options)

class CalendarCredentials():
	class __InitStatic():
		@classmethod
		def get_credential_path(cls, home_dir, credential_dir):
			if not os.path.exists(credential_dir):
				os.makedirs(credential_dir)

			return os.path.join(credential_dir, 'calendar-python-scheduler.json')

		@classmethod
		def get_http(cls, credentials):
			return credentials.authorize(httplib2.Http()) if credentials else None

		@classmethod
		def get_service(cls, http):
			if not http:
				return None
			return discovery.build('calendar', 'v3', http=http) if http else None

	# Static variables for our CalendarCredentials
	flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()

	# If modifying these scopes, delete your previously saved credentials
	# at ~/.credentials/[credential-name]
	SCOPES = 'https://www.googleapis.com/auth/calendar'
	CLIENT_SECRET_FILE = 'client_secret.json'
	APPLICATION_NAME = 'Scheduler'

	home_dir = os.path.expanduser('~')
	credential_dir = os.path.join(home_dir, '.credentials')
	credential_path = __InitStatic.get_credential_path(home_dir, credential_dir)
	store = Storage(credential_path)
	credentials = store.get()
	http = __InitStatic.get_http(credentials)
	service = __InitStatic.get_service(http)

	def __init__(self):
		pass

	def __set_credential_path(self):
		self.credential_dir = os.path.join(home_dir, '.credentials')
		if not os.path.exists(self.credential_dir):
			os.makedirs(credential_dir)

		return os.path.join(credential_dir, 'calendar-python-scheduler.json')

	def __get_credentials(self):
		self.store = Storage(self.credential_path)
		return self.store.get()

	@classmethod
	def logged_in(cls):
		return cls.credentials or cls.credentials.invalid

	@classmethod
	def get_credentials(cls):
		"""
		Gets valid user credentials from storage.

		If nothing has been stored, or if the stored credentials are invalid,
		the OAuth2 flow is completed to obtain new credentials.

		Returns:
			Credentials, the obtained credential
		"""
		if not cls.credentials or cls.credentials.invalid:
			flow = client.flow_from_clientsecrets(cls.CLIENT_SECRET_FILE, cls.SCOPES)
			flow.user_agent = cls.APPLICATION_NAME
			cls.credentials = tools.run_flow(flow, cls.store, cls.flags)
			print('Storing credentials to ' + cls.credential_path)

			cls.http = cls.__InitStatic.get_http(cls.credentials)
			cls.service = cls.__InitStatic.get_service(cls.http)

	@classmethod
	def remove_credentials(cls):
		"""
		Removes saved user credentials effectively logging the user out.
		"""
		if not os.path.exists(cls.credential_dir):
			print("ERROR. A credential directory does not exist.")
			return
		try:
			os.remove(cls.credential_path)
		except OSError:
			print("ERROR. Credential file does not exist.")
		
		cls.credentials = None
		cls.http = None
		cls.service = None
		print("Credential file deleted.")

def handle_login(event):
	# Then we're logged in
	if not CalendarCredentials.credentials or CalendarCredentials.credentials.invalid:
		CalendarCredentials.get_credentials()
		event.widget.config(text='logout')
	else:
		CalendarCredentials.remove_credentials()
		event.widget.config(text='login')

def setup_login_logout_button(button_frame):
	text = "logout"
	if not CalendarCredentials().credentials or CalendarCredentials().credentials.invalid:
		text = "login"

	login_logout = Label(
		button_frame, 
		text=text,
		cursor='hand2',
		font="TkDefaultFont 8 underline",
	)
	login_logout.bind("<Button-1>", handle_login)
	login_logout.bind("<Enter>", lambda event: event.widget.configure(font="TkDefaultFont 8 bold underline"))
	login_logout.bind("<Leave>", lambda event: event.widget.configure(font="TkDefaultFont 8 underline"))
	login_logout.grid(row=0, column=0, sticky='we')

	return login_logout

def create_calendar_event(event):
	print("Creating event ... ")

	# Turn our event dictionary into keyword arguments
	ce = CalendarEvent(**event)
	ce.create_event()

if __name__ == '__main__':
	root = Tk()

	button_frame = Frame(root, height=20, width=45)
	login_logout = setup_login_logout_button(button_frame)

	# Ensures our frame doesn't expand when the font 
	# changes for our login_logout button
	button_frame.grid_propagate(False)
	button_frame.grid(row=0, column=0, sticky=E)

	event_form = EventForm(root, create_calendar_event)
	event_form.grid(row=1, column=0, padx=10, pady=10)

	root.resizable(width=False, height=False)
	root.mainloop()	
