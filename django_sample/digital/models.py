# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from sp3d.storage_backends import PrivateMediaStorage
from django.db.models.signals import pre_delete, post_save
from django.dispatch.dispatcher import receiver
from django.conf import settings
from django.core import serializers
from storages.backends.s3boto3 import S3Boto3StorageFile
from datetime import datetime
from users.models import Organisation, CustomUser
from ast import literal_eval

# Create your models here.
class UserPartFilters(models.Model):
    PRINTABLE_CHOICES = (('ALL', "All"), ('IDENTIFIED', 'Identified'), ('PRINTABLE', 'Printable'))
    ANALYSIS_CHOICES = (('ALL', 'All times'), ('LAST', 'Last Analysis'))
    REORDER_YEAR_CHOICES = (('1', 'year 1'), ('2', 'year 2'), ('3', 'year 3'), ('4', 'year 4'), ('5', 'year 5'))
    user = models.OneToOneField('users.CustomUser', null=True, blank=True, on_delete=models.CASCADE, related_name='part_filters')
    printable = models.CharField(max_length=20, choices=PRINTABLE_CHOICES, default="ALL")
    analysis = models.CharField(max_length=20, choices=ANALYSIS_CHOICES, default="ALL")
    obsolete = models.BooleanField("Obsolete Parts", default = False)
    longtail = models.BooleanField("Longtail Parts",default=False)
    shortage = models.BooleanField("Shortage Parts",default=False)
    pex = models.BooleanField("PEX Parts",default=False)
    viable = models.BooleanField("Financially viable",default=False)
    appliance_list = models.TextField("Appliance Type List", default='', blank=True)
    parttype_list = models.TextField("Part Type List", default='', blank=True)
    technology_list = models.TextField("Technology List", default='', blank=True)
    material_list = models.TextField("Material List", default='', blank=True)
    reorder = models.CharField(max_length=100, default="", blank=True)
    sort = models.CharField(max_length=100, default="", blank=True)

    def __str__(self):
        return "Part Filters %s" % (self.id,)
    def getPrintableChoiceList(self):
        return self.PRINTABLE_CHOICES
    def getAnalysisChoiceList(self):
        return self.ANALYSIS_CHOICES
    def getReorderYearChoiceList(self):
        return self.REORDER_YEAR_CHOICES

    def reset(self):
        self.printable = 'ALL'
        self.analysis = 'ALL'
        self.obsolete = False
        self.longtail = False
        self.shortage = False
        self.pex = False
        self.viable = False
        self.appliance_list = ''
        self.parttype_list = ''
        self.technology_list = ''
        self.material_list = ''
        self.reorder = ''
        self.sort = ''

    def isOn(self):
        if self.printable != "ALL": return True
        if self.analysis != "ALL": return True
        if self.obsolete : return True
        if self.longtail: return True
        if self.shortage: return True
        if self.pex: return True
        if self.viable: return True
        print self.reorder
        if self.reorder:
            if literal_eval(self.reorder): return True

        if self.appliance_list:
            appliance_families = list(ApplianceFamily.objects.filter(industry__in = self.user.organisation.industry.all()).order_by('name').values_list("id",flat=True)) + [None]
            if set(literal_eval(self.appliance_list)) != set(appliance_families): return True

        if self.parttype_list:
            part_types = list(PartType.objects.filter(appliance_family__industry__in = self.user.organisation.industry.all()).order_by('name').values_list("name", flat=True).distinct()) + [None]
            if set(literal_eval(self.parttype_list)) != set(part_types): return True

        return False

# create or update and attach this filter card when CustomUser is created
@receiver(post_save, sender=CustomUser)
def create_or_update_part_filters(sender, instance, created, **kwargs):
    if not hasattr(instance, 'part_filters'):
        UserPartFilters.objects.create(user=instance)
    instance.part_filters.save()

