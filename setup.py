try: 
	from setuptools import setup
except:
	from disutils.core import setup


setup(
	name='Scheduler',
	version='1.0',
	include_package_data = True,

	author='Ben Windishar-Tatham',
	author_email='bentatham93@gmail.com',
	
	py_modules=['tkcalendar', 'eventform', 'scheduler'],
	install_requires=['google-api-python-client', 'tzlocal'],

	keywords='google-calendar-api scheduler event',
)
