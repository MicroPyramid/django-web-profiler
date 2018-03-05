import logging
import threading
import re
try:
    import resource     # Not available on Win32 systems
except ImportError:
    resource = None
import time


from django.conf import settings
from debug_toolbar.middleware import DebugToolbarMiddleware
from django.utils.encoding import force_text
from debug_toolbar import settings as dt_settings
from .models import ProfileLogRecord


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


_HTML_TYPES = ('text/html', 'application/xhtml+xml')

LOGGING_PANELS = ['SQLPanel', 'CachePanel', 'TimerPanel']

DEFAULT_LOGGED_SETTINGS = [
    'CACHE_BACKEND', 'CACHE_MIDDLEWARE_KEY_PREFIX', 'CACHE_MIDDLEWARE_SECONDS',
    'DATABASES', 'DEBUG', 'DEBUG_LOGGING_CONFIG', 'DEBUG_TOOLBAR_CONFIG',
    'DEBUG_TOOLBAR_PANELS', 'INSTALLED_APPS', 'INTERNAL_IPS',
    'MIDDLEWARE_CLASSES', 'TEMPLATE_CONTEXT_PROCESSORS', 'TEMPLATE_DEBUG',
    'USE_I18N', 'USE_L10N'
]


LOGGING_CONFIG = {
    'SQL_EXTRA': False,
    'CACHE_EXTRA': False,
    'BLACKLIST': [],
    'LOGGING_HANDLERS': ('debug_logging.handlers.DBHandler',),
    'LOGGED_SETTINGS': DEFAULT_LOGGED_SETTINGS,
}

logger = logging.getLogger('debug.logger')
logger1 = logging.getLogger('request-logging')

for HandlerClass in LOGGING_CONFIG["LOGGING_HANDLERS"]:
    logger.addHandler(HandlerClass)


