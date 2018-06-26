from django.conf.urls import patterns, url
from django.contrib import admin
from coversheets import views


urlpatterns = patterns(
    '',
    url(r'^$', views.home, name='home'),
    url(r'^add_album/', views.add_album, name='add_album'),
    url(r'^show_album/(\d+)/$', views.show_album, name='show_album'),
    url(r'^reports/', views.reports, name='reports'),
    url(r'^email_doc/', views.email_doc, name='email_doc'),
    url(r'^email_pic/', views.email_pics, name='email_pic'),
    url(r'^job_number/', views.get_job_number, name='get_job_number'),
    url(r'^print_job/(\d+)/', views.print_job, name='print_job'),
    url(r'^print_job_with_notes/(\d+)/', views.print_job_with_notes, name='print_job_with_notes'),
)
