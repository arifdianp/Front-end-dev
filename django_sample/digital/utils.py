# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from digital.models import Part, PartImage, PartBulkFile
from digital.decorators import postpone
from django.db.models import FieldDoesNotExist
from django.core.exceptions import FieldError
from django.template.loader import get_template
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from digital.models import Part, PartImage, PartBulkFile, Characteristics, PartType, ApplianceFamily, BulkPartUpload, FinancialCard, AnalysisExport, UserPartFilters, Catalogue
from jb.models import CoupleTechnoMaterial, Technology, Material, FinalCard
from django.db.models import Case, IntegerField, FloatField, Sum, When, Q, F, Count, Max, Avg, Min, Variance, StdDev
from django.db import connection, transaction
from django.shortcuts import get_object_or_404
from django.core.files import File
import tempfile
from stl import mesh
import numpy
import os
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from digital.models import ClientPartStatus
import csv
from django.db.models import Q
import re, math
from collections import Counter
from os.path import join
from ast import literal_eval
from threading import Thread
import datetime
import operator
import random
from numpy.random import normal

dir_path = os.path.dirname(os.path.realpath(__file__))

DEFAULT_NB_PER_PAGE = 20
DEFAULT_PAGE_RANGE = 10

def getPartsClean(request):
    # FILTERS:
    filters_q, filters_dic = buildUserFilters(request.user)

    # add search in request
    search_string = request.GET.get('search', None)
    if search_string:
        filters_q  &= (Q(name__icontains=search_string) | Q(reference__icontains=search_string))


    # get right catalogue
    catalogue_id = request.GET.get('catalogue', None)
    try:
        catalogue = Catalogue.objects.get(organisation=request.user.organisation, id = catalogue_id)
        filters_dic['catalogue'] = catalogue
    except:
        None


    # get part sum up with filters without filter status applied
    parts_sumup, appliance_fam_distrib, parttype_distrib = getPartSumUp(filters_q, **filters_dic)

    # add status to filters
    id_status = request.GET.get('status', '')
    if id_status:
        try:
            status = ClientPartStatus.objects.get(id=id_status)
            filters_dic['status'] = status
        except:
            None

    # ADD SORTING ARGUMENT TO filters_dic
    sort = request.GET.get('sort', None)
    if request.user.part_filters:
        _filters = request.user.part_filters
    else:
        _filters = UserPartFilter.sobjects.create(user=request.user)

    if not sort is None:
        if sort == "":
            sort = 'date_created'
        else:
            if sort.startswith("-"):
                sort = "-financial_card__%s"%sort[1:]
            else:
                sort = "financial_card__%s"%sort

        if not sort == _filters.sort:
            _filters.sort = sort
            _filters.save()

    if not _filters.sort:
        _filters.sort = 'date_created'
        _filters.save()
    sort = _filters.sort

    try:
        Part.objects.all().values(sort.replace('-','')).first() #just as a test see if sort field exists
        all_parts = Part.objects.filter(filters_q, **filters_dic).order_by(sort)
    except (FieldDoesNotExist, FieldError):
        all_parts = Part.objects.filter(filters_q, **filters_dic).order_by('date_created')


    # PAGINATION
    page = request.GET.get('page', '')
    nb_per_page = request.GET.get('nb-per-page', '')
    if not page:
        page = 1
    if not nb_per_page:
        nb_per_page = DEFAULT_NB_PER_PAGE
    paginator = Paginator(all_parts, nb_per_page) #show nb_per_page elements per page
    try:
        parts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page = 1
        parts = paginator.page(page)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page = paginator.num_pages
        parts = paginator.page(page)

    first_pagination_number = (int(page)/DEFAULT_PAGE_RANGE)*DEFAULT_PAGE_RANGE + 1
    pagination_range=[]
    for i in range(DEFAULT_PAGE_RANGE):
        # print paginator.num_pages
        if first_pagination_number + i > paginator.num_pages:
            break
        pagination_range.append(first_pagination_number + i)



    # CONCATENATION
    parts_dict = dict([(part.id, part) for part in parts])

    # inject pictures directly in
    pictures = PartImage.objects.filter(part__in=parts)
    relation_dict = {}
    for pic in pictures:
        relation_dict.setdefault(pic.part.id, []).append(pic)
    for id, images in relation_dict.items():
        parts_dict[id].images = images


    # inject files directly in
    bulk_files = PartBulkFile.objects.filter(part__in=parts)
    relation_dict = {}
    for file in bulk_files:
        relation_dict.setdefault(file.part.id, []).append(file)
    for id, files in relation_dict.items():
        parts_dict[id].bulk_files = files


    return parts, page, pagination_range, nb_per_page, id_status, parts_sumup, appliance_fam_distrib, parttype_distrib





def buildUserFilters(user):
    filters_q = Q()
    filters_dic = {}
    # organisation filter
    filters_dic['organisation'] = user.organisation
    # check if user has custom filters, otherwise return
    if hasattr(user,'part_filters'):
        ft = user.part_filters
    else:
        return filters_q, filters_dic

    # printable filter
    if ft.printable == "IDENTIFIED":
        filters_dic['type__isnull'] = False
    elif ft.printable == "PRINTABLE":
        filters_dic['final_card__isnull'] = False
        filters_dic['final_card__techno_material__isnull'] = False

    # analysis filter:
    if ft.analysis == "LAST":
        latest_bulk_upload = BulkPartUpload.objects.filter(created_by__organisation = user.organisation).order_by('-date_created').first()
        if latest_bulk_upload:
            filters_dic['bulk_upload'] = latest_bulk_upload

    # obsolete and longtail
    query_or = Q()
    if ft.obsolete:
        query_or |= Q(financial_card__positive_obsolete_analysis = True)
    if ft.longtail:
        query_or |= Q(financial_card__positive_longtail_analysis = True)
    if ft.shortage:
        query_or |= Q(financial_card__positive_shortage_analysis = True)
    if ft.pex:
        query_or |= Q(financial_card__positive_pex_analysis = True)
    filters_q &= query_or

    # need reorder
    if ft.reorder:
        try:
            year_restocking = literal_eval(ft.reorder)
            query_or_1 = Q()
            for year in year_restocking:
                query_or_1 |= Q(financial_card__year_restocking = year)
            filters_q &= query_or_1
        except:
            None

    # appliance type filter
    if ft.appliance_list:
        try:
            appliance_list = literal_eval(ft.appliance_list)
            query_or_2 = Q(type__appliance_family__id__in = appliance_list)
            if None in appliance_list:
                query_or_2 |= Q(type__isnull = True)
            filters_q &= query_or_2
        except:
            None

    # part type filter
    if ft.parttype_list:
        try:
            parttype_list = literal_eval(ft.parttype_list)
            query_or_3 = Q(type__name__in = parttype_list)
            if None in parttype_list:
                query_or_3 |= Q(type__isnull = True)
            filters_q &= query_or_3
        except:
            None

    if ft.technology_list:
        try:
            technology_list = literal_eval(ft.technology_list)
            query_or_4 = Q(final_card__techno_material__technology__id__in = technology_list)
            if None in technology_list:
                query_or_4 |= Q(final_card__isnull = True)
            filters_q &= query_or_4
        except:
            None

    if ft.material_list:
        try:
            material_list = literal_eval(ft.material_list)
            query_or_5 = Q(final_card__techno_material__material__id__in = material_list)
            if None in material_list:
                query_or_5 |= Q(final_card__isnull = True)
            filters_q &= query_or_5
        except:
            None



    return filters_q, filters_dic





@postpone
def send_email(html_path, context, subject, from_email, to):
    html = get_template(html_path)
    html_content = html.render(context)
    msg = EmailMessage(subject, html_content, from_email, to=to)
    msg.content_subtype = 'html'
    msg.send()
    return True





def margin_yearly_analysis(request, decrease_rate = None, **kwargs):
    organisation = request.user.organisation
    currency_rate = request.user.currency.rate
    yearly_margin_list=[0]*5
    q0, q1, q2, q3, q4 = buildPartQueriesFromURLParams(request.GET)
    q5 = Q()
    id_part = kwargs.get('id_part', None)

    # get catalogue if there
    id_catalogue = request.POST.get('catalogue',None)
    Q_cat = Q()
    if id_catalogue:
        try:
            catalogue = Catalogue.objects.get(organisation=request.user.organisation, id=id_catalogue)
            Q_cat = Q(catalogue=catalogue)
            # print Q_cat
        except:
            print "Wrong catalogue ID"

    if id_part:
        q5 = Q(id = id_part)

    parts = Part.objects.filter(Q_cat & q0 & q1 & q2 & q3 & q5, organisation = organisation,
                                financial_card__isnull = False,
                                financial_card__positive_obsolete_analysis = True,
                                financial_card__year_restocking__isnull = False)

    if not decrease_rate:
        decrease_rate = organisation.financial_settings.yearly_selling_decrease_ratio
    for part in parts:
        stock = part.financial_card.stock
        selling_volumes = part.financial_card.selling_volumes
        sp3d_price = part.financial_card.sp3d_selling_price
        selling_price = part.financial_card.selling_repriced
        for i in range(5):
            year_volume = selling_volumes*pow(1 - decrease_rate, i)
            stock -= year_volume
            if stock < 0:
                yearly_margin_list[i] += round(- stock * (selling_price - sp3d_price)*currency_rate,2)
                stock = 0

    return yearly_margin_list



