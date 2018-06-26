import locale
import urllib

from django.contrib import admin
from django.db import models
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms import ModelForm, ModelChoiceField, BooleanField, ValidationError
from django.forms.widgets import TextInput
from sorl.thumbnail.admin import AdminImageMixin
from sorl.thumbnail import get_thumbnail
from suit.widgets import AutosizedTextarea
from reversion.admin import VersionAdmin
from relatedwidget import RelatedWidgetWrapperBase
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from rangefilter.filter import DateRangeFilter

import coversheets.models
from forms import AlbumUpload
from coversheets.widgets import AmPmSuitSplitDateTimeWidget

UserAdmin.list_display = ('first_name', 'last_name', 'email', 'is_active')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Default settings based on the user's environment.
locale.setlocale(locale.LC_ALL, '')

# Register your models here.
admin.site.register(coversheets.models.ProgramType)
admin.site.register(coversheets.models.Insurance)
admin.site.register(coversheets.models.JobStatus)
admin.site.register(coversheets.models.LossType)
admin.site.register(coversheets.models.AdjusterType)
admin.site.register(coversheets.models.ReferralType)

admin.site.register(coversheets.models.DocumentSource)
admin.site.register(coversheets.models.DocumentType)


class AdjusterForm(ModelForm):
    class Meta:
        widgets = {
                'phone_ext': TextInput(attrs={'style': 'width:60px'}),
                'mobile_ext': TextInput(attrs={'style': 'width:60px'}),
                'fax_ext': TextInput(attrs={'style': 'width:60px'}),
                'phone': TextInput(attrs={'style': 'width:100px'}),
                'mobile': TextInput(attrs={'style': 'width:100px'}),
                'fax': TextInput(attrs={'style': 'width:100px'}),
            }

@admin.register(coversheets.models.Adjuster)
class AdjusterAdmin(admin.ModelAdmin):
    list_display = ['name', 'insurance_company', 'email', 'adjuster_type']
    search_fields = ['name', 'insurance_company__name', 'email', 'phone', 'mobile']
    form = AdjusterForm

    fieldsets = (
        ('', {
            'fields': (
            ('name',),
            ('adjuster_type', ),
            ('insurance_company',),
            ('email',),
            ('phone', 'phone_ext'),
            ('mobile', 'mobile_ext'),
            ('fax', 'fax_ext'),
            )
        }
        ),
    )


