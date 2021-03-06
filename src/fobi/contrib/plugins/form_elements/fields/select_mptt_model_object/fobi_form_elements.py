__title__ = 'fobi.contrib.plugins.form_elements.fields.select_mptt_model_object.fobi_form_elements'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = 'Copyright (c) 2014-2015 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('SelectMPTTModelObjectInputPlugin',)

from django.db import models
from django.forms.widgets import Select
from django.utils.translation import ugettext_lazy as _

from mptt.fields import TreeNodeChoiceField

from fobi.base import FormFieldPlugin, form_element_plugin_registry, get_theme
from fobi.constants import (
    SUBMIT_VALUE_AS_VAL, SUBMIT_VALUE_AS_REPR
    )
from fobi.helpers import safe_text, get_app_label_and_model_name

from nine.versions import DJANGO_GTE_1_7

if DJANGO_GTE_1_7:
    from django.apps import apps
    get_model = apps.get_model
else:
    from django.db.models import get_model

from . import UID
from .forms import SelectMPTTModelObjectInputForm
from .settings import SUBMIT_VALUE_AS

theme = get_theme(request=None, as_instance=True)

class SelectMPTTModelObjectInputPlugin(FormFieldPlugin):
    """
    Select MPTT model object field plugin.
    """
    uid = UID
    name = _("Select MPTT model object")
    group = _("Fields")
    form = SelectMPTTModelObjectInputForm

    def get_form_field_instances(self, request=None):
        """
        Get form field instances.
        """
        app_label, model_name = get_app_label_and_model_name(self.data.model)
        model = get_model(app_label, model_name)
        queryset = model._default_manager.all()

        kwargs = {
            'label': self.data.label,
            'help_text': self.data.help_text,
            'initial': self.data.initial,
            'required': self.data.required,
            'queryset': queryset,
            'widget': Select(attrs={'class': theme.form_element_html_class}),
        }

        return [(self.data.name, TreeNodeChoiceField, kwargs)]

    def submit_plugin_form_data(self, form_entry, request, form):
        """
        Submit plugin form data/process.

        :param fobi.models.FormEntry form_entry: Instance of
            ``fobi.models.FormEntry``.
        :param django.http.HttpRequest request:
        :param django.forms.Form form:
        """
        # In case if we should submit value as is, we don't return anything.
        # In other cases, we proceed further.

        # Get the object
        obj = form.cleaned_data.get(self.data.name, None)
        if obj:
            value = None
            # Should be returned as repr
            if SUBMIT_VALUE_AS == SUBMIT_VALUE_AS_REPR:
                value = safe_text(obj)
            elif SUBMIT_VALUE_AS == SUBMIT_VALUE_AS_VAL:
                value = '{0}.{1}.{2}'.format(
                    obj._meta.app_label,
                    obj._meta.module_name,
                    obj.pk
                    )
            else:
                # Handle the submitted form value
                value = '{0}.{1}.{2}.{3}'.format(
                    obj._meta.app_label,
                    obj._meta.module_name,
                    obj.pk,
                    safe_text(obj)
                    )

            # Overwrite ``cleaned_data`` of the ``form`` with object qualifier.
            form.cleaned_data[self.data.name] = value

        # It's critically important to return the ``form`` with updated
        # ``cleaned_data``
        return form


form_element_plugin_registry.register(SelectMPTTModelObjectInputPlugin)