def buildPartQueriesFromURLParams(dic):
    # get filters in request parameters, and build sub filters
    appliance = dic.get('appliance', '')
    parttype = dic.get('parttype', '')
    technology = dic.get('technology', '')
    material = dic.get('material', '')
    printable = dic.get('printable', '')
    restock = dic.get('restock', '')
    obsolete = dic.get('obsolete', '')
    longtail = dic.get('longtail', '')
    shortage = dic.get('shortage', '')
    pex = dic.get('pex', '')
    q0 = Q()
    q1 = Q()
    q2 = Q()
    q3 = Q()
    q4 = Q()
    if printable:
        q0 &= Q(final_card__techno_material__isnull = False)
    elif restock:
        q0 &= Q(financial_card__year_restocking__isnull = False) & Q(final_card__techno_material__isnull = False)
    if appliance:
        appliance = appliance.split("--")
        q1 &= Q(type__appliance_family__name__in = appliance)
    if parttype:
        q2 &= Q(type__name = parttype)
    if technology and material:
        q3 &= Q(final_card__techno_material__technology__name = technology) & Q(final_card__techno_material__material__name = material)
    if obsolete:
        q4 &= Q(financial_card__positive_obsolete_analysis = True)
    elif longtail:
        q4 &= Q(financial_card__positive_longtail_analysis = True)
    elif shortage:
        q4 &= Q(financial_card__positive_shortage_analysis = True)
    elif pex:
        q4 &= Q(financial_card__positive_pex_analysis = True)

    return q0, q1, q2, q3, q4



def getBulkUploadSumUp(request):
    organisation = request.user.organisation
    parts_sumup = None
    parttype_distrib = []
    appliance_fam_distrib = []
    techno_material_distrib = []
    obsolete_margin_5y = None
    longtail_margin_5y  = None
    conversion_rate = request.user.currency.rate

    selling_decrease = 1 - organisation.financial_settings.yearly_selling_decrease_ratio
    latest_bulk_upload = BulkPartUpload.objects.filter(created_by__organisation = organisation).order_by('-date_created').first()

    # get catalogue
    id_catalogue = request.GET.get('catalogue', None)
    Q_cat = Q()
    try:
        catalogue = Catalogue.objects.get(organisation = request.user.organisation, id = id_catalogue)
    except:
        # catalogue = request.user.organisation.catalogue_set.first()
        catalogue = None
    if catalogue:
        Q_cat = Q(catalogue = catalogue)

    # if latest_bulk_upload:
    parts_sumup = Part.objects.filter(Q_cat, organisation = organisation).aggregate(
        parts_total = Sum(Case(When(~Q(pk=None), then=1),default = 0, output_field=IntegerField())),
        parts_with_type = Sum(Case(When(type__isnull=False, then=1), default = 0, output_field=IntegerField())),
        parts_with_final_card = Sum(Case(When(Q(final_card__techno_material__isnull=False), then=1), default = 0, output_field=IntegerField())),
        parts_out_in_5_y = Sum(Case(When(Q(final_card__isnull=False) & Q(financial_card__year_restocking__isnull = False), then=1), default = 0, output_field=IntegerField())),
        parts_positive_obsolete_analysis = Sum(Case(When(Q(financial_card__positive_obsolete_analysis = True) & Q(financial_card__year_restocking__isnull = False), then=1), default = 0, output_field=IntegerField())),
        parts_positive_longtail_analysis = Sum(Case(When(Q(financial_card__positive_longtail_analysis = True), then=1), default = 0, output_field=IntegerField())),
        parts_positive_pex_analysis = Sum(Case(When(Q(financial_card__positive_pex_analysis = True), then=1), default = 0, output_field=IntegerField())),
        parts_positive_shortage_analysis = Sum(Case(When(Q(financial_card__positive_shortage_analysis = True), then=1), default = 0, output_field=IntegerField())),
    )

    q0, q1, q2, q3, q4 = buildPartQueriesFromURLParams(request.GET)

    appliance_fam_distrib =  Part.objects.filter(Q_cat & q0 & q2 & q3 & q4,organisation = organisation, type__isnull=False, type__appliance_family__isnull=False).values('type__appliance_family__name').annotate(count=Count('type__appliance_family__name')).order_by('-count')
    parttype_distrib =  Part.objects.filter(Q_cat & q0 & q1 & q3 & q4,organisation = organisation, type__isnull=False).values('type__name').annotate(count=Count('type__name')).order_by('-count')
    techno_material_distrib =  Part.objects.filter(Q_cat & q0 & q1 & q2 & q4,organisation = organisation, final_card__isnull=False, final_card__techno_material__isnull=False).values('final_card__techno_material__technology__name', 'final_card__techno_material__material__name').annotate(count=Count('pk')).order_by('-count')
    # for the next, I don't put q4 so that financial figures are not changed when user selects a filter like 'obsolete parts'
    obsolete_margin_5y = Part.objects.filter(Q_cat & q0 & q1 & q2 & q3,organisation = organisation, financial_card__positive_obsolete_analysis = True).values('financial_card__cost_saving_5y').annotate(converted=F('financial_card__cost_saving_5y')*conversion_rate).aggregate(total = Sum('converted'))
    longtail_margin_5y = Part.objects.filter(Q_cat & q0 & q1 & q2 & q3,organisation = organisation, financial_card__positive_longtail_analysis = True).values('financial_card__cost_saving_5y').annotate(converted=F('financial_card__cost_saving_5y')*conversion_rate).aggregate(total = Sum('converted'))
    pex_margin = Part.objects.filter(Q_cat & q0 & q1 & q2 & q3,organisation = organisation, financial_card__positive_pex_analysis = True).values('financial_card__cost_saving_pex').annotate(converted=F('financial_card__cost_saving_pex')*conversion_rate).aggregate(total = Sum('converted'))
    shortage_margin = Part.objects.filter(Q_cat & q0 & q1 & q2 & q3,organisation = organisation, financial_card__positive_shortage_analysis = True).values('financial_card__cost_saving_shortage').annotate(converted=F('financial_card__cost_saving_shortage')*conversion_rate).aggregate(total = Sum('converted'))

    return parts_sumup, parttype_distrib, appliance_fam_distrib, techno_material_distrib, latest_bulk_upload, obsolete_margin_5y, longtail_margin_5y, pex_margin,shortage_margin, catalogue



def getPartSumUp(*args, **kwargs):
    organisation = kwargs.get('organisation', None)
    parts_sumup = Part.objects.filter(*args,**kwargs).aggregate(
        parts_total = Sum(Case(When(~Q(pk=None), then=1),default = 0, output_field=IntegerField())),
        parts_new = Sum(Case(When(status__id=1, then=1), default = 0, output_field=IntegerField())),
        parts_pending_indus = Sum(Case(When(status__id=2, then=1), default = 0, output_field=IntegerField())),
        parts_disqualified = Sum(Case(When(status__id=3, then=1),default = 0,output_field=IntegerField())),
        parts_industrialized = Sum(Case(When(status__id=4, then=1),default = 0,output_field=IntegerField())),
        parts_metal = Sum(Case(When(material__family="metal", then=1),default = 0,output_field=IntegerField())),
        parts_plastic = Sum(Case(When(material__family="plastic", then=1),default = 0,output_field=IntegerField())),
    )
    for key, item in parts_sumup.iteritems():
        if item is None:
            parts_sumup[key]=0

    appliance_fam_distrib =  Part.objects.filter(organisation = organisation, type__isnull=False, type__appliance_family__isnull=False).values('type__appliance_family__name').annotate(count=Count('type__appliance_family__name')).order_by('-count')
    parttype_distrib =  Part.objects.filter(organisation = organisation, type__isnull=False).values('type__name').annotate(count=Count('type__name')).order_by('-count')
    return parts_sumup, appliance_fam_distrib, parttype_distrib

def getApplianceFamilyDistribution(organisation):
    distribution =  Part.objects.filter(organisation = organisation).values('type__appliance_family__name').annotate(count=Count('type__appliance_family__name')).order_by('-count')
    return distribution

def getOrganisationCapacity(organisation):
    images = PartImage.objects.filter