class DebugLoggingMiddleware(DebugToolbarMiddleware):
    has_content = resource is not None
    view_name = ''
    args = ''
    kwargs = ''

    def process_request(self, request):
        self._start_time = time.time()
        self._start_rusage = resource.getrusage(resource.RUSAGE_SELF)
        self.t = time.process_time()
        response = super(DebugLoggingMiddleware, self).process_request(request)

        return response

    def _elapsed_ru(self, name):
        return getattr(self._end_rusage, name) - getattr(self._start_rusage, name)

    def process_view(self, request, view_func, *view_args, **view_kwargs):
        self.view_name = view_func
        self.args = view_args
        self.kwargs = view_kwargs

    def process_response(self, request, response):
        path = request.get_full_path()
        device = request.META[
            'HTTP_USER_AGENT'] if 'HTTP_USER_AGENT' in request.META.keys() else ''
        ip_address = get_client_ip(request)

        if settings.DEBUG:
            toolbar = self.__class__.debug_toolbars.pop(
                threading.current_thread().ident, None)
            if not toolbar:
                return response

            # Run process_response methods of panels like Django middleware.
            for panel in reversed(toolbar.enabled_panels):
                new_response = panel.process_response(request, response)
                if new_response:
                    response = new_response

            # Deactivate instrumentation ie. monkey-unpatch. This must run
            # regardless of the response. Keep 'return' clauses below.
            # (NB: Django's model for middleware doesn't guarantee anything.)
            for panel in reversed(toolbar.enabled_panels):
                panel.disable_instrumentation()

            # Check for responses where the toolbar can't be inserted.
            content_encoding = response.get('Content-Encoding', '')
            content_type = response.get('Content-Type', '').split(';')[0]
            if any((getattr(response, 'streaming', False),
                    'gzip' in content_encoding,
                    content_type not in _HTML_TYPES)):
                return response

            # Collapse the toolbar by default if SHOW_COLLAPSED is set.
            if toolbar.config['SHOW_COLLAPSED'] and 'djdt' not in request.COOKIES:
                response.set_cookie('djdt', 'hide', 864000)
            statistics = {}
            statistics['path'] = path
            statistics['device'] = device
            statistics['ip_address'] = ip_address
            # Insert the toolbar in the response.
            content = force_text(
                response.content, encoding=settings.DEFAULT_CHARSET)
            insert_before = dt_settings.get_config()['INSERT_BEFORE']
            pattern = re.escape(insert_before)
            bits = re.split(pattern, content, flags=re.IGNORECASE)
            if len(bits) > 1:
                # When the toolbar will be inserted for sure, generate the
                # stats.
                for panel in reversed(toolbar.enabled_panels):
                    panel.generate_stats(request, response)
                    if panel.__class__.__name__.strip() in LOGGING_PANELS:
                        if panel.__class__.__name__.strip() == 'SQLPanel':
                            statistics['num_queries'] = len(
                                panel.get_stats()['queries'])
                            statistics['sql_total_time'] = panel.get_stats()[
                                'sql_time']
                        if panel.__class__.__name__.strip() == 'CachePanel':
                            # statistics['cache_calls'] = panel.get_stats()['calls']
                            statistics['cache_total_calls'] = panel.get_stats()[
                                'total_calls']
                            statistics['cache_counts'] = panel.get_stats()[
                                'counts']
                            statistics['cache_hits'] = panel.get_stats()[
                                'hits']
                            statistics['cache_misses'] = panel.get_stats()[
                                'misses']
                            statistics['cache_total_time'] = panel.get_stats()[
                                'total_time']
                        if panel.__class__.__name__.strip() == 'TimerPanel':
                            statistics['user_cpu_time'] = panel.get_stats()[
                                'utime']
                            statistics['system_cpu_time'] = panel.get_stats()[
                                'stime']
                            statistics['total_cpu_time'] = panel.get_stats()[
                                'total']
                            statistics['elapsed_time'] = panel.get_stats()[
                                'total_time']
                            statistics['total_time'] = panel.get_stats()[
                                'total_time']

                request.statistics = statistics
                logger1.debug(statistics)
                if device:
                    cache_calls = {k: i for i, k in enumerate(
                        statistics['cache_counts'])}

                    ProfileLogRecord.objects.create(request_path=statistics['path'],
                                                    ip_address=statistics['ip_address'],
                                                    device=statistics['device'],
                                                    timer_utime=statistics['user_cpu_time'],
                                                    timer_stime=statistics['system_cpu_time'],
                                                    timer_cputime=statistics['total_cpu_time'],
                                                    sql_num_queries=statistics['num_queries'],
                                                    sql_time=statistics['sql_total_time'],
                                                    sql_queries=statistics['num_queries'],
                                                    cache_num_calls=statistics['cache_total_calls'],
                                                    cache_time=statistics['cache_total_time'],
                                                    cache_hits=statistics['cache_hits'],
                                                    cache_misses=statistics['cache_misses'],
                                                    cache_sets=cache_calls['set'],
                                                    cache_gets=cache_calls['get'],
                                                    cache_get_many=cache_calls['get_many'],
                                                    cache_deletes=cache_calls['delete'],
                                                    cache_calls=statistics['cache_total_calls'])

                bits[-2] += toolbar.render_toolbar()
                response.content = insert_before.join(bits)
                if response.get('Content-Length', None):
                    response['Content-Length'] = len(response.content)
        else:
            try:
                is_authenticated = True if request.user and request.user.is_authenticated() else False
            except:
                is_authenticated = False

            request_details = {}
            if hasattr(self, '_start_time'):
                request_details['total_time'] = (
                    time.time() - self._start_time) * 1000
            if hasattr(self, '_start_rusage'):
                self._end_rusage = resource.getrusage(resource.RUSAGE_SELF)
                request_details['utime'] = 1000 * self._elapsed_ru('ru_utime')
                request_details['stime'] = 1000 * self._elapsed_ru('ru_stime')
                request_details['total'] = request_details[
                    'utime'] + request_details['stime']
                try:
                    request_details[
                        'function_name'] = self.view_name.__module__ + "." + self.view_name.__name__
                except:
                    pass

            request_details['path'] = path
            request_details['user_logged_in'] = is_authenticated
            request_details['view_data'] = self.args
            request_details['view_data_kwargs'] = self.kwargs
            request_details['device'] = device
            request_details['ip_address'] = ip_address
            try:
                request_details['total_cpu_time'] = (
                    "%(total_time)0.3f") % request_details
            except:
                request_details['total_cpu_time'] = 0
            try:
                request_details['user_cpu_time'] = (
                    "%(utime)0.3f") % request_details
            except:
                request_details['user_cpu_time'] = 0
            try:
                request_details['system_cpu_time'] = (
                    "%(stime)0.3f") % request_details
            except:
                request_details['system_cpu_time'] = 0
            request.statistics = request_details
            logger1.debug(statistics)
        return response