# Create your models here.
class UserPartColumns(models.Model):
    user = models.OneToOneField('users.CustomUser', null=True, blank=True, on_delete=models.CASCADE, related_name='part_columns')
    stock = models.BooleanField("Stock", default = False)
    selling_price = models.BooleanField("Original Selling Price", default = False)
    selling_repriced = models.BooleanField("Repriced Selling Price", default = False)
    selling_volumes = models.BooleanField("Yearly Selling Volumes", default = False)
    former_production_cost = models.BooleanField("Former Production Cost", default = False)
    production_cost = models.BooleanField("SP3D Production Cost", default = False)
    former_moq = models.BooleanField("Former MOQ", default = False)
    former_tco = models.BooleanField("Former TCO", default = False)
    sp3d_selling_price = models.BooleanField("SP3D Selling Price", default = False)
    cost_saving_5y = models.BooleanField("Cost saving 5 year", default = False)
    cost_saving_shortage = models.BooleanField("Cost saving Shortage", default = False)
    cost_saving_pex = models.BooleanField("Cost saving Pex", default = False)

    def __str__(self):
        return "Part Columns Choice %s" % (self.id,)

# create or update and attach this filter card when CustomUser is created
@receiver(post_save, sender=CustomUser)
def create_or_update_part_columns(sender, instance, created, **kwargs):
    if not hasattr(instance, 'part_columns'):
        UserPartColumns.objects.create(user=instance)
    instance.part_columns.save()

# Create your models here.
class FinancialSettings(models.Model):
    organisation = models.OneToOneField('users.Organisation', null=True, blank=True, on_delete=models.CASCADE, related_name='financial_settings')
    cost_plus_ratio = models.FloatField("Percentage of Cost to find cost+", default=0.3)
    client_margin = models.FloatField("Client Margin", default=0.4)
    appliance_repricing_maxvalue_ratio = models.FloatField("Percentage Value of Appliance as a max repricing", default = 0.05)
    repricing_new_max_ratio = models.FloatField("Ratio to set new maximum betwwn cost+and max on repricing", default = 0.5)
    yearly_stock_price_ratio = models.FloatField("Ratio of stock price per year", default = 0.2)
    yearly_selling_decrease_ratio = models.FloatField("Yearly Selling Decrease Ratio", default = 0.1)
    repricing = models.BooleanField("Repricing Authorized", default = True)
    show_financial = models.BooleanField("Show Financial Cards", default = True)
    avg_shortage_duration = models.FloatField("Average Shortage Duration (in months)", default = 3)
    shortage_volume_loss_ratio = models.FloatField("loss ratio of customers during the shortage", default = 0.2)

    def __str__(self):
        return "Financial settings %s" % (self.id,)

# create or update and attach this settings card when Organisation is created
@receiver(post_save, sender=Organisation)
def create_or_update_financial_settings(sender, instance, created, **kwargs):
    if not hasattr(instance, 'financial_settings'):
        FinancialSettings.objects.create(organisation=instance)
    instance.financial_settings.save()