def getfiledata(file):
    data=''
    type="BULK"
    filename, file_extension = os.path.splitext('%s'%file)

    if file_extension.lower() == '.stl':
        type="STL"
        temp = tempfile.NamedTemporaryFile(delete = False)
        # temp = open(dir_path + "/test.stl", 'wb+')
        for chunk in file.chunks():
            temp.write(chunk)
        temp.close()
        # stl_mesh = mesh.Mesh.from_file(os.path.join(dir_path, 'test.stl'))
        stl_mesh = mesh.Mesh.from_file(temp.name)
        volume, cog, inertia = stl_mesh.get_mass_properties()

        print("Volume                                  = {0}".format(volume))
        print("Position of the center of gravity (COG) = {0}".format(cog))
        print("Inertia matrix at expressed at the COG  = {0}".format(inertia[0,:]))
        print("                                          {0}".format(inertia[1,:]))
        print("                                          {0}".format(inertia[2,:]))
        os.unlink(temp.name)
        data = {
            'volume': volume,
            'cog': cog.tolist(),
            'inertia': inertia.tolist(),
        }

    if file_extension.lower() in ['.sldprt','.sldasm','.step','.iges','.gcode']:
        type="3D"
    if file_extension.lower() in ['.dwg', '.dxf']:
        type='2D'
    return type, json.dumps(data)



def upload_bulk_parts(file, user, **kwargs):
    filename, file_extension = os.path.splitext('%s'%file)
    # check file extension
    if not file_extension.lower() == '.csv':
        return None

    # create temporary file
    temp = tempfile.NamedTemporaryFile(delete = False)
    for chunk in file.chunks():
        temp.write(chunk)
    temp.close()

    # create a instance of Bulk PartUpload
    bulk_upload = BulkPartUpload(created_by = user)
    bulk_upload.file = file
    bulk_upload.save()

    # get catalogue
    catalogue_id = kwargs.pop('catalogue-id',None)
    try:
        catalogue = Catalogue.objects.get(id=catalogue_id, organisation = user.organisation)
    except:
        catalogue = Catalogue.objects.create(organisation = user.organisation, name = "analysis %s"%datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    kwargs['catalogue'] = catalogue

    # proccess temporary file to populate database
    def AsynchronousAnalysis(temp, bulk_upload):
        time_begin = datetime.datetime.now()
        error_list=[]
        warning_list=[]
        fieldnames = ['reference', 'name', 'type', 'appliance_family', 'weight',
                        'x', 'y', 'z','stock', 'yearly_selling_volumes',
                        'selling_price','former_production_cost', 'former_moq','shortage_volumes','pex_volumes','analysis_type']
        with open(temp.name, 'rb+') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames = fieldnames)
            transaction.set_autocommit(False)
            for index, row in enumerate(reader, start=1):
                print index
                if index == 1:continue #jump first row
                bulk_upload.finished_entries = index
                # commit transaction of queries every 1000 queries for computation speed purposes
                if index % 200 == 0:
                    bulk_upload.save()
                    transaction.commit()

                if row.get('reference',None):
                    with transaction.atomic():
                        part, error_dic, warning_dic = processPartRow(row, bulk_upload, user, **kwargs)
                    if error_dic:
                        error_dic["row_index"] = index
                        # error_list.append(error_dic)
                    if warning_dic:
                        warning_dic["row_index"] = index
                        # warning_list.append(warning_dic)
            transaction.commit() #commit rest of queries still in transaction

        transaction.set_autocommit(True)
        bulk_upload.errors = "%s"%error_list
        bulk_upload.warnings = "%s"%warning_list
        bulk_upload.finished = True
        bulk_upload.save()
        os.unlink(temp.name)
        pretty_errors (error_list)
        print "ALGO TIME: %s"%(datetime.datetime.now()-time_begin)
        return None


    t = Thread(target = AsynchronousAnalysis, args=(temp, bulk_upload))
    t.daemon = True
    t.start()
    return None



def processPartRow(row, bulk_upload, user, **kwargs):
    part = None
    error_dic = {}
    warning_dic = {}
    try:
        # extract all row values
        _reference = row.get('reference',None)
        _name = row.get('name',None)
        _appliance_family = row.get('appliance_family',None)
        _type = row.get('type',None)
        _weight = row.get('weight',None)
        _x = row.get('x',None)
        _y = row.get('y',None)
        _z = row.get('z',None)
        _stock = row.get('stock',None)
        _yearly_selling_volumes = row.get('yearly_selling_volumes',None)
        _selling_price = row.get('selling_price',None)
        _former_production_cost = row.get('former_production_cost',None)
        _former_moq = row.get('former_moq',None)
        _analysis_type = row.get('analysis_type',None)
        _shortage_volumes = row.get('shortage_volumes', None)
        _pex_volumes = row.get('pex_volumes', None)

        catalogue = kwargs.pop("catalogue")
        # check errors on fields
        # MANDATORY FIELD  - reference
        if _reference:
            _reference = _reference.upper().strip()
        else:
            error_dic["reference"] = "Part Reference is missing"
        # MANDATORY FIELD  - name
        if _name:
            _name = re.sub(' +',' ',_name.strip()) #remove leading ending and multiple spaces in a row
            _name = unicode(_name.decode('latin'))
        else:
            error_dic["name"] = "Part Name is missing"
        #  MANDATORY FIELD  - appliance family
        # if not _appliance_family:
        #     appl_fams = ApplianceFamily.objects.all()
        #     for appl_fam in appl_fams:
        #         if appl_fam.name.lower() in _name.lower():
        #             _appliance_family = appl_fam.name
        #             break
        if _appliance_family:
            _appliance_family = re.sub(' +',' ',_appliance_family.strip()) #remove leading ending and multiple spaces in a row
            _appliance_family = unicode(_appliance_family.decode('latin'))
        else:
            warning_dic["appliance_family"] = "Appliance Family is missing and no match was found from name"

        #  MANDATORY FIELD  - weight
        if _weight:
            try:
                _weight = float(_weight.strip())
            except ValueError:
                _weight = None
                warning_dic["weight"] = "Part Weight is not a float"
        else:
            _weight = None
            warning_dic["weight"] = "Part Weight is missing"

        #  OPTIONAL FIELD  - Part type
        if _type:
            _type = re.sub(' +',' ',_type.strip()) #remove leading ending and multiple spaces in a row
            _type = unicode(_type.decode('latin'))
        else:
            warning_dic["type"] = "No Part Type specified"
        #  OPTIONAL FIELDS  - Dimensions
        if _x and _y and _z:
            try:
                _x = float(_x.strip())
                _y = float(_y.strip())
                _z = float(_z.strip())
            except ValueError:
                _x = None
                _y = None
                _z = None
                warning_dic["x_y_z"] = "Part Dimensions are not floats"
        else:
            warning_dic["x_y_z"] = "Part Dimensions are missing"

        if _stock:
            try:
                _stock = int(_stock.replace(',', '').strip())
            except ValueError:
                _stock = 0
                error_dic['stock'] = "not an integer"

        if _yearly_selling_volumes:
            try:
                _yearly_selling_volumes = int(_yearly_selling_volumes.replace(',', '').strip())
            except ValueError:
                _yearly_selling_volumes = None
                error_dic['yearly_selling_volumes'] = "not an int"

        if _shortage_volumes:
            try:
                _shortage_volumes = int(_shortage_volumes.replace(',', '').strip())
            except ValueError:
                _shortage_volumes = None
                warning_dic['_shortage_volumes'] = "not an int"

        if _pex_volumes:
            try:
                _pex_volumes = int(_pex_volumes.replace(',', '').strip())
            except ValueError:
                _pex_volumes = None
                warning_dic['_pex_volumes'] = "not an int"

        if _selling_price:
            try:
                _selling_price = float(_selling_price.replace(',', '').strip())
            except ValueError:
                _selling_price = None
                error_dic['_selling_price'] = "not a float"

        if _former_moq:
            try:
                _former_moq = int(_former_moq.strip())
            except ValueError:
                _former_moq = None
                error_dic["former_moq"] = "not integer"

        if _former_production_cost:
            try:
                _former_production_cost = float(_former_production_cost.strip())
            except ValueError:
                _former_production_cost = None
                error_dic["former_production_cost"] = "not float"

        if _analysis_type:
            a_type = ['o', 'l']
            _analysis_type = _analysis_type.lower().strip()
            if not _analysis_type in a_type:
                warning_dic['analysis_type']="wrong type of analysis type"
                _analysis_type = ''


        if not error_dic:
            try:
                part = Part.objects\
                    .select_related('type','type__characteristics', 'financial_card', 'final_card')\
                    .get(organisation = user.organisation, reference = _reference)
            except Part.DoesNotExist:
                part = Part(created_by = user, organisation=user.organisation, reference=_reference)

            part.bulk_upload = bulk_upload
            part.name = _name
            if _weight:
                part.weight = _weight
            if _x and _y and _z:
                part.length = _x
                part.width = _y
                part.height = _z

            # find part type
            temp_type = None
            if _type and _appliance_family:
                in_blacklist_q = reduce(operator.or_, (Q(blacklist__iregex='[[:<:]]%s[[:>:]]'%re.escape(x)) for x in _name.split()))
                print in_blacklist_q
                temp_type = PartType.objects.filter((Q(name__icontains=_type) | Q(keywords__icontains=_type)) & ~in_blacklist_q, appliance_family__name__icontains = _appliance_family).exclude(name="N/A").first()
            if not temp_type:
                type_prediction = part_type_from_name_1(_name, _appliance_family)
                temp_type = type_prediction.get('part_type', None)
            part.type = temp_type
            if not temp_type:
                warning_dic["part_type"] = "Part Type not found"
            # save part
            part.catalogue = catalogue
            part.save()

            if part.type and part.type.characteristics:
                new_charac = part.type.characteristics
                new_charac.pk = part.characteristics.pk if part.characteristics else None
                new_charac.part_type = None
                new_charac.part = part
                new_charac.save()
            elif part.type and not part.type.characteristics:
                if part.characteristics:
                    part.characteristics.delete()
                    part.characteristics = None #protection because transaction is not commited yet
                warning_dic["characteristics"] = "Part Type %s - %s - %s has No characteristics attached"%(part.type.id, part.type.name, part.type.appliance_family)
            elif not part.type and part.characteristics:
                part.characteristics.delete()
                part.characteristics = None


            # find couple techno_material match
            part = findTechnoMaterial(part, fallback_mode=False)

            # refresh instance of part
            # part.refresh_from_db()

            print "WARNING DIC:%s"%warning_dic
            print "ERROR DIC:%s"%error_dic
            ####FINANCIAL ANALYSIS
            if not error_dic and part:
                # find financial card if exist, otherwise create new:
                kwargs['_stock'] = _stock
                kwargs['_yearly_selling_volumes'] = _yearly_selling_volumes
                kwargs['_selling_price'] = _selling_price
                kwargs['_former_moq'] = _former_moq
                kwargs['_former_production_cost'] = _former_production_cost
                kwargs['_shortage_volumes'] = _shortage_volumes
                kwargs['_pex_volumes'] = _pex_volumes
                kwargs['_analysis_type'] = _analysis_type
                UpdateFinancialAnalysis(part,**kwargs)
            elif part.financial_card:
                part.financial_card.reset()

            # refresh instance of part
            # part.refresh_from_db()

    except Exception as e:
        print "EXCEPTION ############################################################################\
        ############################################################################"
        print e
        print e.message
        error_dic['general_error'] = e.message
    if part:
        part.save()


    return part, error_dic, warning_dic


