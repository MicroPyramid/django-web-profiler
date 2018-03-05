from django.db import models


class ProfileLog(models.Model):
    """Captures overall statistics about a single test run."""
    name = models.CharField(max_length=255, blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    hostname = models.CharField(max_length=255, blank=True, null=True)

    total_requests = models.IntegerField(blank=True, null=True)
    avg_time = models.FloatField(blank=True, null=True)
    total_time = models.FloatField(blank=True, null=True)
    avg_cpu_time = models.FloatField(blank=True, null=True)
    total_user_cpu_time = models.FloatField(blank=True, null=True)
    total_system_cpu_time = models.FloatField(blank=True, null=True)

    avg_sql_time = models.FloatField(blank=True, null=True)
    total_sql_time = models.FloatField(blank=True, null=True)
    avg_sql_queries = models.FloatField(blank=True, null=True)
    total_sql_queries = models.IntegerField(blank=True, null=True)

    avg_cache_hits = models.FloatField(blank=True, null=True)
    total_cache_hits = models.IntegerField(blank=True, null=True)
    avg_cache_misses = models.FloatField(blank=True, null=True)
    total_cache_misses = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return u'Test Rume from %s to %s' % (self.start_time, self.end_time)


class ProfileLogRecord(models.Model):
    """Captures statistics for individual requests."""
    timestamp = models.DateTimeField(auto_now_add=True)
    profile_log = models.ForeignKey(
        ProfileLog, blank=True, null=True, related_name='profile_log', on_delete=models.CASCADE)

    request_path = models.CharField(max_length=255)
    ip_address = models.CharField(max_length=255)
    device = models.CharField(max_length=255)
    arguments = models.TextField(default='')
    kw_arguments = models.TextField(default='')

    # Timer stats
    timer_utime = models.FloatField(blank=True, null=True)
    timer_stime = models.FloatField(blank=True, null=True)
    timer_cputime = models.FloatField(blank=True, null=True)
    timer_total = models.FloatField(blank=True, null=True)
    timer_vcsw = models.IntegerField(blank=True, null=True)
    timer_ivcsw = models.IntegerField(blank=True, null=True)

    # Sql stats
    sql_num_queries = models.IntegerField(blank=True, null=True)
    sql_time = models.FloatField(blank=True, null=True)
    sql_queries = models.FloatField(blank=True, null=True)

    # Cache stats
    cache_num_calls = models.IntegerField(blank=True, null=True)
    cache_time = models.FloatField(blank=True, null=True)
    cache_hits = models.IntegerField(blank=True, null=True)
    cache_misses = models.IntegerField(blank=True, null=True)
    cache_sets = models.IntegerField(blank=True, null=True)
    cache_gets = models.IntegerField(blank=True, null=True)
    cache_get_many = models.IntegerField(blank=True, null=True)
    cache_deletes = models.IntegerField(blank=True, null=True)
    cache_calls = models.TextField(default='')

    def __unicode__(self):
        return u'DebugLogRecord from %s' % self.timestamp