class FinancialCard(models.Model):
    # part = models.OneToOneField('digital.Part', null=True, blank=True, on_delete=models.CASCADE, related_name='financial_card')
    stock = models.IntegerField(default=0)
    selling_price = models.FloatField("Selling price (in US$)", null = True, blank=True)
    selling_repriced = models.FloatField("Repriced selling price (in US$)", null = True, blank=True)
    selling_volumes = models.IntegerField("Yearly Selling Volumes", null=True, blank=True)
    shortage_volumes = models.IntegerField("Shortage Volumes", null=True, blank=True)
    pex_volumes = models.IntegerField("PEX Volumes", null=True, blank=True)
    former_production_cost = models.FloatField("Former Production Cost (in US$)", null=True, blank=True)
    production_cost = models.FloatField("SP3D production cost (in US$)", default = 0.0)
    former_moq = models.IntegerField("Former Minimum Quantity Order", null=True, blank=True)
    former_tco = models.FloatField("Former Total Cost Overall ($US)", null=True, blank=True)
    sp3d_selling_price = models.FloatField("SP3D Selling price to OEM (US$)", null=True, blank=True)
    cost_saving_5y = models.FloatField("cost savings on 5 years", default = 0)
    cost_saving_pex = models.FloatField("Pex Cost Saving", default = 0)
    cost_saving_shortage = models.FloatField("Shortage Cost Saving", default = 0)
    positive_obsolete_analysis = models.BooleanField("Obsolete Analysis positive", default=False)
    positive_longtail_analysis = models.BooleanField("Long Tail Analysis positive", default=False)
    positive_pex_analysis = models.BooleanField("PEX Analysis positive", default=False)
    positive_shortage_analysis = models.BooleanField("Shortage Analysis positive", default=False)
    year_restocking = models.IntegerField("Year need restocking", null=True, blank=True)

    def __str__(self):
        return "Financial card %s" % (self.id,)
    def reset(self):
        self.selling_repriced = None
        self.production_cost = 0
        self.sp3d_selling_price = None
        self.cost_saving_5y = 0
        self.positive_obsolete_analysis = False
        self.positive_longtail_analysis = False
        self.year_restocking = None
        self.former_tco = None
        return self.save()

    def natural_key(self):
        return {
            'id':self.id,
            'stock':self.stock,
            'selling_price':self.selling_price,
            'selling_repriced':self.selling_repriced,
            'selling_volumes':self.selling_volumes,
            'shortage_volumes':self.shortage_volumes,
            'pex_volumes':self.pex_volumes,
            'former_production_cost':self.former_production_cost,
            'former_moq':self.former_moq,
            'former_tco':self.former_tco,
            'sp3d_selling_price':self.sp3d_selling_price,
            'cost_saving_5y':self.cost_saving_5y,
            'positive_obsolete_analysis':self.positive_obsolete_analysis,
            'positive_longtail_analysis':self.positive_longtail_analysis,
            'positive_shortage_analysis':self.positive_shortage_analysis,
            'positive_pex_analysis':self.positive_pex_analysis,
            'cost_saving_shortage':self.cost_saving_shortage,
            'cost_saving_pex':self.cost_saving_pex,
            'year_restocking':self.year_restocking,
            }

# save opposite one to one key
# @receiver(post_save, sender = FinancialCard)
# def save_reverse_onetoone_financialcard(sender, created, instance, **kwargs):
#     if instance.part:
#         instance.part.financial_card = instance
#         instance.part.save()