def getPartCost(part, yearly_volume):
    sp3d_selling_price = None
    try:
        yearly_volume = int(float(yearly_volume))
        if yearly_volume < 0:
            raise ValueError("Yearly Volume is negative")
        production_cost = part.final_card.techno_material.cost_per_gram*part.weight
        cpr = part.organisation.financial_settings.cost_plus_ratio
        cost_plus = production_cost * (1+cpr)
        max_price_appliance = part.organisation.financial_settings.appliance_repricing_maxvalue_ratio * part.type.appliance_family.retail_price
        r1 = part.organisation.financial_settings.repricing_new_max_ratio
        x2 = (10*(max_price_appliance + cost_plus))/cost_plus
        if yearly_volume and cost_plus < max_price_appliance:

            # sp3d selling price
            if yearly_volume < 10:
                sp3d_selling_price = (max_price_appliance + cost_plus)/2
            elif 10 <= yearly_volume <= x2:
                sp3d_selling_price = (5*(cost_plus + max_price_appliance)*(max_price_appliance-cost_plus))/(max_price_appliance*yearly_volume) + ((cost_plus + max_price_appliance)*cost_plus)/(2*max_price_appliance)
                # sp3d_selling_price = (max_price_appliance + cost_plus)*r1 + ((max_price_appliance - cost_plus)/(2*(10-100))) * (yearly_volume-10)
            else:
                sp3d_selling_price = cost_plus
        elif yearly_volume and cost_plus > max_price_appliance:
            sp3d_selling_price = cost_plus
    except Exception as e:
        print e

    if sp3d_selling_price:
        sp3d_selling_price = round(sp3d_selling_price,2)
    return sp3d_selling_price





AAA=0
def UpdateFinancialAnalysis(part,**kwargs):
    global AAA
    # get financial card
    if part.financial_card:
        financial_card = part.financial_card

    else:
        financial_card = FinancialCard()
        financial_card.part = part
    # check if refreshing or inputing data
    refreshing = kwargs.get('refreshing', False)

    # get parameters in financial card only if not given (only if refresh financial analysis):
    if refreshing:
        _stock = financial_card.stock
        _yearly_selling_volumes = financial_card.selling_volumes
        _selling_price = financial_card.selling_price
        _former_moq = financial_card.former_moq
        _former_production_cost = financial_card.former_production_cost
        _pex_volumes = financial_card.pex_volumes
        _shortage_volumes = financial_card.shortage_volumes
    else:
        # set up entry values
        _stock = kwargs.get('_stock',0)
        _yearly_selling_volumes = kwargs.get('_yearly_selling_volumes',None)
        _selling_price = kwargs.get('_selling_price',None)
        _former_moq = kwargs.get('_former_moq',None)
        _former_production_cost = kwargs.get('_former_production_cost',None)
        _pex_volumes = kwargs.get('_pex_volumes',None)
        _shortage_volumes = kwargs.get('_shortage_volumes',None)
        if RepresentsInt(_yearly_selling_volumes):financial_card.selling_volumes = _yearly_selling_volumes
        if RepresentsInt(_pex_volumes):financial_card.pex_volumes = _pex_volumes
        if RepresentsInt(_shortage_volumes):financial_card.shortage_volumes = _shortage_volumes
        if RepresentsFloat(_selling_price): financial_card.selling_price = round(_selling_price,2)
        if RepresentsInt(_stock):financial_card.stock = _stock
        if RepresentsInt(_former_moq): financial_card.former_moq = _former_moq
        if RepresentsFloat(_former_production_cost): financial_card.former_production_cost = round(_former_production_cost,2)
    # if final card or type is missing, return
    if not part.final_card or not part.type or not part.weight:
        # reset analysis results
        financial_card.positive_obsolete_analysis = False
        financial_card.positive_pex_analysis = False
        financial_card.positive_shortage_analysis = False
        financial_card.positive_longtail_analysis = False
        financial_card.selling_repriced = None
        financial_card.sp3d_selling_price = None
        financial_card.cost_saving_5y = 0
        financial_card.cost_saving_pex = 0
        financial_card.cost_saving_shortage = 0
        financial_card.production_cost = 0
        financial_card.former_tco = None
        # save
        financial_card.save()
        return part
    # keep former analysis type in memory for the refreshing part:
    former_obsolete = financial_card.positive_obsolete_analysis
    former_longtail = financial_card.positive_longtail_analysis

    ## reset analysis results
    financial_card.positive_obsolete_analysis = False
    financial_card.positive_longtail_analysis = False
    financial_card.positive_pex_analysis = False
    financial_card.positive_shortage_analysis = False
    financial_card.selling_repriced = None
    financial_card.sp3d_selling_price = None
    financial_card.cost_saving_5y = 0
    financial_card.cost_saving_pex = 0
    financial_card.cost_saving_shortage = 0
    financial_card.former_tco = None
    # financial_card.former_production_cost = None
    # financial_card.selling_price = None
    # financial_card.former_moq = None
    ## initialize some financial values
    production_cost = part.final_card.techno_material.cost_per_gram*part.weight
    cpr = part.organisation.financial_settings.cost_plus_ratio
    cost_plus = production_cost * (1+cpr)
    max_price_appliance = part.organisation.financial_settings.appliance_repricing_maxvalue_ratio * part.type.appliance_family.retail_price
    repricing_authorized = part.organisation.financial_settings.repricing
    # analysis_type = kwargs.get('analysis-type', None)
    _analysis_type = kwargs.get('_analysis_type', None)
    r1 = part.organisation.financial_settings.repricing_new_max_ratio
    r2 = part.organisation.financial_settings.client_margin
    r3 = part.organisation.financial_settings.yearly_stock_price_ratio
    r4 = part.organisation.financial_settings.yearly_selling_decrease_ratio
    r5 = part.organisation.financial_settings.avg_shortage_duration
    r6 = part.organisation.financial_settings.shortage_volume_loss_ratio
    if _yearly_selling_volumes:
        total_sold = _yearly_selling_volumes * (pow(1-r4,5) - 1) / ((1-r4) - 1)
    # Check stock shortage year only for obsolete part
    if (_analysis_type == "o" or former_obsolete) and RepresentsInt(_stock) and _yearly_selling_volumes and total_sold > _stock:
        _year_out = 0
        _s = _stock
        for i in range(5):
            _year_out += 1
            year_volume = int(round(_yearly_selling_volumes*pow(1 - r4, i)))
            _s += - year_volume
            if _s < 0:
                financial_card.year_restocking = _year_out
                break
    else:
        financial_card.year_restocking = None
    # for OBSOLETE AND LONGTAIL analysis, check that selling volume and cost plus are good
    if _yearly_selling_volumes and cost_plus < max_price_appliance:

        # sp3d selling price
        financial_card.sp3d_selling_price = getPartCost(part, _yearly_selling_volumes)
        # OBSOLETE PARTS ANALYSIS

        if (_analysis_type == "o" or former_obsolete) and RepresentsInt(_stock):
            # repricing of client price
            if repricing_authorized and _selling_price:
                selling_repriced = max(_selling_price, min(sp3d_selling_price * (1+r2), max_price_appliance))
            elif repricing_authorized:
                selling_repriced = min(sp3d_selling_price * (1+r2), max_price_appliance)
            else:
                selling_repriced = None
            financial_card.selling_repriced = selling_repriced

            # find sp3d selling price if possible
            if not selling_repriced or total_sold < _stock:
                financial_card.positive_obsolete_analysis = False
                financial_card.cost_saving_5y = 0
            else:
                cost_saving =  (total_sold - _stock) * (selling_repriced - sp3d_selling_price)
                financial_card.positive_obsolete_analysis = True
                financial_card.cost_saving_5y = round(cost_saving,2)




        # LONG TAIL ANALYSIS
        if (_analysis_type == "l" or former_longtail) and RepresentsInt(_stock) and _former_moq and _former_production_cost:
            buy_quantity = (_stock - total_sold) / _former_moq
            if buy_quantity < 0:
                buy_quantity = - buy_quantity
                if buy_quantity < _former_moq:
                    buy_quantity = _former_moq
            else:
                buy_quantity = 0
            stock = _stock + buy_quantity
            cost_waste =  (stock - total_sold)*_former_production_cost
            # if financial_card.year_restocking
            cost_inventory = r3 * _former_production_cost * (5*stock - _yearly_selling_volumes*((pow(1-r4,5) - 1) / ((1- r4) - 1)))
            tco = _former_production_cost + (cost_waste + cost_inventory + 0.0)/total_sold
            if sp3d_selling_price > tco:
                financial_card.positive_longtail_analysis = False
                financial_card.cost_saving_5y = 0
            else:
                cost_saving =  total_sold * (tco - sp3d_selling_price)
                financial_card.positive_longtail_analysis = True
                financial_card.cost_saving_5y = round(cost_saving,2)
            financial_card.former_tco = round(tco,2)



    # for PEX analysis, check that selling volume and cost plus are good
    if RepresentsInt(_pex_volumes) and cost_plus < 200:
        if cost_plus < max_price_appliance:
            # sp3d selling price
            sp3d_selling_price_temp = getPartCost(part, _pex_volumes)
        else:
            sp3d_selling_price_temp = cost_plus

        # PEX ANALYSIS
        if part.type.appliance_family:
            family_detail = part.organisation.ApplianceFamilyDetails.filter(appliance_family = part.type.appliance_family).first()
            if family_detail and family_detail.replacement_cost and family_detail.replacement_cost > sp3d_selling_price_temp:
                cost_saving =  _pex_volumes * (family_detail.replacement_cost - sp3d_selling_price_temp)
                financial_card.cost_saving_pex = round(cost_saving,2)
                financial_card.positive_pex_analysis = True
            elif 300 > sp3d_selling_price_temp:
                cost_saving =  _pex_volumes * (300 - sp3d_selling_price_temp)
                financial_card.cost_saving_pex = round(cost_saving,2)
                financial_card.positive_pex_analysis = True
            else:
                financial_card.cost_saving_pex = 0
                financial_card.positive_pex_analysis = False
    elif not RepresentsInt(_pex_volumes):
        print "PEX volume not int"
    elif not cost_plus < max_price_appliance:
        print "cost plus < max price appliance : %s < %s"(cost_plus,max_price_appliance)



    # for SHORTAGE analysis, check that selling volume and cost plus are good
    if RepresentsInt(_shortage_volumes) and cost_plus < max_price_appliance:

        sp3d_selling_price_temp = getPartCost(part, _shortage_volumes)
        # SHORTAGE ANALYSIS
        if _former_production_cost and _selling_price:
            if sp3d_selling_price_temp < _selling_price:
                cost_saving = ((_selling_price - sp3d_selling_price_temp) - (_selling_price - _former_production_cost)*(1-r6)) * _shortage_volumes
                if cost_saving > 0:
                    financial_card.cost_saving_shortage = round(cost_saving,2)
                    financial_card.positive_shortage_analysis = True
                else:
                    financial_card.cost_saving_shortage = 0
                    financial_card.positive_shortage_analysis = False

    # save financial card:
    financial_card.production_cost = round(production_cost,2)
    financial_card.save()
    part.financial_card = financial_card
    return part





