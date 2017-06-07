import math

from django.shortcuts import render, get_object_or_404
from .models import ProfileLog, ProfileLogRecord
from django.db.models import Q


# Create your views here.
def index(request):
    profile_logs = ProfileLog.objects.filter().order_by('-start_time')
    return render(request, 'profiler_base.html', {'profile_logs': profile_logs})


def get_prev_after_pages_count(page, no_pages):
    prev_page = page - 1
    if prev_page == 1:
        previous_page = prev_page
    else:
        previous_page = prev_page - 1
    if page == 1:
        prev_page = page
        previous_page = page

    if page == no_pages:
        aft_page = no_pages
        after_page = no_pages
    else:
        aft_page = page + 1
        if aft_page == no_pages:
            after_page = no_pages
        else:
            after_page = aft_page + 1
    return prev_page, previous_page, aft_page, after_page


def records_list(request, record_id):
    profile_logs = ProfileLog.objects.filter().order_by('-start_time')
    profile_log = get_object_or_404(ProfileLog, id=record_id)
    profile_log_records = ProfileLogRecord.objects.filter(
        profile_log_id=record_id)
    if request.POST.get("search"):
        profile_log_records = profile_log_records.filter(Q(request_path__icontains=request.POST.get(
            "search")) | Q(ip_address__icontains=request.POST.get("search")))
    if request.POST.get("queries"):
        profile_log_records = profile_log_records.filter(Q(sql_queries__lte=request.POST.get(
            "queries")) | Q(timer_utime__lte=request.POST.get("queries")))

    no_of_jobs = profile_log_records.count()
    items_per_page = 10
    no_pages = int(math.ceil(float(no_of_jobs) / items_per_page))
    page = request.POST.get('page')
    if request.method == 'GET':
        page = request.GET.get('page')
    try:
        if int(page) > 0:
            if int(page) > (no_pages + 2):
                page = 1
            else:
                page = int(page)
        else:
            page = 1
    except:
        page = 1

    profile_log_records = profile_log_records[
        (page - 1) * items_per_page:page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages)

    return render(request, 'log_detail.html', {'profile_logs': profile_logs,
                                               'profile_log_records': profile_log_records,
                                               'profile_log': profile_log,
                                               'aft_page': aft_page,
                                               'after_page': after_page,
                                               'prev_page': prev_page,
                                               'previous_page': previous_page,
                                               'current_page': page,
                                               'last_page': no_pages,
                                               'no_of_jobs': no_of_jobs,
                                               })


def device_records_list(request):
    profile_logs = ProfileLog.objects.filter().order_by('-start_time')
    profile_logs_records = ProfileLogRecord.objects.filter(
        device__isnull=False).order_by('-timestamp')
    if request.POST.get("search"):
        profile_logs_records = profile_logs_records.filter(Q(request_path__icontains=request.POST.get(
            "search")) | Q(ip_address__icontains=request.POST.get("search")))
    if request.POST.get("queries"):
        profile_logs_records = profile_logs_records.filter(Q(sql_queries__lte=request.POST.get(
            "queries")) | Q(timer_utime__lte=request.POST.get("queries")))

    no_of_jobs = profile_logs_records.count()
    items_per_page = 10
    no_pages = int(math.ceil(float(no_of_jobs) / items_per_page))
    page = request.POST.get('page')
    if request.method == 'GET':
        page = request.GET.get('page')
    try:
        if int(page) > 0:
            if int(page) > (no_pages + 2):
                page = 1
            else:
                page = int(page)
        else:
            page = 1
    except:
        page = 1

    profile_logs_records = profile_logs_records[
        (page - 1) * items_per_page:page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages)

    return render(request, 'device_log_detail.html', {'profile_logs_records': profile_logs_records,
                                                      'profile_logs': profile_logs,
                                                      'aft_page': aft_page,
                                                      'after_page': after_page,
                                                      'prev_page': prev_page,
                                                      'previous_page': previous_page,
                                                      'current_page': page,
                                                      'last_page': no_pages,
                                                      'no_of_jobs': no_of_jobs,
                                                      })