class Characteristics(models.Model):
    COLOR_CHOICES = (("NA", "n/a"),("GREEN", "Green"),("WHITE", "White"),("BLACK", "Black"), ("GREY", "Grey"), ("SILVER", "Silver"))
    FLAME_RETARDANT_CHOICES = (("NA", "n/a"),("HB", "HB"),("V0", "V0"),("V1", "V1"),("V2", "V2"))
    TEMPERATURE_UNIT_CHOICES = (("°C", "°C"),("°F", "°F"))
    part = models.OneToOneField('digital.Part', null=True, blank=True, on_delete=models.CASCADE, related_name='part_characteristics')
    part_type = models.OneToOneField('PartType', on_delete=models.CASCADE, null=True, blank=True, related_name = 'part_type_characteristics')
    technology = models.OneToOneField('jb.Technology', on_delete=models.CASCADE, null=True, blank=True, related_name = 'technology_characteristics')
    material = models.OneToOneField('jb.Material', on_delete=models.CASCADE, null=True, blank=True, related_name = 'material_characteristics')
    techno_material = models.OneToOneField('jb.CoupleTechnoMaterial', on_delete=models.CASCADE, null=True, blank=True, related_name = 'techno_material_characteristics')

    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default="NA")
    is_visual = models.BooleanField("Visual part", default=False, blank=True)
    is_transparent = models.BooleanField("Transparent", default=False, blank=True)
    is_rubbery = models.BooleanField("Rubbery Like", default=False, blank=True)
    is_water_resistant = models.BooleanField("Water Resistant", default=False, blank=True)
    is_chemical_resistant = models.BooleanField("Chemical Resistant", default=False, blank=True)
    is_flame_retardant = models.BooleanField("Flame Retardant", default=False, blank=True)
    is_food_grade = models.BooleanField("Food Grade", default=False, blank=True)
    flame_retardancy =  models.CharField(max_length=10, choices=FLAME_RETARDANT_CHOICES, default="NA")
    min_temp =  models.IntegerField("Minimum Operating Temperature", null=True, blank=True)
    max_temp =  models.IntegerField("Maximum Operating Temperature", null=True, blank=True)
    temp_unit = models.CharField(max_length=5, choices=TEMPERATURE_UNIT_CHOICES, default="°C")

    density = models.FloatField(max_length=10, null=True, blank=True)
    tensile = models.IntegerField(max_length=10, null=True, blank=True)
    elongation = models.IntegerField(max_length=10, null=True, blank=True)
    surface_roughness = models.IntegerField(max_length=10, null=True, blank=True)
    dim_accuracy = models.IntegerField(max_length=10, null=True, blank=True)
    hardness = models.IntegerField(max_length=10, null=True, blank=True)
    impact_resist_charpy = models.IntegerField(max_length=10, null=True, blank=True)
    fatigue = models.IntegerField(max_length=10, null=True, blank=True)
    corrosion = models.FloatField(max_length=10, null=True, blank=True)
    max_service_temp = models.IntegerField(max_length=10, null=True, blank=True)
    machinability = models.IntegerField(max_length=10, null=True, blank=True)


    def __str__(self):
        return "Characteristics card %s" % (self.id,)

    def natural_key(self):
        return {
            'color':self.color,
            'is_visual':self.is_visual,
            'is_transparent':self.is_transparent,
            'is_rubbery':self.is_rubbery,
            'is_water_resistant':self.is_water_resistant,
            'is_chemical_resistant':self.is_chemical_resistant,
            'is_flame_retardant':self.is_flame_retardant,
            'is_food_grade':self.is_food_grade,
            'flame_retardancy':self.flame_retardancy,
            'min_temp':self.min_temp,
            'max_temp':self.max_temp,
            'temp_unit':self.temp_unit,
            'density':self.density,
            'tensile':self.tensile,
            'elongation':self.elongation,
            'surface_roughness':self.surface_roughness,
            'dim_accuracy':self.dim_accuracy,
            'hardness':self.hardness,
            'impact_resist_charpy':self.impact_resist_charpy,
            'fatigue':self.fatigue,
            'corrosion':self.corrosion,
            'max_service_temp':self.max_service_temp,
            'machinability':self.machinability,
            }
    
    def get_retardant_choice(self, string):
        error = ''
        choices = [choice[0] for choice in self.FLAME_RETARDANT_CHOICES]
        if string.upper() in choices:
            return error, string.upper()
        else:
            error = 'Wrong Retardancy Level: %s. Instead, assigned HB'%string
            return error, "HB"

# save opposite one to one key
@receiver(post_save, sender=Characteristics)
def save_reverse_onetoones(sender, created, instance, **kwargs):
    if instance.part:
        instance.part.characteristics = instance
        instance.part.save()
    elif instance.material:
        instance.material.characteristics = instance
        instance.material.save()
    elif instance.part_type:
        instance.part_type.characteristics = instance
        instance.part_type.save()
    elif instance.technology:
        instance.technology.characteristics = instance
        instance.technology.save()
    elif instance.techno_material:
        instance.techno_material.characteristics = instance
        instance.techno_material.save()