def analysis_to_csv(user, catalogue):
    organisation = user.organisation
    if RepresentsInt(catalogue):
        catalogue = Catalogue.objects.filter(id = int(catalogue), organisation = user.organisation)
    else:
        catalogue = Catalogue.objects.filter(organisation = user.organisation)

    # latest_bulk_upload = BulkPartUpload.objects.filter(created_by__organisation = user.organisation).order_by('-date_created').first()
    parts = None
    export = None
    currency_rate = user.currency.rate
    if catalogue:
        parts = Part.objects.filter(organisation = organisation, catalogue__in = catalogue)\
            .select_related('type', 'type__appliance_family', 'final_card', 'organisation__financial_settings')

    if parts:
        temp = tempfile.NamedTemporaryFile(delete = False)
        with open(temp.name, 'rb+') as csvfile:
            fieldnames = ['reference', 'name', 'type', 'appliance_family', 'weight', 'x', 'y', 'z','max_price_appliance', 'max_price_part',
                'technology', 'material', 'production_cost', 'cost_plus',
                'obsolete','long_tail', 'yearly_stock_price_ratio', 'cost_plus_ratio', 'client_margin', 'appliance_repricing_maxvalue_ratio','repricing_new_max_ratio', 'yearly_stock_price_ratio',
                'stock','yearly_selling_volumes', 'year_restocking', 'selling_price','selling_repriced', 'sp3d_selling_price', 'margin_y1', 'margin_y2', 'margin_y3', 'margin_y4', 'margin_y5','margin_accumulated',
                'sp3d_margin_y1', 'sp3d_margin_y2', 'sp3d_margin_y3', 'sp3d_margin_y4', 'sp3d_margin_y5', 'sp3d_margin_accumulated',
                'former_moq','former_production_cost','former_tco','sp3d_production_cost','cost_saving_5y',
                'shortage', 'pex','cost_saving_pex','cost_saving_shortage'
                ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for part in parts:
                row={}
                row['reference'] = str(part.reference)
                row['name'] = str(part.name.encode('latin'))
                row['weight'] = str(part.weight)
                row['x'] = str(part.length)
                row['y'] = str(part.width)
                row['z'] = str(part.height)
                if part.type:
                    row['type'] = str(part.type.name)
                    row['appliance_family'] = str(part.type.appliance_family.name)
                    row['max_price_appliance'] = str(part.type.appliance_family.retail_price * currency_rate)
                    row['max_price_part'] = str(part.organisation.financial_settings.appliance_repricing_maxvalue_ratio * part.type.appliance_family.retail_price * currency_rate)
                if part.final_card:
                    row['technology'] = str(part.final_card.techno_material.technology.name)
                    row['material'] = str(part.final_card.techno_material.material.name)
                    if part.weight:
                        row['production_cost'] = str(part.final_card.techno_material.cost_per_gram * part.weight * currency_rate)
                        row['cost_plus'] = str((part.final_card.techno_material.cost_per_gram * part.weight)*(1 + part.organisation.financial_settings.cost_plus_ratio)*currency_rate)
                if part.organisation.financial_settings:
                    financial_settings = part.organisation.financial_settings
                    row['yearly_stock_price_ratio'] = str(financial_settings.yearly_stock_price_ratio)
                    row['cost_plus_ratio'] = str(financial_settings.cost_plus_ratio)
                    row['client_margin'] = str(financial_settings.client_margin * currency_rate) if financial_settings.client_margin else str(financial_settings.client_margin)
                    row['appliance_repricing_maxvalue_ratio'] = str(financial_settings.appliance_repricing_maxvalue_ratio)
                    row['repricing_new_max_ratio'] = str(financial_settings.repricing_new_max_ratio)

                if part.financial_card:
                    financial_card = part.financial_card
                    row['obsolete'] = str(financial_card.positive_obsolete_analysis)
                    row['long_tail'] = str(financial_card.positive_longtail_analysis)
                    row['shortage'] = str(financial_card.positive_shortage_analysis)
                    row['pex'] = str(financial_card.positive_pex_analysis)
                    row['stock'] = str(financial_card.stock)
                    row['year_restocking'] = str(financial_card.year_restocking)
                    row['yearly_selling_volumes'] = str(financial_card.selling_volumes)
                    row['selling_price'] = str(financial_card.selling_price * currency_rate) if financial_card.selling_price else str(financial_card.selling_price)
                    row['selling_repriced'] = str(financial_card.selling_repriced * currency_rate) if financial_card.selling_repriced else str(financial_card.selling_repriced)
                    row['sp3d_selling_price'] = str(financial_card.sp3d_selling_price * currency_rate) if financial_card.sp3d_selling_price else str(financial_card.sp3d_selling_price)
                    row['former_moq'] = str(financial_card.former_moq)
                    row['former_production_cost'] = str(financial_card.former_production_cost * currency_rate) if financial_card.former_production_cost else str(financial_card.former_production_cost)
                    row['former_tco'] = str(financial_card.former_tco * currency_rate) if financial_card.former_tco else str(financial_card.former_tco)
                    row['sp3d_production_cost'] = str(financial_card.production_cost * currency_rate) if financial_card.production_cost else str(financial_card.production_cost)
                    row['cost_saving_5y'] = str(financial_card.cost_saving_5y * currency_rate) if financial_card.cost_saving_5y else str(financial_card.cost_saving_5y)
                    row['cost_saving_shortage'] = str(financial_card.cost_saving_shortage * currency_rate) if financial_card.cost_saving_shortage else str(financial_card.cost_saving_shortage)
                    row['cost_saving_pex'] = str(financial_card.cost_saving_pex * currency_rate) if financial_card.cost_saving_pex else str(financial_card.cost_saving_pex)
                    # 5y analysis
                    if financial_card.positive_obsolete_analysis:
                        decrease_rate = organisation.financial_settings.yearly_selling_decrease_ratio
                        stock = part.financial_card.stock
                        selling_volumes = part.financial_card.selling_volumes
                        sp3d_price = part.financial_card.sp3d_selling_price
                        production_cost = part.financial_card.production_cost
                        selling_price = part.financial_card.selling_repriced
                        row['margin_accumulated'] = 0
                        row['sp3d_margin_accumulated'] = 0
                        for i in range(5):
                            year_volume = int(round(selling_volumes*pow(1 - decrease_rate, i)))
                            stock += - year_volume
                            if stock < 0:
                                row['margin_y%s'%(i+1)] = - stock * (selling_price - sp3d_price) * currency_rate
                                row['sp3d_margin_y%s'%(i+1)] = - stock * (sp3d_price - production_cost) * currency_rate
                                row['margin_accumulated'] += row['margin_y%s'%(i+1)]
                                row['sp3d_margin_accumulated'] += row['sp3d_margin_y%s'%(i+1)]
                                stock = 0
                            else:
                                row['margin_y%s'%(i+1)] = 0

                writer.writerow(row)
            export = AnalysisExport.objects.create(created_by = user, file = File(csvfile))
        os.unlink(temp.name)
    return export







def translate_matrix(file):
    error_list=[]
    warning_list=[]
    filename, file_extension = os.path.splitext('%s'%file)

    # check file extension
    if not file_extension.lower() == '.csv':
        error_list.append("WRONG FILE EXTENSION")
        return error_list, warning_list


    # check file name
    if filename.lower() == 'techno_materials':
        fieldnames = ['technology','material', 'c','d','e','f','g','h','i','j','is_visual','is_transparent','is_rubbery','is_water_resistant','is_chemical_resistant',
            'is_flame_retardant','is_food_grade','flame_retardancy','min_temp','max_temp']
    elif filename.lower() == 'materials':
        fieldnames = ['material','description', 'type','d','e','f','g','h','i','j','is_visual','is_transparent','is_rubbery','is_water_resistant','is_chemical_resistant',
            'is_flame_retardant','is_food_grade','flame_retardancy','min_temp','max_temp']
    elif filename.lower() == 'technologies':
        fieldnames = ['technology','max_X', 'max_Y','max_Z','description','f','g','h','i','j','is_visual','is_transparent','is_rubbery','is_water_resistant','is_chemical_resistant',
            'is_flame_retardant','is_food_grade','flame_retardancy','min_temp','max_temp']
    elif filename.lower() == 'part_types':
        fieldnames = ['part_type','appliance_family', 'keywords','blacklist','e','f','g','h','i','printable','is_visual','is_transparent','is_rubbery','is_water_resistant','is_chemical_resistant',
            'is_flame_retardant','is_food_grade','flame_retardancy','min_temp','max_temp']
    else:
        error_list.append("WRONG FILE NAME")
        return error_list, warning_list


    # copy csv in temporary file
    temp = tempfile.NamedTemporaryFile(delete = False)
    for chunk in file.chunks():
        temp.write(chunk)
    temp.close()


    # treat temporary file to populate database
    with open(temp.name, 'rb+') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames = fieldnames)
        for index, row in enumerate(reader, start=1):
            print index
            if index == 1:continue
            if row.get('material',None) or row.get('technology',None) or row.get('part_type',None) :
                error, warning, cleaned_dic = CleanCSV(row)
                if error:
                    error['row_number'] = index
                    error_list.append(error)
                else:
                    # add warnings to list
                    if warning:
                        warning['row_number'] = index
                        warning_list.append(warning)


                    # remove all fields not related
                    if 'techno_material' in cleaned_dic:
                        cleaned_dic.pop('material', None)
                        cleaned_dic.pop('technology', None)
                        cleaned_dic.pop('part_type', None)
                        cleaned_dic.pop('part', None)
                    elif 'material' in cleaned_dic:
                        cleaned_dic.pop('techno_material', None)
                        cleaned_dic.pop('technology', None)
                        cleaned_dic.pop('part_type', None)
                        cleaned_dic.pop('part', None)
                    elif 'technology' in cleaned_dic:
                        cleaned_dic.pop('techno_material', None)
                        cleaned_dic.pop('material', None)
                        cleaned_dic.pop('part_type', None)
                        cleaned_dic.pop('part', None)
                    elif 'part_type' in cleaned_dic:
                        cleaned_dic.pop('techno_material', None)
                        cleaned_dic.pop('material', None)
                        cleaned_dic.pop('technology', None)
                        cleaned_dic.pop('part', None)

                    printable = cleaned_dic.pop('printable')

                    # check if characteristic card already exists, update, otherwise create new card
                    if cleaned_dic.get('techno_material',None) and cleaned_dic['techno_material'].characteristics:
                        techno_material = cleaned_dic.pop('techno_material')
                        charac_card = Characteristics.objects.filter(id=techno_material.characteristics.id)
                    elif cleaned_dic.get('material',None) and cleaned_dic['material'].characteristics:
                        material = cleaned_dic.pop('material')
                        charac_card = Characteristics.objects.filter(id=material.characteristics.id)
                    elif cleaned_dic.get('technology',None) and cleaned_dic['technology'].characteristics:
                        technology = cleaned_dic.pop('technology')
                        charac_card = Characteristics.objects.filter(id=technology.characteristics.id)
                    elif cleaned_dic.get('part_type',None) and cleaned_dic['part_type'].characteristics:
                        part_type = cleaned_dic.pop('part_type')
                        charac_card = Characteristics.objects.filter(id=part_type.characteristics.id)
                    else:
                        charac_card = Characteristics.objects.create(**cleaned_dic)
                        # get queryset with this element only:
                        charac_card = Characteristics.objects.filter(id=charac_card.id)


                    # if not printable delete
                    if printable:
                        charac_card.update(**cleaned_dic)
                    else:
                        charac_card.delete()

    os.unlink(temp.name) #delete temp file

    return error_list, warning_list