@admin.register(coversheets.models.Document)
class DocumentAdmin(admin.ModelAdmin):
    list_filter = ['jobsheet', 'type', 'created_at', 'source', 'file']
    list_display = ['jobsheet', 'type', 'created_at', 'source', 'description']
    search_fields = ['type__type', 'source__name', 'file', 'jobsheet__customer', 'description', 'created_at',]
    actions = ['email', ]
    actions_on_top = True

    def email(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect(reverse('email_doc') + "?ids={}".format(','.join(selected)))
    email.short_description = "Email"

def email_img(modeladmin, request, queryset):
    selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
    return HttpResponseRedirect(reverse('email_pic') + "?ids={}".format(','.join(selected)))
email_img.short_description = "Email"

@admin.register(coversheets.models.Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['thumb', 'description']
    search_fields = ['description']
    list_filter = ['album']
    actions = ['email', ]
    actions_on_top = True

    def email(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect(reverse('email_pic') + "?ids={}".format(','.join(selected)))
    email.short_description = "Email"

    def thumb(self, obj):
        if obj is not None:
            thumbnail = get_thumbnail(obj.image_file, "200x200")
            return u'<img src="{}"/>'.format(thumbnail.url)
    thumb.short_description = 'Image'
    thumb.allow_tags = True
    thumb.admin_order_field = 'image_file'

@admin.register(coversheets.models.Note)
class JobNoteAdmin(admin.ModelAdmin):
    model = coversheets.models.Note
    search_fields = ['comment', 'jobsheet_id']
    list_display = ['created_at', 'created_by', 'jobsheet']

class JobNoteInlineForm(ModelForm):
    class Meta:
        widgets = {
            'comment': AutosizedTextarea(attrs={'class': 'input-medium', 'rows': 5, 'style': 'width:95%'})
        }

class JobNoteAdminViewInline(admin.TabularInline):
    form = JobNoteInlineForm
    model = coversheets.models.Note
    readonly_fields = ("comment_html", "created_by", "created_at", "cc1", "cc2")
    fields = ("comment_html", "created_by", "created_at", "cc1", "cc2")
    ordering = ('-created_at',)
    extra = 0
    suit_classes = 'suit-tab suit-tab-notes'

    def comment_html(self, note):
        if note.comment:
            return note.comment.replace('\n', '<br>')
    comment_html.allow_tags = True

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class JobNoteAdminAddInline(admin.StackedInline):
    form = JobNoteInlineForm
    model = coversheets.models.Note
    #readonly_fields = ("created_by", "created_at")
    fields = ('comment', 'cc1', 'cc2')
    extra = 1
    verbose_name_plural = "Add Notes"
    suit_classes = 'suit-tab suit-tab-notes'

    def has_change_permission(self, request, obj=None):
        return False


class DocumentInlineForm(ModelForm):
    class Meta:
        widgets = {
            'description': AutosizedTextarea(attrs={'class': 'input-medium', 'rows': 2, 'style': 'width:95%'})
        }

class DocumentAdminViewInline(admin.TabularInline):
    form = DocumentInlineForm
    model = coversheets.models.Document
    readonly_fields = ['type', 'created_at', 'source', 'description', 'file_link', 'file', 'email_doc']
    ordering = ('-created_at',)
    extra = 0
    suit_classes = 'suit-tab suit-tab-docs'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class DocumentAdminAddInline(admin.TabularInline):
    form = DocumentInlineForm
    model = coversheets.models.Document
    extra = 1
    fields = ['type', 'source', 'description', 'file']
    verbose_name_plural = "Add Documents"
    suit_classes = 'suit-tab suit-tab-docs'

    def has_change_permission(self, request, obj=None):
        return False

class ImageForm(ModelForm):
    class Meta:
        widgets = {
            'description': AutosizedTextarea,
        }


class ImageAdminInline(AdminImageMixin, admin.TabularInline, ):
    model = coversheets.models.Image
    form = ImageForm
    readonly_fields = ['email']


class AlbumForm(ModelForm):
    class Meta:
        widgets = {
            'description': AutosizedTextarea,
        }

@admin.register(coversheets.models.Album)
class AlbumAdmin(admin.ModelAdmin):
    form = AlbumUpload
    inlines = (ImageAdminInline, )
    suit_form_includes = (
        ('admin/coversheets/email_all_button.html', 'top',),
    )
    suit_classes = 'suit-tab suit-tab-job_info'

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:  # obj is not None, so this is a change page
            kwargs['form'] = AlbumUpload
        return super(AlbumAdmin, self).get_form(request, obj, **kwargs)

    def get_formsets(self, request, obj=None):
        if obj is not None:
            for inline in self.get_inline_instances(request, obj):
                yield inline.get_formset(request, obj)

class AlbumAddAdminInline(AdminImageMixin, admin.TabularInline):
    model = coversheets.models.Album
    form = AlbumUpload
    extra = 0
    readonly_fields = ['pictures']
    suit_classes = 'suit-tab suit-tab-albums'

    def has_change_permission(self, request, obj=None):
        return False


class AlbumAdminViewInline(AdminImageMixin, admin.TabularInline):
    form = AlbumForm
    extra = 0
    model = coversheets.models.Album
    readonly_fields = ['pictures']
    suit_classes = 'suit-tab suit-tab-albums'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class CustomUserChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s %s" % (obj.first_name, obj.last_name)



class EstimatorFilter(admin.SimpleListFilter):

    title = 'Estimator'
    parameter_name = 'estimator'

    def lookups(self, request, model_admin):
        estimators_by_fist_name = User.objects.filter(groups__name='Estimators', is_active=True).order_by('first_name')
        return ((user.id, user.first_name + " " + user.last_name) for user in estimators_by_fist_name)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(estimator__id=self.value())
        else:
            queryset.all()


class SuperFilter(admin.SimpleListFilter):

    title = 'Super'
    parameter_name = 'super'

    def lookups(self, request, model_admin):
        supers_by_fist_name = User.objects.filter(groups__name='Superintendents', is_active=True).order_by('first_name')
        return ((user.id, user.first_name + " " + user.last_name) for user in supers_by_fist_name)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(super__id=self.value())
        else:
            queryset.all()

class JobForm(ModelForm):
    estimator = CustomUserChoiceField(queryset=User.objects.filter(groups__name='Estimators', is_active=True).order_by('first_name'), required=False)
    super = CustomUserChoiceField(queryset=User.objects.filter(groups__name='Superintendents', is_active=True).order_by('first_name'), required=False)
    production_manager = CustomUserChoiceField(queryset=User.objects.filter(groups__name='Production Managers', is_active=True).order_by('first_name'), required=False)
    same_as_loss_address = BooleanField(required=False)

    def clean(self):
        cleaned_data = super(JobForm, self).clean()
        same_as_loss_addr = cleaned_data.get("same_as_loss_address")
        if not same_as_loss_addr:
            if (cleaned_data.get('customer_address') is None or
                        cleaned_data.get('city') is None or
                        cleaned_data.get('zip') is None):
                raise ValidationError('Must include mailing address or mark same as loss address')

        return cleaned_data

    class Meta:
        widgets = {
            'additional_info': AutosizedTextarea(attrs={'style': 'width:55%'}),
            'loss_information': AutosizedTextarea(attrs={'style': 'width:55%'}),
            'entry_date': AmPmSuitSplitDateTimeWidget(),
            'primary_phone_ext': TextInput(attrs={'style': 'width:60px'}),
            'mobile_phone_ext': TextInput(attrs={'style': 'width:60px'}),
            'contact_info_1_ext': TextInput(attrs={'style': 'width:60px'}),
            'contact_info_2_ext': TextInput(attrs={'style': 'width:60px'}),
            #DateTimePicker(options={"format": "YYYY-MM-DD", "pickTime": True})
        }


class JobStatusFilter(admin.SimpleListFilter):
    title = 'Show Declined Jobs'
    parameter_name = 'show_declined'
    template = 'job_status_filter.html'

    def lookups(self, request, model_admin):
        return (
            ('a', 'b'),
            ('c', 'd')
        )

    def queryset(self, request, queryset):
        show = request.GET.get('show_declined')
        if show:
            return queryset.all()
        else:
            return queryset.exclude(status__status='Declined')


@admin.register(coversheets.models.Job)
class JobAdmin(RelatedWidgetWrapperBase, VersionAdmin):
    form = JobForm
    list_per_page = 50
    ordering = ('-entry_date',)
    list_display = [
        "customer",
        "loss_address",
        "city",
        "loss_zip",
        "entry_date",
        "job_number_or_empty_string",
        "estimator_name",
        "super_name",
        "insurance_company",
        "loss_type",
        "status",
        "value",
        "program_type"
    ]

    list_filter = [
        EstimatorFilter,
        SuperFilter,
        'status',
        JobStatusFilter,
        ('entry_date', DateRangeFilter),
    ]

    search_fields = [
        'additional_info',
        'customer',
        'customer_address',
        # 'city',
        # 'zip',
        'customer_email',
        'contact',
        'contact_email',
        'emergency_dispatch',
        'loss_address',
        # 'loss_city__name',
        'id',
        'info_entered_at',
        'customer',
        'primary_phone',
        'mobile_phone',
        'claim_number',
        'adjuster__name',
        'adjuster__email',
        'adjuster__phone',
        'adjuster__mobile',
        'adjuster__fax',
        'contact_info_1',
        'contact_info_2',
        'job_number',
        'insurance_company__name',
        'claim_date',
        'claim_number',
        'policy_number',
        'deductible',
        'contact_info_1',
        'contact_info_2',
        'job_number',
        'program_type__type',
        'called_in_by',
        'loss_type__type',
        'estimated_loss',
        'referral_type__type',
        'referred_by',
        'estimator',
        'super',
        'production_manager',
    ]


    suit_form_tabs = (
        ('job_info', 'Job info',),
        ('notes', 'Notes'),
        ('docs', 'Documents'),
        ('albums', 'Albums')
    )
    inlines = (DocumentAdminAddInline, DocumentAdminViewInline, JobNoteAdminAddInline, JobNoteAdminViewInline, AlbumAddAdminInline, AlbumAdminViewInline)
    readonly_fields = (
        'info_updated_by',
        'info_taken_by',
        'info_updated_at',
        'info_entered_at',
        'pictures',
        'adjuster_phone',
        'adjuster_mobile',
        'adjuster_fax',
        'adjuster_email',
        'ind_adjuster_phone',
        'ind_adjuster_mobile',
        'ind_adjuster_fax',
        'ind_adjuster_email',
        'job_number_or_empty_string',
        'map'
    )

    suit_form_includes = (
        ('admin/coversheets/print_job_button.html', 'top', 'job_info'),
        ('admin/coversheets/document_search_button.html', 'middle', 'docs'),
    )

    fieldsets = (
        ('Customer/Contact Information',  {
            'classes': ('suit-tab suit-tab-job_info',),
            'fields': (
                ('customer', 'customer_email'),
                ('contact_info_1', 'contact_info_1_ext'),
                ('contact_info_2', 'contact_info_2_ext'),
                ('contact', 'contact_email'),
                ('primary_phone', 'primary_phone_ext',),
                ('mobile_phone', 'mobile_phone_ext'),
                ('same_as_loss_address'),
                ('customer_address', 'city', 'zip')),
        }),

        ('Loss Location', {
            'classes': ('suit-tab suit-tab-job_info',),
            'fields': ('loss_address', 'loss_city', 'loss_zip', 'loss_information', 'loss_year_built', 'map'),
        }),

        ('', {
            'classes': ('suit-tab suit-tab-job_info',),
            'fields':  ('additional_info',),
        }),

        ('Insurance', {
            'classes': ('suit-tab suit-tab-job_info',),
            'fields': (
                'insurance_company',
                ('adjuster', 'independent_adjuster'),
                ('adjuster_email', 'ind_adjuster_email'),
                ('adjuster_phone', 'ind_adjuster_phone'),
                ('adjuster_mobile', 'ind_adjuster_mobile'),
                ('adjuster_fax', 'ind_adjuster_fax'),
                'claim_date',
                'claim_number',
                'policy_number',
                'deductible'
            ),
        }),

        ('Call Data', {
            'classes': ('suit-tab suit-tab-job_info',),
            'fields': (('program_type', 'called_in_by'), ('loss_type', 'estimated_loss'), ('referral_type', 'referred_by'),)
        }),

        ('Assignments', {
            'classes': ('suit-tab suit-tab-job_info',),
            'fields': ('estimator', 'super', 'production_manager')
        }),

        ('Job Info', {
            'classes': ('suit-tab suit-tab-job_info',),
            'fields': (
                'percent_complete',
                'estimated_completion_date',
                'program_due_date',
                'production_start_date',
                'pending_items',
                'album_link',
                'budget_link',
                'schedule_link'
            )
        }),

        ('Last Update', {
            'classes': ('suit-tab suit-tab-job_info',),
            'fields': ('status', 'info_updated_by', 'info_updated_at', 'job_number', 'add_job_number')
        }),

        ('Created by', {
            'classes': ('suit-tab suit-tab-job_info',),
            'fields': ('entry_date', 'info_entered_at', 'info_taken_by', )
        }),

        ('', {
            'classes': ('suit-tab suit-tab-job_info',),
            'fields': ( 'emergency_requested', 'emergency_dispatch'),
        }),

        ('', {
            'classes': ('suit-tab suit-tab-job_info',),
            'fields':  ((),),
        }),
    )

    def map(self, obj):
        if obj.loss_address is not None and obj.loss_city is not None:
            iframe = """<iframe
  width="600"
  height="450"
  frameborder="0" style="border:0"
  src="https://www.google.com/maps/embed/v1/place?key=AIzaSyBWjTTvBY7LF9fPCWvE8TwCjbgWMo9jbUI
    &q={} {}">
</iframe>""".format(obj.loss_address, obj.loss_city)
            return iframe
        else:
            return "No Map"
    map.allow_tags = True

    def adjuster_phone(self, obj):
        if obj.adjuster is not None:
            return obj.adjuster.full_phone()
        else:
            return ''

    def adjuster_email(self, obj):
        if obj.adjuster is not None:
            if obj.claim_number is not None:
                return '<a href=mailto:{0}?Subject={1}.%20Claim%20#%20{2}>{0}</a>'.format(obj.adjuster.email, urllib.quote(obj.customer), urllib.quote(obj.claim_number))
            else:
                return '<a href=mailto:{0}?Subject={1}>{0}</a>'.format(obj.adjuster.email, obj.customer)
        else:
            return ''
    adjuster_email.allow_tags = True

    def adjuster_mobile(self, obj):
        if obj.adjuster is not None:
            return obj.adjuster.full_mobile()
        else:
            return ''

    def adjuster_fax(self, obj):
        if obj.adjuster is not None:
            return obj.adjuster.full_fax()
        else:
            return ''

    def ind_adjuster_phone(self, obj):
        if obj.independent_adjuster is not None:
            return obj.independent_adjuster.full_phone()
        else:
            return ''

    def ind_adjuster_email(self, obj):
        if obj.independent_adjuster is not None:
            if obj.claim_number is not None:
                return '<a href=mailto:{0}?Subject={1}.%20Claim%20#%20{2}>{0}</a>'.format(obj.independent_adjuster.email, urllib.quote(obj.customer), urllib.quote(obj.claim_number))
            else:
                return '<a href=mailto:{0}?Subject={1}>{0}</a>'.format(obj.independent_adjuster.email, obj.customer)
        else:
            return ''
    ind_adjuster_email.allow_tags = True

    def ind_adjuster_mobile(self, obj):
        if obj.independent_adjuster is not None:
            return obj.independent_adjuster.full_mobile()
        else:
            return ''

    def ind_adjuster_fax(self, obj):
        if obj.independent_adjuster is not None:
            return obj.independent_adjuster.full_fax()
        else:
            return ''

    def value(self, obj):
        if obj.estimated_loss is not None:
            return "$" + locale.format("%d", obj.estimated_loss, grouping=True)
        else:
            return '-'
    value.admin_order_field = 'estimated_loss'

    def super_name(self, obj):
        if obj.super is not None:
            return obj.super.first_name + " " + obj.super.last_name
    super_name.short_description = "super"
    super_name.admin_order_field = 'super__first_name'

    def super_name(self, obj):
        if obj.super is not None:
            return obj.super.first_name + " " + obj.super.last_name
        else:
            return ""
    super_name.short_description = "super"
    super_name.admin_order_field = 'super__first_name'

    def production_manager_name(self, obj):
        if obj.production_manager is not None:
            return obj.production_manager.first_name + " " + obj.production_manager.last_name
        else:
            return ""
    production_manager_name.short_description = "Production Mgr"
    production_manager_name.admin_order_field = 'production_manager__first_name'

    def estimator_name(self, obj):
        if obj.estimator is not None:
            return obj.estimator.first_name + " " + obj.estimator.last_name
        else:
            return ""
    estimator_name.short_description = "estimator"
    estimator_name.admin_order_field = 'estimator__first_name'

    def job_number_or_empty_string(self, obj):
        if obj.job_number is not None:
            return obj.job_number
        else:
            return ""
    job_number_or_empty_string.short_description = "Job Number"
    job_number_or_empty_string.admin_order_field = 'job_number'

    def save_model(self, request, obj, form, change):
        """
        Saves the form into a new model instance. For the job, we want to copy over the loss address to contact address
        if contact address is blank and use the adjuster's insurance information instead of what may have been
        previously selected.
        :param request:
        :param obj: and instance of the model being created, in this case, a job
        :param form:
        :param change:
        :return:
        """
        if obj.city == '' or obj.customer_address == '' or obj.zip == '':
            # The only way that this can be blank is if the "same as loss address" box was checked, so copy the
            # information from loss address into the contact address.
            obj.city = obj.loss_city
            obj.customer_address = obj.loss_address
            obj.zip = obj.loss_zip

        if obj.adjuster is not None and obj.adjuster.insurance_company_id is not None:
            obj.insurance_company_id = obj.adjuster.insurance_company_id

        if obj.add_job_number == True and obj.job_number is None:
            new_job_number = coversheets.models.Job.objects.all().aggregate(models.Max('job_number'))
            if new_job_number['job_number__max'] is not None:
                obj.job_number = new_job_number['job_number__max'] + 1
            else:
                obj.job_number = 1
        obj.save()

    def get_form(self, request, obj=None, **kwargs):
        form = super(JobAdmin, self).get_form(request, obj, **kwargs)
        for key in form.base_fields.keys():
            form.base_fields[key].widget.can_delete_related = False
            form.base_fields[key].widget.can_edit_related = False
        form.base_fields['city'].widget.can_edit_related = False
        form.base_fields['adjuster'].widget.can_edit_related = True
        return form

    def get_readonly_fields(self, request, obj=None):
        if obj is not None and obj.add_job_number:
            return self.readonly_fields + ('add_job_number',)
        return self.readonly_fields