class PartType(models.Model):
    name = models.CharField(max_length=100, default = '')
    appliance_family = models.ForeignKey('ApplianceFamily', on_delete=models.SET_NULL, verbose_name="Appliance Family", null=True)
    keywords = models.CharField(max_length=200, default = '', blank=True)
    blacklist = models.CharField(max_length=600, default = '', blank=True)
    characteristics = models.OneToOneField('Characteristics', on_delete=models.SET_NULL, null=True, blank=True, related_name = 'part_type_characteristics')

    def __str__(self):
        return "%s - %s" % (self.name,self.appliance_family.name)

    def natural_key(self):
        return {'id':self.id,'name':self.name}
    class Meta:
        unique_together = (('name', 'appliance_family'),)

class ApplianceFamily(models.Model):
    name = models.CharField(max_length=100, default = '', unique = True)
    industry = models.ForeignKey('users.Industry', on_delete=models.SET_DEFAULT, default=1)
    retail_price = models.FloatField('Average Retail Price (US$)', default=0.0)
    organisation_details = models.ManyToManyField('users.Organisation', through = 'ApplianceFamilyDetails')

    def __str__(self):
        return "%s" % (self.name,)

    def natural_key(self):
        return {'name':self.name, 'industry':self.industry.name}


class ApplianceFamilyDetails(models.Model):
    appliance_family = models.ForeignKey('ApplianceFamily', on_delete=models.CASCADE)
    organisation = models.ForeignKey('users.Organisation', on_delete=models.CASCADE, related_name="ApplianceFamilyDetails")
    retail_price = models.FloatField('Average Retail Price (US$)', default=300)
    replacement_cost = models.FloatField('Replacement Cost (US$)', default = 300)

    class Meta:
        unique_together = (('appliance_family', 'organisation'),)

    def __str__(self):
        return "%s" % (self.id,)

    def natural_key(self):
        return {'name':self.id}