def RepresentsInt(s):
    try:
        _int = int(s)
        return True
    except:
        return False

def RepresentsFloat(s):
    try:
        _float = float(s)
        return True
    except:
        return False





def CleanCSV(dic):
    error={}
    warning={}
    positive_match = ['true', 'yes', 'y']
    cleaned_dic = {}
    cleaned_dic['is_transparent'] = dic['is_transparent'].lower() in positive_match
    cleaned_dic['is_food_grade'] = dic['is_food_grade'].lower() in positive_match
    cleaned_dic['is_rubbery'] = dic['is_rubbery'].lower() in positive_match
    cleaned_dic['is_visual'] = dic['is_visual'].lower() in positive_match
    cleaned_dic['is_water_resistant'] = dic['is_water_resistant'].lower() in positive_match
    cleaned_dic['is_chemical_resistant'] = dic['is_chemical_resistant'].lower() in positive_match
    cleaned_dic['is_flame_retardant'] = dic['is_flame_retardant'].lower() in positive_match

    if dic.get('printable', None) == "N":
        cleaned_dic['printable'] = False
    else:
        cleaned_dic['printable'] = True
    if RepresentsInt(dic.get('max_temp',None)):
        cleaned_dic['max_temp'] = dic['max_temp']
    else:
        warning["max_temp"]="max Temp is not an Integer"

    if RepresentsInt(dic.get('min_temp',None)):
        cleaned_dic['min_temp'] = dic['min_temp']
    else:
        warning["min_temp"]="min Temp is not an Integer"


    # if is_flame_retardant, look up level:
    if cleaned_dic.get('is_flame_retardant',None) and dic.get('flame_retardancy',None):
        temp_error, flame_retardancy = Characteristics().get_retardant_choice(dic['flame_retardancy'])
        if temp_error:
            error['flame_retardancy'] = temp_error
        cleaned_dic['flame_retardancy'] = flame_retardancy


    # check if technology exists
    if dic.get('technology',None):
        try:
            cleaned_dic['technology'] = Technology.objects.get(name__iexact=dic['technology'])
        except Technology.DoesNotExist:
            error['technology'] = 'Technology %s does not match a technology in database'%dic['technology']


    # check if material exists
    if dic.get('material', None):
        try:
            cleaned_dic['material'] = Material.objects.get(name__iexact=dic['material'])
        except Material.DoesNotExist:
            error['material'] = 'Material %s does not match a material in database'%dic['material']


    # check if part_type exists
    if dic.get('part_type', None) and dic.get('appliance_family', None):
        try:
            temp_appliance_family = ApplianceFamily.objects.get(name__iexact = dic['appliance_family'])
            cleaned_dic['part_type'] = PartType.objects.get(name = dic['part_type'], appliance_family = temp_appliance_family)
            cleaned_dic['part_type'].keywords = dic['keywords']
            cleaned_dic['part_type'].blacklist = dic['blacklist']
            cleaned_dic['part_type'].save()
        except ApplianceFamily.DoesNotExist:
            error['appliance_family'] = 'No match on appliance family %s'%dic['appliance_family']
        except PartType.DoesNotExist:
            part_type = PartType(name= dic['part_type'], appliance_family = temp_appliance_family, keywords = dic['keywords'])
            part_type.save()
            cleaned_dic['part_type'] = part_type


    # check if techno_material exists
    if cleaned_dic.get('material', None) and cleaned_dic.get('technology',None):
        try:
            techno_material = CoupleTechnoMaterial.objects.get(material= cleaned_dic['material'], technology = cleaned_dic['technology'])
        except CoupleTechnoMaterial.DoesNotExist:
            techno_material = CoupleTechnoMaterial(material= cleaned_dic['material'], technology = cleaned_dic['technology'])
            techno_material.save()
        cleaned_dic['techno_material'] = techno_material

    return error, warning, cleaned_dic





