from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django_web_profiler.models import ProfileLogRecord
from django.core.management import call_command
from django.test import Client


# Create your tests here.
class profiler_get_views_test(TestCase):

    def setUp(self):
        for i in range(0, 20):
            User.objects.create(username='test_' + str(i), email='test_' + str(i))

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users.html')

        response = self.client.get('/profiler/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiler_base.html')

    def test_logs(self):
        response = self.client.get('/profiler/device-records-list/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'device_log_detail.html')

    def test_management_command(self):
        args = []
        opts = {}

        call_command('logging_urls', *args, **opts)

    # def test_log_detail(self):
    #     self.log = ProfileLog.objects.first()
    #     print (self.log)
    #     if self.log:
    #         url = reverse('django_web_profiler:records_list', kwargs={'record_id': self.log.id})
    #         response = self.client.get(url)
    #         self.assertEqual(response.status_code, 200)
    #         self.assertTemplateUsed(response, 'log_detail.html')


class TestAppViews(TestCase):
    client = Client()

    def test_ip_graph(self):
        response = self.client.get('/ip/graph/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ip_graph.html')

    def test_path_graph(self):
        response = self.client.get('/path/graph/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'path_graph.html')
