from django.conf.urls import patterns, url
from django.contrib import admin
from coversheets import views


urlpatterns = patterns(
    '',
    url(r'^$', views.home, name='home'),
    url(r'^add_album/', views.add_album, name='add_album'),
    url(r'^show_album/(\d+)/$', views.show_album, name='show_album'),
    url(r'^reports/', views.reports, name='reports'),
    url(r'^weekly-production/', views.weekly_production, name='weekly-production'),
    url(r'^estimator-snapshot/', views.estimator_snapshot, name='estimator-snapshot'),
    url(r'^warranty-list/', views.warranty_list, name='warranty-list'),
    url(r'^email_doc/', views.email_doc, name='email_doc'),
    url(r'^email_pic/', views.email_pics, name='email_pic'),
    url(r'^job_number/', views.get_job_number, name='get_job_number'),
    url(r'^job_info/(\d+)/', views.get_job_info, name='get_job_info'),
    url(r'^print_job/(\d+)/', views.print_job, name='print_job'),
    url(r'^print_job_with_notes/(\d+)/', views.print_job_with_notes, name='print_job_with_notes'),
)