def findTechnoMaterial(part, fallback_mode=True):
    errors = []
    list_couple_techno_material = None
    args = []
    kwargs = {}
    perfect_match = False
    discarded_criterias = {}

    # check if part has characteristics attached
    if not part.characteristics:
        print "No prevision Possible, Part has no characteristics attached !"
        return part


    # set up first filters as args for Q and kwargs for rest
    characs = part.characteristics
    # discriminant criterias:
    kwargs['characteristics__is_rubbery'] = characs.is_rubbery
    kwargs['characteristics__is_transparent'] = characs.is_transparent
    # non discriminant criterias:
    kwargs['characteristics__is_visual'] = characs.is_visual
    kwargs['characteristics__is_water_resistant'] = characs.is_water_resistant
    kwargs['characteristics__is_chemical_resistant'] = characs.is_chemical_resistant
    kwargs['material__characteristics__is_flame_retardant'] = characs.is_flame_retardant
    kwargs['characteristics__is_food_grade'] = characs.is_food_grade
    if characs.flame_retardancy == 'NA':higher_ret_list = ['NA', 'HB', 'V2', 'V1', 'V0']
    elif characs.flame_retardancy == 'HB':higher_ret_list = ['HB', 'V2', 'V1', 'V0']
    elif characs.flame_retardancy == 'V2':higher_ret_list = ['V2', 'V1', 'V0']
    elif characs.flame_retardancy == 'V1':higher_ret_list = ['V1', 'V0']
    elif characs.flame_retardancy == 'V0':higher_ret_list = ['V0']
    kwargs['material__characteristics__flame_retardancy__in'] = higher_ret_list

    if part.length and part.width and part.height:
        args.append(
            (Q(technology__max_X__gte=part.length) & Q(technology__max_Y__gte=part.width) & Q(technology__max_Z__gte=part.height)) |
            (Q(technology__max_X__gte=part.length) & Q(technology__max_Y__gte=part.height) & Q(technology__max_Z__gte=part.width)) |
            (Q(technology__max_X__gte=part.width) & Q(technology__max_Y__gte=part.length) & Q(technology__max_Z__gte=part.height)) |
            (Q(technology__max_X__gte=part.width) & Q(technology__max_Y__gte=part.height) & Q(technology__max_Z__gte=part.length)) |
            (Q(technology__max_X__gte=part.height) & Q(technology__max_Y__gte=part.length) & Q(technology__max_Z__gte=part.width)) |
            (Q(technology__max_X__gte=part.height) & Q(technology__max_Y__gte=part.width) & Q(technology__max_Z__gte=part.length))
        )

    # nullable criterias:
    if (characs.min_temp is not None) and (characs.max_temp is not None):
        kwargs['material__characteristics__min_temp__lte'] = characs.min_temp
        kwargs['material__characteristics__max_temp__gte'] = characs.max_temp


    # QUERIES
    # first query filter
    list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs).order_by('-priority_level')
    if list_couple_techno_material:perfect_match=True


    # if no perfect match remove non discriminant characteristics and query again
    if not list_couple_techno_material:
        if not characs.is_visual:
            discarded_criterias['visual part'] = kwargs.pop('characteristics__is_visual')
        if not characs.is_water_resistant:
            discarded_criterias['water resistant'] = kwargs.pop('characteristics__is_water_resistant')
        if not characs.is_water_resistant:
            discarded_criterias['chemical resistant'] = kwargs.pop('characteristics__is_chemical_resistant')
        if not characs.is_flame_retardant:
            discarded_criterias['flame retardant'] = kwargs.pop('material__characteristics__is_flame_retardant')
        if not characs.is_food_grade:
            discarded_criterias['food grade'] = kwargs.pop('characteristics__is_food_grade')
        list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs).order_by('-priority_level')
        if list_couple_techno_material:perfect_match = True



    # in fallback mode remove slowly characteristics
    if fallback_mode:
        # 2 query filter if 1 had no match
        if (not list_couple_techno_material) and ('material__characteristics__min_temp__lte' in kwargs) and ('material__characteristics__max_temp__gte' in kwargs):
            discarded_criterias['min temp'] = kwargs.pop('material__characteristics__min_temp__lte')
            discarded_criterias['max temp'] = kwargs.pop('material__characteristics__max_temp__gte')
            list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs).order_by('-priority_level')


        # 3 query filter if 2 had no match
        if (not list_couple_techno_material) and ('characteristics__is_transparent' in kwargs):
            discarded_criterias['transparent'] = kwargs.pop('characteristics__is_transparent')
            list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs).order_by('-priority_level')

        # 4 query filter if 3 had no match
        if (not list_couple_techno_material) and ('material__characteristics__is_flame_retardant' in kwargs):
            discarded_criterias['flame retardant'] = kwargs.pop('material__characteristics__is_flame_retardant')
            if 'material__characteristics__flame_retardancy__in' in kwargs: kwargs.pop('material__characteristics__flame_retardancy__in')
            list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs).order_by('-priority_level')


        # 5 query filter if 4 had no match
        if (not list_couple_techno_material) and ('characteristics__is_chemical_resistant' in kwargs):
            discarded_criterias['chemical resistant'] = kwargs.pop('characteristics__is_chemical_resistant')
            list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs).order_by('-priority_level')

        # 6 query filter if 5 had no match
        if (not list_couple_techno_material) and ('characteristics__is_water_resistant' in kwargs):
            discarded_criterias['water resistant'] = kwargs.pop('characteristics__is_water_resistant')
            list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs).order_by('-priority_level')

        # 7 query filter if 6 had no match
        if (not list_couple_techno_material) and ('characteristics__is_visual' in kwargs):
            discarded_criterias['visual part'] = kwargs.pop('characteristics__is_visual')
            list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs).order_by('-priority_level')

        # 8 query filter if 7 had no match
        if (not list_couple_techno_material) and ('characteristics__is_food_grade' in kwargs):
            discarded_criterias['food grade'] = kwargs.pop('characteristics__is_food_grade')
            list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs).order_by('-priority_level')

        # 9 query filter if 8 had no match
        if (not list_couple_techno_material) and ('characteristics__is_rubbery' in kwargs):
            discarded_criterias['rubbery'] = kwargs.pop('characteristics__is_rubbery')
            list_couple_techno_material = CoupleTechnoMaterial.objects.filter(*args, **kwargs).order_by('-priority_level')

    # SAVE PART
    if perfect_match and list_couple_techno_material:
        if part.final_card:
            final_card = part.final_card
        else:
            final_card = FinalCard()
            final_card.part = part
        final_card.techno_material = list_couple_techno_material.first()
        final_card.save()
        part.final_card = final_card
        part.save()
    # else remove final card
    elif part.final_card:
        part.final_card.delete()
        part.final_card = None #protection because transaction is not commited yet

    return part