class Catalogue(models.Model):
    name = models.CharField(max_length=200, null=True)
    organisation = models.ForeignKey('users.Organisation', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "%s" % self.name

    def natural_key(self):
        return {'id':self.id, 'name':self.name}

    class Meta:
        unique_together = (('name', 'organisation'),)



class Appliance(models.Model):
    name = models.CharField(max_length=200, null=True)
    reference = models.CharField(max_length=200, default='', unique = True)
    organisation = models.ForeignKey('users.Organisation', on_delete=models.SET_NULL, null=True)
    family = models.ForeignKey('ApplianceFamily', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "%s - %s" % (self.family.name, self.reference)

    def natural_key(self):
        return {'id':self.id, 'name':self.name, 'reference':self.reference, 'family':self.family.name}

    class Meta:
        unique_together = (('name', 'reference','family'),)



class ClientPartStatus(models.Model):
    name = models.CharField(max_length=50, default = '', unique=True)

    def __str__(self):
        return "%s" % (self.name,)

    def natural_key(self):
        return {'id':self.id,'name':self.name}

class PartEvent(models.Model):
    EVENT_TYPE_CHOICES = (
        ("INFO", "info"),
        ("REQUEST", "request"),
        ("STATUS_CHANGE", "status change"),
    )
    date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True)
    part = models.ForeignKey('Part', on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default="INFO")
    status = models.ForeignKey('ClientPartStatus', on_delete=models.SET_NULL, null=True)
    short_description = models.CharField(max_length=100, default = '')
    long_description = models.TextField(default = '')

    def __str__(self):
        return "%s" % (self.short_description,)

    def natural_key(self):
        return {'id':self.id, 'type':type, 'short_description':short_description}



class Part(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True)
    reference = models.CharField(max_length=300, null = True)
    name = models.CharField(max_length=400, default = '')
    description = models.CharField(max_length=400, default = '')
    type = models.ForeignKey('PartType', on_delete=models.SET_NULL, null=True, blank=True)
    characteristics = models.OneToOneField('Characteristics', null=True, blank=True, on_delete = models.SET_NULL, related_name='part_characteristics')
    financial_card = models.OneToOneField('FinancialCard', null=True, blank=True, on_delete = models.SET_NULL, related_name='part')
    organisation = models.ForeignKey('users.Organisation', on_delete=models.SET_NULL, null=True)
    appliance = models.ManyToManyField(Appliance, blank=True)
    material = models.ForeignKey('jb.Material', on_delete=models.SET_NULL, null=True, blank=True)
    length = models.FloatField(max_length=10, null=True, blank=True)
    width = models.FloatField(max_length=10, null=True, blank=True)
    height = models.FloatField(max_length=10, null=True, blank=True)
    weight = models.FloatField(max_length=10, null=True, blank=True)
    dimension_unit = models.CharField(max_length=5, default="mm", choices=[('mm','mm'), ('inch','inch')])
    weight_unit = models.CharField(max_length=5, default='gr', choices=[('gr','gr')])
    status = models.ForeignKey('ClientPartStatus', on_delete=models.SET_DEFAULT, default=1)
    final_card = models.OneToOneField('jb.FinalCard', on_delete=models.SET_NULL, null=True, blank=True, related_name = 'part')
    notify_status_to_client = models.BooleanField("Notify Part Status to Client", default=False, blank=True)
    bulk_upload = models.ForeignKey('BulkPartUpload', on_delete=models.SET_NULL, null=True, blank=True)
    catalogue = models.ForeignKey('Catalogue', on_delete=models.CASCADE, null=True)

    def __unicode__(self):
        return "%s" % (self.name,)

    class Meta:
        unique_together = (('reference', 'organisation'),)

    def save(self,  *args, **kwargs):
        # if no characteristics, remove final card and reset financial analysis
        if not self.characteristics:
            if self.final_card:
                self.final_card.delete()
                self.final_card = None
            if self.financial_card:
                self.financial_card.reset()
        super(Part, self).save(*args, **kwargs)

def get_bulkpartupload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    date = datetime.now().strftime("%Y%m%d-%H%M%S")
    return '{0}/bulk-uploads/upload-{1}.csv'.format(instance.created_by.organisation.name, date)

class BulkPartUpload(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True)
    file = models.FileField(storage = PrivateMediaStorage(bucket='sp3d-clients'), upload_to = get_bulkpartupload_path, blank=True)
    errors = models.TextField(null=True, blank=True)
    warnings = models.TextField(null=True, blank=True)
    finished = models.BooleanField(default = False)
    finished_entries = models.IntegerField(default=0)
    def __str__(self):
        return "Bulk Upload %s" % (self.id, )

    def natural_key(self):
        return self.file.url


def get_analysisexport_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    date = datetime.now().strftime("%Y%m%d-%H%M%S")
    return '{0}/analysis-exports/export-{1}.csv'.format(instance.created_by.organisation.name, date)

class AnalysisExport(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True)
    bulk_upload = models.ForeignKey('BulkPartUpload', on_delete=models.SET_NULL, null=True)
    catalogue = models.ForeignKey('Catalogue', on_delete=models.SET_NULL, null=True)
    file = models.FileField(storage = PrivateMediaStorage(bucket='sp3d-clients'), upload_to = get_analysisexport_path, blank=True)
    def __str__(self):
        return "%s" % (self.id, self.file.url)

    def natural_key(self):
        return self.file.url


def get_image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return '{0}/parts/{1}/images/{2}'.format(instance.part.organisation.name, instance.part.reference, filename)

class PartImage(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True)
    part = models.ForeignKey('Part', on_delete=models.CASCADE, null=True)
    image = models.ImageField(storage = PrivateMediaStorage(bucket='sp3d-clients'), upload_to = get_image_path, blank=True)
    thumbnail = models.ImageField(storage = PrivateMediaStorage(bucket='sp3d-clients'), upload_to = get_image_path, blank=True, null=True)

    def create_thumbnail(self):
        # original code for this method came from
        # http://snipt.net/danfreak/generate-thumbnails-in-django-with-pil/

        # If there is no image associated with this.
        # do not create thumbnail
        if not self.image:
            return

        # if the image is not a new image, but is already a S3 file, do not create thumbnail
        if isinstance(self.image.file, S3Boto3StorageFile):
            return

        from PIL import Image
        from cStringIO import StringIO
        from django.core.files.uploadedfile import SimpleUploadedFile
        import os

        # Set our max thumbnail size in a tuple (max width, max height)
        THUMBNAIL_SIZE = (200, 200)

        DJANGO_TYPE = self.image.file.content_type

        if DJANGO_TYPE == 'image/jpeg':
            PIL_TYPE = 'jpeg'
            FILE_EXTENSION = 'jpg'
        elif DJANGO_TYPE == 'image/png':
            PIL_TYPE = 'png'
            FILE_EXTENSION = 'png'

        # Open original photo which we want to thumbnail using PIL's Image
        image = Image.open(StringIO(self.image.read()))

        # We use our PIL Image object to create the thumbnail, which already
        # has a thumbnail() convenience method that contrains proportions.
        # Additionally, we use Image.ANTIALIAS to make the image look better.
        # Without antialiasing the image pattern artifacts may result.
        image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

        # Save the thumbnail
        temp_handle = StringIO()
        image.save(temp_handle, PIL_TYPE)
        temp_handle.seek(0)

        # Save image to a SimpleUploadedFile which can be saved into
        # ImageField
        suf = SimpleUploadedFile(os.path.split(self.image.name)[-1],
                temp_handle.read(), content_type=DJANGO_TYPE)
        # Save SimpleUploadedFile into image field
        self.thumbnail.save(
            '%s_thumbnail.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
            suf,
            save=False
        )

    def save(self, *args, **kwargs):
        self.create_thumbnail()
        force_update = False
        # If the instance already has been saved, it has an id and we set
        # force_update to True
        if self.id:
            force_update = True
        # Force an UPDATE SQL query if we're editing the image to avoid integrity exception
        super(PartImage, self).save(force_update=force_update)

    def __str__(self):
        return "%s" % (self.image.name,)

    def natural_key(self):
        return self.image.url

# delete image file on bucket on delete instance if not in  production:
@receiver(pre_delete, sender=PartImage)
def partimage_delete(sender, instance, **kwargs):
    if settings.DEBUG:
        # Pass false so FileField doesn't save the model.
        instance.image.delete(False)
        instance.thumbnail.delete(False)


def get_bulk_path(instance, filename):
    path = '{0}/parts/{1}/'.format(instance.part.organisation.name, instance.part.reference)
    if instance.type == "BULK":
        path = path + 'bulk_files/{0}'.format(filename)
    elif instance.type == "MATERIAL":
        path = path + 'bulk_files/{0}'.format(filename)
    elif instance.type == "2D":
        path = path + '2d_files/{0}'.format(filename)
    elif instance.type == "3D" or instance.type == "STL":
        path = path + '3d_files/{0}'.format(filename)
    else:
        path = path + '{0}'.format(filename)
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return path

class PartBulkFile(models.Model):
    FILE_TYPE_CHOICES = (
        ("BULK", "bulk files"),
        ("MATERIAL", "material files"),
        ("3D", "3d model"),
        ("2D", "2d drawings"),
        ("STL", "STL file"),
    )
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True)
    part = models.ForeignKey('Part', on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default="BULK")
    file = models.FileField(storage = PrivateMediaStorage(bucket='sp3d-clients'), upload_to = get_bulk_path, blank=True)
    data = models.CharField(max_length=1000, default = '')

    def __str__(self):
        return "%s" % (self.file.name,)

    def getTypeChoices(self):
        return self.FILE_TYPE_CHOICES

    def natural_key(self):
        return {"name":self.file.name.rsplit("/",1)[1], "url":self.file.url, 'id':self.id, 'type':self.type, 'data':self.data}

# delete image file on bucket on delete instance if not in  production:
@receiver(pre_delete, sender=PartBulkFile)
def partbulkfile_delete(sender, instance, **kwargs):
    if settings.DEBUG:
        # Pass false so FileField doesn't save the model.
        instance.file.delete(False)
