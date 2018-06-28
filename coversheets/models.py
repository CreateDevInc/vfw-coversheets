from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from cities_light.models import City, Region
from django_localflavor_us.models import PhoneNumberField
from sorl.thumbnail import ImageField
from cuser.fields import CurrentUserField
from django.conf import settings
from django.core.mail import send_mail
from django.core import urlresolvers
from email.utils import formataddr
import datetime


class ProgramType(models.Model):
    type = models.CharField(max_length=255)

    def __str__(self):
        return self.type

    class Meta:
        ordering = ['type']


class JobStatus(models.Model):
    status = models.CharField(max_length=255)

    def __str__(self):
        return self.status

    class Meta:
        verbose_name_plural = "Job Statuses"
        ordering = ['status']


class LossType(models.Model):
    loss_type = models.CharField(max_length=255)

    def __str__(self):
        return self.loss_type

    class Meta:
        ordering = ['loss_type']


class AdjusterType(models.Model):
    adjuster_type = models.CharField(max_length=255)

    def __str__(self):
        return self.adjuster_type

    class Meta:
        ordering = ['adjuster_type']


class ReferralType(models.Model):
    referral_type = models.CharField(max_length=255)

    def __str__(self):
        return self.referral_type

    class Meta:
        ordering = ['referral_type']


class Job(models.Model):
    info_taken_by = CurrentUserField(add_only=True, related_name="created_job", blank=True)
    info_updated_by = CurrentUserField(related_name="updated_job", blank=True)

    info_entered_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    info_updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    entry_date = models.DateTimeField(default=datetime.datetime.now, null=True, blank=True)

    status = models.ForeignKey(JobStatus, null=True, blank=True)
    add_job_number = models.BooleanField(default=False, blank=True)
    job_number = models.PositiveIntegerField(unique=True, null=True, blank=True)

    # Assignments, Users in the system that have these groups can be assigned here.
    estimator = models.ForeignKey("auth.User", blank=True, null=True, limit_choices_to={'groups__name': "Estimators",
                                                                                        'is_active': True}, related_name="job_estimator")
    super = models.ForeignKey("auth.User", blank=True, null=True, limit_choices_to={'groups__name': "Superintendents",
                                                                                        'is_active': True}, related_name="job_super")
    production_manager = models.ForeignKey("auth.User", blank=True, null=True, limit_choices_to={'groups__name': "Production Managers",
                                                                                        'is_active': True}, related_name="job_project_manager")

    percent_complete = models.CharField(max_length=255, null=True, blank=True)
    estimated_completion_date = models.DateField(null=True, blank=True)
    program_due_date = models.DateField(null=True, blank=True)
    production_start_date = models.DateField(null=True, blank=True)
    pending_items = models.CharField(max_length=1000, null=True, blank=True)
    album_link = models.CharField(max_length=255, null=True, blank=True)
    budget_link = models.CharField(max_length=512, null=True, blank=True)
    schedule_link = models.CharField(max_length=512, null=True, blank=True)

    #Call info

    program_type = models.ForeignKey(ProgramType, blank=True, null=True)
    called_in_by = models.CharField(max_length=200, blank=True)
    loss_type = models.ForeignKey(LossType, blank=True, null=True)
    estimated_loss = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    referral_type = models.ForeignKey(ReferralType, null=True, blank=True)
    referred_by = models.CharField(max_length=255, blank=True, null=True)

    #Customer and contact info
    customer = models.CharField(max_length=255, blank=True)
    customer_email = models.EmailField(blank=True, null=True)
    contact_info_1 = PhoneNumberField(blank=True, null=True)
    contact_info_1_ext = models.CharField(max_length=64, blank=True, null=True)
    contact_info_1.verbose_name = 'Best Contact Phone'
    contact_info_1_ext.verbose_name = 'ext.'

    contact_info_2 = PhoneNumberField(blank=True, null=True)
    contact_info_2_ext = models.CharField(max_length=64, blank=True, null=True)
    contact_info_2.verbose_name = 'Addtional Contact Phone'
    contact_info_2_ext.verbose_name = 'ext.'

    contact = models.CharField(max_length=255, null=True, blank=True)
    contact_email = models.EmailField(blank=True)

    primary_phone = PhoneNumberField(blank=True)
    primary_phone_ext = models.CharField(max_length=64, blank=True, null=True)
    primary_phone_ext.verbose_name = 'ext.'

    mobile_phone = PhoneNumberField(blank=True, null=True)
    mobile_phone_ext = models.CharField(max_length=64, blank=True, null=True)
    mobile_phone_ext.verbose_name = 'ext.'

    customer_address = models.CharField(max_length=128, blank=True, null=True)
    customer_address.verbose_name = 'Customer Mailing Address'
    city = models.ForeignKey(City, related_name="job_city_customer", blank=True, null=True)
    zip = models.CharField(max_length=10, blank=True, null=True)

    loss_address = models.CharField(max_length=128, blank=True, null=True)
    loss_city = models.ForeignKey(City, related_name="job_city_loss", blank=True, null=True)
    loss_zip = models.CharField(max_length=10, blank=True, null=True)
    loss_year_built = models.DateField(blank=True, null=True)
    loss_information = models.TextField(max_length=4000, blank=True, null=True)

    # insurance information
    adjuster = models.ForeignKey('Adjuster', null=True, blank=True)
    independent_adjuster = models.ForeignKey('Adjuster', null=True, blank=True, related_name='independent_adjuster')
    insurance_company = models.ForeignKey("Insurance", null=True, blank=True)

    claim_date = models.DateField(blank=True, null=True)
    claim_number = models.CharField(max_length=255, blank=True, null=True)
    deductible = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    deductible_collected = models.BooleanField(default=False, null=False, blank=True)
    policy_number = models.CharField(max_length=255, blank=True, null=True)

    emergency_requested = models.BooleanField(default=False, null=False, blank=True)
    emergency_dispatch = models.CharField(max_length=255, blank=True, null=True)  # Strange field that can be used for user names, company names, or a description of what happened for the emergency.
    additional_info = models.TextField(max_length=4000, blank=True, null=True)

    @property
    def deductable_d(self):
        return "$%s" % self.deductible if self.deductible else ""

    @property
    def value(self):
        return "$%s" % self.estimated_loss if self.estimated_loss else ""

    def pictures(self):
        target = self.album
        if target is not None:
            return u'<a href="%s">Edit</a> |  <a href="%s">View</a>' % (reverse("admin:coversheets_album_change", args=[target.id]), reverse('show_album', args=[target.id]))
        return None
    pictures.allow_tags = True

    def loss_location(self):
        return self.loss_address + "<br>" + str(self.loss_city)
    loss_location.allow_tags = True

    def most_recent_note(self):
        most_recent = self.note_set.latest('created_at')
        return str(most_recent) + "\n" + most_recent.comment

    def __str__(self):
        return self.customer


