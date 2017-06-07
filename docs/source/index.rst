django-web-profiler's documentation:
=====================================

Introduction:
=============

django-web-profiler is a django profiling tool which logs, stores debug toolbar statistics and also a set of URL's statistics using a management command.  It logs request values such as device, ip address, user cpu time, system cpu time, No of queries, sql time, no of cache calls, missing, setting data cache calls for a particular url.

It provides a basic UI, which will differentiate development url statistics, production level statistics which generates using a management command.

Source Code is available in Micropyramid Repository(https://github.com/MicroPyramid/django-web-profiler).


Modules used:

    * Python  >= 2.6 (or Python 3.4)
    * Django  = 1.9.6
    * JQuery  >= 1.7


Installation Procedure
======================

1. Install django-web-packer using the following command::

    pip install django-web-profiler

        (or)

    git clone git://github.com/micropyramid/django-web-profiler.git

    cd django-web-profiler

    python setup.py install

2. Add app name in settings.py::

    INSTALLED_APPS = [
       '..................',
       'django-web-profiler',
       '..................'
    ]

3. After installing/cloning, add the following details in settings file about urls,  logger names::

    URLS = ['http://stage.testsite.com/', 'http://stage.testsite.com/testing/']


4. Add the following logger to your existing loggers::

        'request-logging': {
            'level': 'DEBUG',
            'handlers': ['console', 'file_log'],
            'propagate': False,
        },

    Here file_log is a handler which contains a path where log files are stored.


Features:
=========

    * Logs debug toolbar statistics of a urls into a database in a development environment.
    * Logs statistics of a urls into a database in a production environment.
    * Provides a basic UI to display production, developement url statistics.


We are always looking to help you customize the whole or part of the code as you like.


Visit our Django Development page `Here`_


We welcome your feedback and support, raise `github ticket`_ if you want to report a bug. Need new features? `Contact us here`_

.. _contact us here: https://micropyramid.com/contact-us/
.. _github ticket: https://github.com/MicroPyramid/django-web-profiler/issues
.. _Here: https://micropyramid.com/django-development-services/

    or

mailto:: "hello@micropyramid.com"