def part_type_from_name_1(name, appliance_family_name):
    if not name:return None
    result = {'intersection':0, 'intersection_f':0, 'part_type': None, 'appliance_family':None}
    name_vector = text_to_vector(name)
    # match with appliance type first
    if appliance_family_name:
        result['appliance_family'] = ApplianceFamily.objects.filter(name__icontains = appliance_family_name).first()
    if not result['appliance_family']:
        appliances_f = ApplianceFamily.objects.all()
        for appliance_f in appliances_f:
            intersection = get_intersection(text_to_vector(appliance_f.name), name_vector)
            # if intersection > 0:
            #     print "FAMILY: %s"%appliance_f
            #     print "V1: %s"%name_vector
            #     print "intersection: %s"%intersection
            if intersection and intersection > result['intersection_f']:
                result['appliance_family'] = appliance_f
                result['intersection_f'] = intersection
    # then look for part type:
    # in_blacklist_q = reduce(operator.or_, (Q(blacklist__icontains=x) for x in name.split()))
    in_blacklist_q = reduce(operator.or_, (Q(blacklist__iregex='[[:<:]]%s[[:>:]]'%re.escape(x)) for x in name.split()))
    # print in_blacklist_q
    if result['appliance_family']:
        part_types = PartType.objects.filter(~in_blacklist_q, appliance_family = result['appliance_family']).exclude(name="N/A").extra(select={'length':'Length(name)'}).order_by('length')
        for part_type in part_types:
            intersection = get_intersection(text_to_vector(part_type.name, 1.5) + text_to_vector(part_type.keywords), name_vector)
            # if intersection > 0:
            #     print in_blacklist_q
            #     print "PART TYPE: %s"%part_type
            #     print "V1: %s"%text_to_vector(part_type.name + " " + part_type.keywords)
            #     print "V2: %s"%name_vector
            #     print "intersection: %s"%intersection
            if intersection and intersection > result['intersection']:
                result['part_type'] = part_type
                result['intersection'] = intersection
        # if no result, look for the NA part types in this appliance:
        if not result['part_type']:
            part_types = PartType.objects.filter(~in_blacklist_q, appliance_family = result['appliance_family'], name="N/A").extra(select={'length':'Length(name)'}).order_by('length')
            for part_type in part_types:
                intersection = get_intersection(text_to_vector(part_type.name, 1.5) + text_to_vector(part_type.keywords), name_vector)
                if intersection and intersection > result['intersection']:
                    result['part_type'] = part_type
                    result['intersection'] = intersection
    # if no match or no appliance family, check in category Other
    else:
        other_family = ApplianceFamily.objects.get(name__iexact = "Other")
        part_types = PartType.objects.filter(~in_blacklist_q, appliance_family = other_family).extra(select={'length':'Length(name)'}).order_by('length')
        for part_type in part_types:
            intersection = get_intersection(text_to_vector(part_type.name, 1.5) + text_to_vector(part_type.keywords), name_vector)
            if intersection and intersection > result['intersection']:
                result['part_type'] = part_type
                result['intersection'] = intersection

    return result





def part_type_from_name(name, appliance_family=None):
    if not name:return None
    result = {'cosine':0.0}
    name_vector = text_to_vector(name)


    # match with appliance type first if not already existing
    if not appliance_family:
        appliance_f_cos = 0
        appliances_f = ApplianceFamily.objects.all()
        for appliance_f in appliances_f:
            cosine = get_cosine(text_to_vector(appliance_f.name), name_vector)
            if cosine and cosine > appliance_f_cos:
                appliance_family = appliance_f
                appliance_f_cos = cosine



    if appliance_family:
        part_types = PartType.objects.filter(appliance_family = appliance_family)
    else:
        part_types = PartType.objects.all()
    for part_type in part_types:
        cosine = get_cosine(text_to_vector(part_type.name + " " + part_type.keywords), name_vector)
        if cosine and cosine > result['cosine']:
            result = {'part_type':part_type, 'appliance_family':part_type.appliance_family, 'cosine':cosine}
    return result


WORD = re.compile(r'\w+')

def get_intersection(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    # return len(intersection)
    return sum([vec1[key]*vec2[key] for key in intersection])


def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator

def text_to_vector(text, factor = 1):
    words = WORD.findall(text.lower())
    counter = Counter(words)
    counter = Counter({k:factor*v for k,v in counter.items()})
    return counter

def pretty_errors(error_list):
    for error in error_list:
        error.pop('find_techno_material', None)
        row_id = error.pop('row_index', None)
        if error:
            print 'row %s:'%row_id
            for key, value in error.items():
                print '\t%s: %s'%(key, value)


def parttypeDistrib(user):
    # part_types = PartType.objects.all().distinct()
    part_types = PartType.objects.all().values_list('name', flat=True).distinct()

    latest_bulk_upload = BulkPartUpload.objects.filter(created_by__organisation = user.organisation).order_by('-date_created').first()
    latest_bulk_upload = BulkPartUpload.objects.get(id=245)
    i=0
    with open('/home/thibault/Downloads/distributions.csv', 'wb+') as csvfile:
        fieldnames = ['part_type', 'count','min_weight',
                    'average_weight','max_weight','std_dev_weight',
                    'average_selling_volumes','min_selling_volumes','max_selling_volumes','std_dev_selling_volumes',
                    'average_selling_price','min_selling_price','max_selling_price','std_dev_selling_price']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for pt in part_types:
            result = Part.objects.filter(bulk_upload = latest_bulk_upload, type__name=pt).aggregate(
                count = Count('id'),
                average_weight = Avg('weight'),
                min_weight = Min('weight'),
                max_weight = Max('weight'),
                std_dev_weight = StdDev('weight'),
                average_selling_volumes = Avg('financial_card__selling_volumes'),
                min_selling_volumes = Min('financial_card__selling_volumes'),
                max_selling_volumes = Max('financial_card__selling_volumes'),
                std_dev_selling_volumes = StdDev('financial_card__selling_volumes'),
                average_selling_price = Avg('financial_card__selling_price'),
                min_selling_price = Min('financial_card__selling_price'),
                max_selling_price = Max('financial_card__selling_price'),
                std_dev_selling_price = StdDev('financial_card__selling_price')

            )
            result['part_type'] = pt
            # result['part_type'] = pt.name
            # result['appliance_family'] = pt.appliance_family.name
            writer.writerow(result)
            i += 1
            if i%50==1:print i


@transaction.atomic
def buildFakeDistrib(user):
    part_type_distrib = {}
    latest_bulk_upload = BulkPartUpload.objects.filter(created_by__organisation = user.organisation).order_by('-date_created').first()
    # latest_bulk_upload = BulkPartUpload.objects.get(id = 259)

    # import data
    fieldnames = ['part_type', 'count','min_weight',
                'average_weight','max_weight','std_dev_weight',
                'average_selling_volumes','min_selling_volumes','max_selling_volumes','std_dev_selling_volumes',
                'average_selling_price','min_selling_price','max_selling_price','std_dev_selling_price']

    with open('/home/thibault/Downloads/distributions.csv', 'rb+') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames = fieldnames)
        for index, row in enumerate(reader, start=1):
            if index == 1:continue
            part_type_distrib[row['part_type']] = row

    i = 0
    j = 0
    for name, distrib in part_type_distrib.iteritems():
        parts = Part.objects.filter(bulk_upload = latest_bulk_upload, type__name = name)
        STD_avg_weight = 70
        STD_min_weight = 5
        STD_avg_selling_price = 20
        STD_std_dev_selling_price = 10
        STD_average_selling_volumes = 30
        STD_std_dev_selling_volumes = 10
        # selling price
        if distrib.get('average_selling_price') and distrib.get('std_dev_selling_price'):
            avg_selling_price = round(float(distrib.get('average_selling_price')),1)
            std_dev_selling_price = round(float(distrib.get('std_dev_selling_price')),1)
            if not avg_selling_price or not std_dev_selling_price:
                avg_selling_price = STD_avg_selling_price
                std_dev_selling_price = STD_std_dev_selling_price
        else:
            avg_selling_price = STD_avg_selling_price
            std_dev_selling_price = STD_std_dev_selling_price

        # weight
        if distrib.get('average_weight', None) and distrib.get('min_weight', None):
            avg_weight = round(float(distrib.get('average_weight')),1)
            min_weight = round(float(distrib.get('min_weight')),1)
        else:
            avg_weight = None
            min_weight = None
        # selling volumes
        if distrib.get('average_selling_volumes').replace(" ", "") and distrib.get('std_dev_selling_volumes').replace(" ", ""):
            average_selling_volumes = int(float(distrib.get('average_selling_volumes')))
            std_dev_selling_volumes = int(float(distrib.get('std_dev_selling_volumes')))
            if not average_selling_volumes or not std_dev_selling_volumes:
                average_selling_volumes = STD_average_selling_volumes
                std_dev_selling_volumes = STD_std_dev_selling_volumes
        else:
            average_selling_volumes = STD_average_selling_volumes
            std_dev_selling_volumes = STD_std_dev_selling_volumes

    # update infos of parts
        for part in parts:
            i += 1
            if i%100==0:print i
            if avg_weight and min_weight:
                part.weight = round(random.uniform(min_weight, avg_weight),1)
                # part.save()

            if part.financial_card:
                f_card = part.financial_card
            else:
                f_card = FinancialCard()
                f_card.part = part
                j += 1

            f_card.selling_volumes = int(abs(normal(average_selling_volumes, std_dev_selling_volumes, 1)[0]))
            f_card.selling_price = round(abs(normal(avg_selling_price, std_dev_selling_price , 1)[0]),2)
            f_card.save()
            part.save()
            #
    print "TOTAL PARTS ADDED WEIGHT: %s"%i
    print "TOTAL PARTS FINANCIAL CARD CREATED: %s"%j
