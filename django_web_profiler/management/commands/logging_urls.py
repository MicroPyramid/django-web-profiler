from django.core.management.base import BaseCommand
from django.core.management import call_command
import json
from django.conf import settings
import requests
from django.test.client import Client
import logging
from django_web_profiler.models import ProfileLog, ProfileLogRecord
import collections
from datetime import datetime


class Command(BaseCommand):
    args = '<filename>'
    help = 'Loads the initial data in to database'

    def handle(self, *args, **options):
        client = Client()
        logger1 = logging.getLogger("request-logging")
        profile_log = ProfileLog.objects.create(name=datetime.now(), start_time=datetime.now())

        for url in settings.URLS:
            response = client.get(url, DJANGO_DEBUG_LOGGING=True)
            request = response.wsgi_request
            statistics = request.statistics
            total_time = total_user_cpu_time = total_system_cpu_time = total_sql_time = 0.0
            total_sql_queries = total_cache_hits = total_cache_misses = 0

            if settings.DEBUG:
                cache_calls = {k:i for i,k in enumerate(statistics['cache_counts'])}

                total_time += statistics['total_cpu_time']
                total_user_cpu_time += statistics['user_cpu_time']
                total_system_cpu_time += statistics['system_cpu_time']
                total_sql_time += statistics['sql_total_time']
                total_sql_queries += statistics['num_queries']
                total_cache_hits += statistics['cache_total_calls']
                total_cache_misses += statistics['cache_misses']
                ProfileLogRecord.objects.create(profile_log=profile_log, request_path=statistics['path'], ip_address=statistics['ip_address'], device=statistics['device'],
                                                timer_utime=statistics['user_cpu_time'], timer_stime=statistics['system_cpu_time'], timer_cputime=statistics['total_cpu_time'],
                                                sql_num_queries=statistics['num_queries'], sql_time=statistics['sql_total_time'], sql_queries=statistics['num_queries'],
                                                cache_num_calls=statistics['cache_total_calls'], cache_time=statistics['cache_total_time'], cache_hits=statistics['cache_hits'], cache_misses=statistics['cache_misses'],
                                                cache_sets=cache_calls['set'], cache_gets=cache_calls['get'], cache_get_many=cache_calls['get_many'], cache_deletes=cache_calls['delete'], cache_calls=statistics['cache_total_calls'])

            else:
                total_time += float(statistics['total_cpu_time'])
                total_user_cpu_time += float(statistics['user_cpu_time'])
                total_system_cpu_time += float(statistics['system_cpu_time'])

                ProfileLogRecord.objects.create(profile_log=profile_log, request_path=statistics['path'], ip_address=statistics['ip_address'], device=statistics['device'],
                                                timer_utime=statistics['user_cpu_time'], timer_stime=statistics['system_cpu_time'], timer_cputime=statistics['total_cpu_time'])
            profile_log_records = ProfileLogRecord.objects.filter(profile_log=profile_log)
            profile_log.total_requests = len(settings.URLS)
            profile_log.avg_time = (total_time/len(settings.URLS))
            profile_log.total_time = total_time
            profile_log.avg_cpu_time = total_user_cpu_time/len(settings.URLS)
            profile_log.total_user_cpu_time = total_user_cpu_time
            profile_log.total_system_cpu_time = total_system_cpu_time
            profile_log.end_time = datetime.now()
            profile_log.save()

        result = {'message': "Successfully Loading initial data"}

        return json.dumps(result)
