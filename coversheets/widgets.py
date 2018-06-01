__author__ = 'Anthony'
from datetimewidget.widgets import TimeWidget, DateWidget
from django import forms
from django.utils.safestring import mark_safe

class AmPmSuitSplitDateTimeWidget(forms.SplitDateTimeWidget):
    def __init__(self, attrs=None, options=None, *args, **kwargs):
        widgets = [DateWidget(options={'format': 'mm/dd/yyyy'}), TimeWidget(options={'showMeridian': True,
                                                                    'format': "HH:ii P"})]
        forms.MultiWidget.__init__(self, widgets, attrs)

    def render(self, name, value, attrs=None):
        output = super(AmPmSuitSplitDateTimeWidget, self).render(name, value, attrs)
        return mark_safe(
            '<div class="input-append">%s</div>' %
            output)