# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from sp3d_quotation.storage_backends import PrivateMediaStorage

class Client(models.Model):

    creation_date = models.DateTimeField('date published')
    first_name = models.CharField(max_length=200, default = '')
    last_name = models.CharField(max_length=200, default = '')
    email = models.CharField(max_length=200, default = '')
    last_session_key = models.CharField(max_length=200, default = '')
    address= models.CharField(max_length=200, default = '')


    def __str__(self):
        return "Client id " + str(self.id)

class Quote(models.Model):

    creation_date = models.DateTimeField('date published')
    id_client = models.IntegerField(default=0)
    list_models3d_quantity = models.CharField(max_length=200, default = '')
    value = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    currency = models.CharField(max_length=20, default = '')
    last_session_key = models.CharField(max_length=200, default = '')

    def __str__(self):
        return "Quote id " + str(self.id)

class Model3D(models.Model):

    creation_date = models.DateTimeField(auto_now_add=True)
    id_technology = models.IntegerField(default=0)
    id_material = models.IntegerField(default=0)
    color = models.CharField(max_length=20, default = '')
    dimensions = models.CharField(max_length=20, default = '')
    file = models.FileField(storage = PrivateMediaStorage(), upload_to = 'models_3d/', blank=True)
    file_path = models.CharField(max_length=200, default = '')
    file_name = models.CharField(max_length=200, default = '')

    def __str__(self):
        return "Model3D id " + str(self.id)    

class Technology(models.Model):
    name = models.CharField(max_length=200, default = '')
    url_name = models.CharField(max_length=200, default = '')
    file_name = models.CharField(max_length=200, default = '')
    priority = models.IntegerField(default=0)
    tag_title = models.CharField(max_length=200, default = '')
    tag_description = models.CharField(max_length=200, default = '') 
    def __str__(self):
        return "YAML id " + str(self.id)

class Material(models.Model):

    name = models.CharField(max_length=200, default = '')
    color_list = models.CharField(max_length=200, default = '')
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    currency = models.CharField(max_length=20, default = '')

    def __str__(self):
        return "Material id " + str(self.id)

class Bulk_Files(models.Model):

    creation_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(storage = PrivateMediaStorage(), upload_to = 'bulk_files/')
    def __str__(self):
        return "Bulk File id " + str(self.id)

class Quote_Form(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    id_bulk_files = models.CharField(max_length=200, default = '')
    quantity = models.IntegerField(default=1)
    email = models.CharField(max_length=200, default = '')
    contact = models.CharField(max_length=200, default = '')
    process = models.CharField(max_length=200, default = '')
    service = models.CharField(max_length=200, default = '')
    request_type = models.CharField(max_length=200, default = '')
    timeline = models.CharField(max_length=100, default = '')
    details = models.CharField(max_length=500, default = '')
    def __str__(self):
        return "Quote Form id " + str(self.id)