class Adjuster(models.Model):
    name = models.CharField(max_length=255)
    adjuster_type = models.ForeignKey("AdjusterType", null=True)
    phone = PhoneNumberField(blank=True)
    phone_ext = models.CharField(max_length=64, blank=True)
    phone_ext.verbose_name = 'ext.'

    fax = PhoneNumberField(blank=True)
    fax_ext = models.CharField(max_length=64, blank=True)
    fax_ext.verbose_name = 'ext.'

    mobile = PhoneNumberField(blank=True)
    mobile_ext = models.CharField(max_length=64, blank=True)
    mobile_ext.verbose_name = 'ext.'

    email = models.EmailField(blank=True)
    insurance_company = models.ForeignKey("Insurance", null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

    def full_phone(self):
        return self.phone + ' ' + self.phone_ext if self.phone_ext != '' else self.phone

    def full_mobile(self):
        return self.mobile + ' ' + self.mobile_ext if self.mobile_ext != '' else self.mobile

    def full_fax(self):
        return self.fax + ' ' + self.fax_ext if self.fax_ext != '' else self.fax

class Album(models.Model):
    name = models.CharField(max_length=255, default="", blank=True)
    description = models.CharField(max_length=2048, default="", blank=True)
    job = models.ForeignKey(Job, null=True, blank=True, related_name='job')

    def pictures(self):
        if self.id is not None:
            return u'<a href="%s">Edit</a> |  <a href="%s">View</a>' % (reverse("admin:coversheets_album_change", args=[self.id]), reverse('show_album', args=[self.id]))
        else:
            return ''
    pictures.allow_tags = True

    def __str__(self):
        if "" != self.name:
            return self.name
        else:
            return str(self.id)


class Image(models.Model):
    image_file = ImageField(upload_to='photos')
    description = models.CharField(max_length=2048, blank=True, default='')
    album = models.ForeignKey(Album, null=True)

    def email(self):
        return "<a href=" + reverse('email_pic') + "?ids={}".format(self.pk) + "> Email </a>"
    email.allow_tags = True

class DocumentSource(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class DocumentType(models.Model):
    type = models.CharField(max_length=255)

    def __str__(self):
        return self.type

class Document(models.Model):
    description = models.TextField(max_length=1024, blank=True, )
    file = models.FileField(upload_to='documents', max_length=512)
    jobsheet = models.ForeignKey(Job)
    type = models.ForeignKey(DocumentType, null=True)
    source = models.ForeignKey(DocumentSource, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def file_link(self):
        if self.file:
            return "<a href='%s'> Download" % self.file.url
        else:
            return "No attachment yet."
    file_link.allow_tags = True

    def email_doc(self):
        """
        Creates a popup link for use in the admin to email_doc this document
        :return:
        """
        link = reverse('email_doc') + "?ids={}".format(self.pk)
        return "<a href='{}' onclick='return showAddAnotherPopup(this);'> Send as Email </a>".format(link)
    email_doc.short_description = 'Send Email'
    email_doc.allow_tags = True

    def __str__(self):
        return self.file.name

    def verbose_str(self):
        return str(self.jobsheet) + " " + str(self.type) + " from " + str(self.source) + ": " + self.file.name


class Note(models.Model):

    created_by = CurrentUserField(add_only=True, related_name="created_note", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    comment = models.TextField(max_length=10000)
    jobsheet = models.ForeignKey(Job)

    cc1 = models.EmailField(null=True, blank=True)
    cc2 = models.EmailField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super(Note, self).save(*args, **kwargs)
        if settings.SEND_EMAIL_NOTIFCATIONS:
            managers = Group.objects.get(name="Management")
            emails = {user.email for user in managers.user_set.all()}
            if self.jobsheet.estimator is not None:
                emails.add(self.jobsheet.estimator.email)
            if self.jobsheet.super is not None:
                emails.add(self.jobsheet.super.email)
            if self.jobsheet.production_manager is not None:
                emails.add(self.jobsheet.production_manager.email)
            domain = Site.objects.get_current().domain

            # exclude people on vaction
            on_vacation = Group.objects.get(name="On Vacation")
            on_vacation_emails = {user.email for user in on_vacation.user_set.all()}
            emails = emails - on_vacation_emails

            # add any email_doc that was cc'd, even if they are on vacation

            if self.cc1 != '':
                emails.add(self.cc1)
            if self.cc2 != '':
                emails.add(self.cc2)

            model_url = "https://" + domain + urlresolvers.reverse('admin:coversheets_job_change', args=(self.jobsheet.id,)) + "#notes"
            model_url_html = "<a href='https://" + domain + urlresolvers.reverse('admin:coversheets_job_change', args=(self.jobsheet.id,)) + "#notes'>Reply</a>"
            subject = 'Coversheet note - ' + self.jobsheet.customer
            body_header = str(self.jobsheet.program_type) + ' / ' + self.jobsheet.customer + ' / ' + str(self.jobsheet.loss_type)
            body = body_header + '\n' + self.comment +"\n----\n" + model_url
            body_html = body_header + '<br>' + self.comment.replace('\n', '<br>') + "<br>----<br>" + model_url_html
            from_header = formataddr((self.created_by.first_name + " " + self.created_by.last_name, self.created_by.email))
            send_mail(subject, self.comment +"\n----\n" + model_url, from_header, emails, html_message=body_html)

    def __str__(self):
        return str(self.created_by) + " on " + str(self.jobsheet) + " at " + self.created_at.strftime('%Y-%m-%d %H:%M:%S')


class Insurance(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        if self.name is not None:
            return self.name
        else:
            return str(self.id)

    class Meta:
        ordering = ['name']
