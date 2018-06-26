#!/usr/bin/env python

from django.forms import Form, ModelForm, RadioSelect, DateField, CharField, ChoiceField, BooleanField, IntegerField, HiddenInput, MultipleChoiceField
from django.forms.widgets import SelectMultiple
from django.forms.widgets import Textarea, NumberInput
from multi_email_field.forms import MultiEmailField, MultiEmailWidget
from bootstrap3_datetime.widgets import DateTimePicker
from models import Album, Image, JobStatus
from multiupload.fields import MultiFileField


class AlbumUpload(ModelForm):
    """
    Multiupload method
    """
    files = MultiFileField(min_num=0, max_num=50, max_file_size=1024 * 1024 * 50, required=False)

    def save(self, commit=True):
        album = self.instance
        album.save()
        file_list = self.cleaned_data['files']
        images = [Image(image_file=file, album=album) for file in file_list]
        for image in images:
            image.save()
        return album

    def save_m2m(self):
        pass

    class Meta:
        model = Album
        exclude = []


class Report(Form):
    sort_choices = [
        ['Adjuster', 'Adjusters'],
        ['Entry Date', 'Entry Date'],
        ['Estimator', 'Estimator'],
        ['Superintendent', 'Superintendent'],
        ['InsuranceCo', 'InsuranceCo'],
        ['LossType', 'LossType'],
        ['Program', 'Program'],
        ['Referral', 'Referral'],
        ['Status', 'Status']
    ]
    group_choices = [
        ['Adjuster', 'Adjusters'],
        ['Entry Date', 'Entry Date'],
        ['Estimator', 'Estimator'],
        ['Superintendent', 'Superintendent'],
        ['InsuranceCo', 'InsuranceCo'],
        ['LossType', 'LossType'],
        ['Program', 'Program'],
        ['Referral', 'Referral'],
        ['Status', 'Status']
    ]

    group_by = ChoiceField(choices=group_choices)
    sort_by = ChoiceField(choices=sort_choices)
    date_type = ChoiceField(choices=[['last_days', 'Recent'],
                                     ['date_range', "Date Range"]], widget=RadioSelect(), initial='last_days')
    last_days = ChoiceField(choices=[[7,7], [30, 30], [365, 365]])
    start = DateField(required=False, widget=DateTimePicker(options={"format": "YYYY-MM-DD",
                                       "pickTime": False}))
    end = DateField(required=False, widget=DateTimePicker(options={"format": "YYYY-MM-DD",
                                       "pickTime": False}))
    most_recent_note = BooleanField(required=False, initial=False)
    show_empty = BooleanField(required=False)
    show_all_statuses = BooleanField(required=False, initial=True)

    statuses = MultipleChoiceField()

    def __init__(self, *args, **kwargs):
        super(Report, self).__init__(*args, **kwargs)
        statuses = [status.status for status in JobStatus.objects.all()]
        self.fields['statuses'] = MultipleChoiceField(zip(statuses, statuses),
                                                      required=False,
                                                      widget=SelectMultiple(attrs={'size': '13'}))

class EmailObjs(Form):
    subject = CharField(max_length=255)

    to = MultiEmailField(widget=MultiEmailWidget(attrs={'rows': 1, 'width': '50%'}))
    cc = MultiEmailField(widget=MultiEmailWidget(attrs={'rows': 1, 'width': '50%'}), required=False)
    bcc = MultiEmailField(widget=MultiEmailWidget(attrs={'rows': 1, 'width': '50%'}), required=False)

    body = CharField(max_length=4096, widget=Textarea(attrs={'rows': 14, 'style': "width: 50%"}))

    obj_ids = CharField(max_length=1024, widget=HiddenInput(attrs={'readonly': True}))
