from django import template
from datetime import date, timedelta
from digital.models import PartImage, Part
from django.core import serializers
import json
import random
from copy import copy
import types
from django.conf import settings

register = template.Library()


@register.filter(name='days_from_date')
def days_from_date(value):
    delta = value.date() - date.today()

    if delta.days == 0:
        return "Today!"
    elif delta.days < 1:
        return "%s %s ago" % (abs(delta.days),
            ("day" if abs(delta.days) == 1 else "days"))
    elif delta.days == 1:
        return "Tomorrow"
    elif delta.days > 1:
        return "In %s days" % delta.days


def silence_without_field(fn):
    def wrapped(field, attr):
        if not field:
            return ""
        return fn(field, attr)
    return wrapped



@register.filter(name='get_due_date_string')
def get_due_date_string(value):
    delta = value.date() - date.today()

    if delta.days == 0:
        return "Today!"
    elif delta.days < 1:
        return "%s %s ago!" % (abs(delta.days),
            ("day" if abs(delta.days) == 1 else "days"))
    elif delta.days == 1:
        return "Tomorrow"
    elif delta.days > 1:
        return "In %s days" % delta.days

@register.filter(name='seconds_to_duration')
def seconds_to_duration(value):
    hours = value//3600
    minutes = (value % 3600)//60
    print "MINUTE: %s"%minutes

    return "%s h %s m"%(hours, minutes)

@register.filter(name='created_recently')
def created_recently(value):
    delta = value.date() - date.today()
    if delta.days > -2:
        return "list-group-item-success"
    else:
        return ""

@register.filter(name='extension_gcode')
def extension_gcode(value):
    extension = value.rsplit(".",1)[1].lower()
    if extension == "gcode":
        return True
    else:
        return False

@register.filter(name='model_to_dict')
def model_to_dict(instance, user):
    currency_rate = user.currency.rate
    f_card = instance.financial_card
    if f_card:
        try:
            f_card.cost_saving_5y *= currency_rate
            f_card.cost_saving_5y = round(f_card.cost_saving_5y,2)
        except:
            None
        try:
            f_card.former_production_cost *= currency_rate
            f_card.former_production_cost = round(f_card.former_production_cost,2)
        except:
            None
        try:
            f_card.former_tco *= currency_rate
            f_card.former_tco = round(f_card.former_tco,2)
        except:
            None
        try:
            f_card.selling_price *= currency_rate
            f_card.selling_price = round(f_card.selling_price,2)
        except:
            None
        try:
            f_card.selling_repriced *= currency_rate
            f_card.selling_repriced = round(f_card.selling_repriced,2)
        except:
            None
        try:
            f_card.sp3d_selling_price *= currency_rate
            f_card.sp3d_selling_price = round(f_card.sp3d_selling_price,2)
        except:
            None
        
    dic = serializers.serialize("json", [instance],  use_natural_foreign_keys=True)[1:-1]
    # print dic['fields']
    # if 'financial_card' in dic['fields'] and dic['fields']['financial_card']:
    #     f_card = dic['fields']['financial_card']
    #     f_card['cost_saving_5y'] = 10
    
    return dic
    
def Convert(instance, rate):
    print instance
    instance = 50
    print instance
    
        
@register.filter(name='url_list')
def url_list(image_instance_list):
    url_list=[]
    for image in image_instance_list:
        if image.image.url:
            url_list.append(image.image.url)
    return json.dumps(url_list)
    
@register.filter(name='equals')
def isequal(field, attr):
    return str(field) == str(attr) 

@register.filter(name='dict_list')
def dict_list(file_instance_list):
    dict_list=[]
    for file in file_instance_list:
        dict_list.append(file.natural_key())
    return json.dumps(dict_list)

@register.simple_tag
def random_int():
    return random.randint(1, 5000)

@register.simple_tag
def debug():
    return settings.DEBUG
    
# settings value
@register.simple_tag
def database_name():
    print "YESAII"
    return settings.DATABASES['default']['NAME']

def _process_field_attributes(field, attr, process):

    # split attribute name and value from 'attr:value' string
    params = attr.split(':', 1)
    attribute = params[0]
    value = params[1] if len(params) == 2 else ''

    field = copy(field)

    # decorate field.as_widget method with updated attributes
    old_as_widget = field.as_widget

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        attrs = attrs or {}
        process(widget or self.field.widget, attrs, attribute, value)
        html = old_as_widget(widget, attrs, only_initial)
        self.as_widget = old_as_widget
        return html

    field.as_widget = types.MethodType(as_widget, field)
    return field

@register.filter("append_attr")
@silence_without_field
def append_attr(field, attr):
    def process(widget, attrs, attribute, value):
        if attrs.get(attribute):
            attrs[attribute] += ' ' + value
        elif widget.attrs.get(attribute):
            attrs[attribute] = widget.attrs[attribute] + ' ' + value
        else:
            attrs[attribute] = value
    return _process_field_attributes(field, attr, process)

@register.filter("add_class")
@silence_without_field
def add_class(field, css_class):
    return append_attr(field, 'class:' + css_class)

@register.filter("attr")
@silence_without_field
def set_attr(field, attr):

    def process(widget, attrs, attribute, value):
        attrs[attribute] = value

    return _process_field_attributes(field, attr, process)
    
@register.filter('startswith')
def startswith(text, starts):
    if isinstance(text, basestring):
        return text.startswith(starts)
    return False
    
@register.filter('convert_rate')
def convert_rate(value, user):
    try:
        return "%s"%int(value*user.currency.rate)
    except:
        return ""
        
@register.filter('input_convert_rate')
def input_convert_rate(_input, user):
    
    
    return _input
        
@register.filter('add_currency')
def add_currency(value, user):
    if value:
        return "%s %s"%(value,user.currency.sign)
    else:
        return ""
    
