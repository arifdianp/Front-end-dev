# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
import os
from os.path import join
import numpy
from stl import mesh
from django.core import serializers
from django.db import connection
from django.db import transaction
from digital.forms import PartBulkFileForm, PartForm, CharacteristicsForm,\
                        PartImageForm, PartFiltersForm, PartColumnsForm, \
                        FinancialCardForm, ApplianceFamilyDetailsForm, Applianceformset
from users.forms import ProfilePicForm, OrganisationForm, ProfileForm, OrganisationLogoForm
from jb.forms import FinalCardForm
from django.core.files.uploadedfile import UploadedFile
from digital.utils import analysis_to_csv, UpdateFinancialAnalysis,margin_yearly_analysis,\
    upload_bulk_parts, getPartsClean, getBulkUploadSumUp, send_email, getPartSumUp, getfiledata,\
    translate_matrix, findTechnoMaterial, part_type_from_name, getApplianceFamilyDistribution, \
    parttypeDistrib, buildFakeDistrib, getPartCost
from django.contrib.auth.decorators import login_required
from django.conf import settings
import json
from notifications.signals import notify
from notifications.models import Notification
import datetime
# import locale
# import sys
# print(str(locale.getlocale()))
# print(str(locale.getdefaultlocale()))
# print(str(sys.getfilesystemencoding()))
# print(str(sys.getdefaultencoding()))
# print(str(sys.getdefaultencoding()))
from jb.models import Technology, Material
from digital.models import Part, PartImage,\
                            PartBulkFile, ClientPartStatus, PartEvent,\
                            Characteristics, PartType, BulkPartUpload, \
                            ApplianceFamily, ApplianceFamilyDetails, Catalogue
from users.models import CustomUser, Currency
from jb.models import FinalCard
dir_path = os.path.dirname(os.path.realpath(__file__))

# Create your views here.
@login_required
def dashboard(request):
    # buildFakeDistrib(request.user)
    # parttypeDistrib(request.user)
    parts_sumup, appliance_fam_distrib, parttype_distrib = getPartSumUp(**{'organisation':request.user.organisation})
    # family_ditribution = getApplianceFamilyDistribution(request.user.organisation)
    context = {
        'page':"dashboard",
        'parts_sumup':parts_sumup,
        # 'family_ditribution':json.dumps(list(family_ditribution)),
        'parttype_distrib':json.dumps(list(parttype_distrib)),
        'appliance_fam_distrib':json.dumps(list(appliance_fam_distrib)),
        'catalogues':Catalogue.objects.filter(organisation=request.user.organisation),
    }
    # total_parts_indus = Parts.objects.filter()
    return render(request, 'digital/dashboard.html', context)
@login_required
def account(request):
    team_members = CustomUser.objects.filter(organisation = request.user.organisation).exclude(pk = request.user.pk)
    currencies = Currency.objects.all()
    context = {
        'page':"account",
        'team_members':team_members,
        'formOrganisation':OrganisationForm(),
        'catalogues':Catalogue.objects.filter(organisation=request.user.organisation),
        'currencies': currencies,
    }
    return render(request, 'digital/account.html', context)

@login_required
def parts(request):
    # query parts, and add all images to a _image attribute in Part object for more query efficiency in template
    parts, page_number, pagination_range, nb_per_page, id_status, parts_sumup, appliance_fam_distrib, parttype_distrib = getPartsClean(request)
    stl_mesh = mesh.Mesh.from_file(join(dir_path, 'static', 'digital', 'stl', 'assemb6.STL'))
    volume, cog, inertia = stl_mesh.get_mass_properties()
    catalogue_id = request.GET.get('catalogue', None)
    try:
        catalogue = Catalogue.objects.get(organisation=request.user.organisation, id = catalogue_id)
    except:
        catalogue = None
    # print("Volume                                  = {0}".format(volume))
    # print("Position of the center of gravity (COG) = {0}".format(cog))
    # print("Inertia matrix at expressed at the COG  = {0}".format(inertia[0,:]))
    # print("                                          {0}".format(inertia[1,:]))
    # print("                                          {0}".format(inertia[2,:]))
    context = {
        'page':"parts",
        'parts':parts,
        'id_status':id_status,
        'page_number':page_number,
        'pagination_range':pagination_range,
        'nb_per_page':nb_per_page,
        'parts_sumup':parts_sumup,
        'formPartBulkFile': PartBulkFileForm(),
        'PartImageForm': PartImageForm(),
        'formPart': PartForm(created_by=request.user),
        'formCharacteristics': CharacteristicsForm(initial={'min_temp':0,'max_temp':70}),
        'formFilters':PartFiltersForm(user=request.user),
        'formColumns':PartColumnsForm(user=request.user),
        'FinancialCardForm':FinancialCardForm(),
        'formFinalCard':FinalCardForm(),
        'clientPartStatuses':ClientPartStatus.objects.all().order_by('id'),
        'search_string':request.GET.get('search', ''),
        'catalogues':Catalogue.objects.filter(organisation=request.user.organisation),
        'catal':catalogue,
    }
    return render(request, 'digital/parts.html', context)


@login_required
def billing(request):
    context = {
        'page':"billing",
    }
    return render(request, 'digital/billing.html', context)


@login_required
def analysis(request):
    if request.GET.get('redirection',None):
        saveRequestFilters(request.user, request.GET)
        print request.GET.get('catalogue')
        # return redirect('digital.digital_parts')
        return HttpResponseRedirect("/digital/parts/?catalogue=%s"%request.GET.get('catalogue',''))
    # buildFakeDistrib(request.user)
    # id_catalogue = request.GET.get('catalogue', None)
    # if not id_catalogue:
    #     id_catalogue = request.user.organisation.catalogue_set.first().id
    #     return HttpResponseRedirect("?catalogue=%s"%id_catalogue)
    parts_sumup, parttype_distrib, appliance_fam_distrib, techno_material_distrib, latest_upload, obsolete_margin_5y, longtail_margin_5y, pex_margin, shortage_margin, catalogue = getBulkUploadSumUp(request)

    appliances = ApplianceFamily.objects.filter(industry__in = request.user.organisation.industry.all()).exclude(organisation_details = request.user.organisation).order_by('name')
    initial = []
    for appliance in appliances:
        dic = {}
        dic['appliance_family'] = appliance
        dic['retail_price'] = 0
        initial.append(dic)
    formset1 = Applianceformset(
                        queryset = ApplianceFamilyDetails.objects.filter(organisation = request.user.organisation),
                        form_kwargs={'organisation': request.user.organisation},
                        initial = initial
                        )
    formset1.extra = len(appliances)
    context = {
        'page':"analysis",
        'parts_sumup':parts_sumup,
        'parttype_distrib':json.dumps(list(parttype_distrib)),
        'appliance_fam_distrib':json.dumps(list(appliance_fam_distrib)),
        'techno_material_distrib':json.dumps(list(techno_material_distrib)),
        'obsolete_margin_5y': obsolete_margin_5y,
        'longtail_margin_5y':longtail_margin_5y,
        'pex_margin':pex_margin,
        'shortage_margin':shortage_margin,
        'latest_upload':latest_upload,
        'Applianceformset':formset1,
        'catalogues':Catalogue.objects.filter(organisation=request.user.organisation),
        'catalogue':catalogue,
    }
    return render(request, 'digital/analysis.html', context)

@login_required
def table(request):
    context = {
        'page':"table",
    }
    return render(request, 'digital/table.html', context)

@login_required
def typography(request):
    context = {
        'page':"typography",
    }
    return render(request, 'digital/typography.html', context)

@login_required
def icons(request):
    context = {
        'page':"icons",
    }
    return render(request, 'digital/icons.html', context)

@login_required
def maps(request):
    context = {
        'page':"maps",
    }
    return render(request, 'digital/maps.html', context)

@login_required
def notifications(request):
    notifications = Notification.objects.filter(recipient=request.user)
    notifications_sent = Notification.objects.filter(actor_content_type__model="customuser",actor_object_id = request.user.id )
    context = {
        'page':"notifications",
        'notifications':notifications,
        'notifications_sent':notifications_sent,
        'catalogues':Catalogue.objects.filter(organisation=request.user.organisation),
    }
    return render(request, 'digital/notifications.html', context)

@login_required
def new_catalogue(request):
    if request.method == 'POST':
        name = request.POST.get('catalogue-name', None)
        if name:
            new_catalogue = Catalogue.objects.create(organisation=request.user.organisation, name = name)
            return redirect('/digital/parts/?catalogue=%s'%new_catalogue.id)
    return redirect('/digital/parts/')


@login_required
@transaction.atomic
def delete_catalogue(request):
    if request.method == 'POST':
        id_catalogue = request.POST.get('id-catalogue', None)
        try:
            catalogue = Catalogue.objects.get(organisation=request.user.organisation, id=id_catalogue)
        except:
            return redirect('digital.digital_parts')
        start = datetime.datetime.now()
        catalogue.delete()
        end = datetime.datetime.now()
        print 'delete_recommendations took {}s'.format(end - start)
        return redirect('digital.digital_parts')
    return redirect('digital.digital_parts')

@login_required
def qualification(request):
    context = {
        'page':"qualification",
    }
    return render(request, 'digital/qualification.html', context)


@login_required
def upload_part_bulk_file(request):
    if request.method == 'POST':
        # initialize default values
        success = True
        errors = []
        files_success=[]
        files_failure=[]
        print 'debug5'
        print request.POST
        print request.FILES
        if request.FILES == None:
            success = False
            errors.append("No files attached")
        else:
            for _file in request.FILES.getlist('file'):
                request.FILES['file'] = _file
                form = PartBulkFileForm(request.POST, request.FILES, created_by=request.user)
                if form.is_valid():
                    print "FORM IS VALID"
                    type, data = getfiledata(_file)
                    print 'debug3'
                    _new_file = form.save(type= type, data = data)
                    files_success.append({"name":(_new_file.file.name).rsplit("/",1)[1], "url":_new_file.file.url, 'id':_new_file.id, 'type':_new_file.type, 'data':_new_file.data})
                    print 'debug4'
                else:
                    print "FORM IS NOT VALID"
                    files_failure.append({"name":_file})
                    success = False
                    errors.append("form with file %s is not valid"%_file)
        data={
            "success":success,
            "errors":errors,
            "files_success":files_success,
            "files_failure":files_failure,
            "id_part": request.POST["part"],
            }
        return JsonResponse(data)

    return HttpResponseRedirect("/digital/parts/")




@login_required
def upload_part_image(request):
    if request.method == 'POST':
        # initialize default values
        success = True
        errors = []
        images_success=[]
        images_failure=[]
        print request.POST
        print request.FILES
        if request.FILES == None:
            success = False
            errors.append("No files attached")
        else:
            for _image in request.FILES.getlist('image'):
                request.FILES['file'] = _image
                form = PartImageForm(request.POST, request.FILES, created_by=request.user)
                if form.is_valid():
                    print "FORM IS VALID"
                    _new_image = form.save()
                    images_success.append({"name":(_new_image.image.name).rsplit("/",1)[1], "url":_new_image.image.url, 'id':_new_image.id})
                else:
                    print "FORM IS NOT VALID"
                    images_failure.append({"name":_image})
                    success = False
                    errors.append("form with file %s is not valid"%_image)
        data={
            "success":success,
            "errors":errors,
            "images_success":images_success,
            "images_failure":images_failure,
            "id_part": request.POST["part"],
            }
        return JsonResponse(data)

    return HttpResponseRedirect("/digital/parts/")






@login_required
def upload_profile_pic(request):
    if request.method == 'POST':
        # initialize default values
        success = True
        errors = []
        thumbnail=''
        print request.POST
        print request.FILES
        _file = request.FILES.get('profile_pic', False)
        if request.FILES == None and _file:
            success = False
            errors.append("No files attached")
        else:
            form = ProfilePicForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                print "FORM IS VALID"
                _user = form.save()
                thumbnail = _user.profile_thumb.url
            else:
                print "FORM IS NOT VALID"
                success = False
                errors.append("form with file %s is not valid"%_image)
        data={
            "success":success,
            "errors":errors,
            "thumbnail":thumbnail,
            }
        return JsonResponse(data)

    return HttpResponseRedirect("/digital/account/")



@login_required
def upload_company_logo(request):
    if request.method == 'POST':
        # initialize default values
        success = True
        errors = []
        thumbnail=''
        print request.POST
        print request.FILES
        _file = request.FILES.get('company_logo', False)
        if request.FILES == None and _file:
            success = False
            errors.append("No files attached")
        else:
            form = OrganisationLogoForm(request.POST, request.FILES, instance=request.user.organisation)
            if form.is_valid():
                print "FORM IS VALID"
                _organisation = form.save()
                thumbnail = _organisation.logo.url
            else:
                print "FORM IS NOT VALID"
                success = False
                errors.append("form with file %s is not valid"%_image)
        data={
            "success":success,
            "errors":errors,
            "thumbnail":thumbnail,
            }
        return JsonResponse(data)

    return HttpResponseRedirect("/digital/account/")




@login_required
def delete_bulk_file(request):
        success=True
        errors=[]
        id_file = request.GET.get("id_file")
        file = PartBulkFile.objects.get(id=id_file)
        if file.part.organisation == request.user.organisation:
            file.delete()
        else:
            success=False
            errors.append("this file does not belong to your organisation")
        data={
            "success":success,
            "errors":errors,
            }
        return JsonResponse(data)

@login_required
def request_for_indus(request):
    success=True
    errors=[]
    id_part = request.GET.get("id_part")
    part = Part.objects.get(id=id_part)
    if part.organisation == request.user.organisation:
        pendingStatus = ClientPartStatus.objects.get(id=2)
        part.status = pendingStatus
        part.save()
        if not settings.DEBUG:
            send_email(
                'digital/mail_templates/rfi.html',
                { 'user': request.user, 'part':part },
                'SP3D: New Industrialisation Request',
                'contact@sp3d.co',
                ['paul.de-misouard@sp3d.co','paul.guillaumot@sp3d.co','thibault.de-saint-sernin@sp3d.co'],
                )
        new_event = PartEvent.objects.create(
            part=part,
            created_by = request.user,
            type="STATUS_CHANGE",
            status = part.status,
            short_description = "status changed to %s"%part.status.name,
            long_description = "The part has been changed to status: %s, and will be reviewed by our team. We will get back to you ASAP"%part.status.name
        )
    else:
        success=False
        errors.append("this part does not belong to your organisation")
    data={
        "success":success,
        "errors":errors,
        }
    return JsonResponse(data)

@login_required
def change_part_status(request):
    success=True
    errors=[]
    id_part = request.GET.get("id_part")
    id_status = request.GET.get("id_status")
    part = Part.objects.get(id=id_part)
    new_status = ClientPartStatus.objects.get(id=id_status)
    if part.organisation == request.user.organisation:
        if not part.status == new_status:
            if new_status == 3 or new_status == 4:
                part.notify_status_to_client = True
            part.status = new_status
            part.save()
            if not settings.DEBUG:
                send_email(
                    'digital/mail_templates/status_change.html',
                    { 'user': request.user, 'part':part },
                    'SP3D: Client Part - Status Change',
                    'contact@sp3d.co',
                    ['paul.de-misouard@sp3d.co','paul.guillaumot@sp3d.co','thibault.de-saint-sernin@sp3d.co'],
                    )
            new_event = PartEvent.objects.create(
                part=part,
                created_by = request.user,
                type="STATUS_CHANGE",
                status = part.status,
                short_description = "status changed to %s"%part.status.name,
                long_description = "The part has been changed to status: %s, and will be reviewed by our team. We will get back to you ASAP"%part.status.name
            )
    else:
        success=False
        errors.append("this part does not belong to your organisation")
    data={
        "success":success,
        "errors":errors,
        }
    return JsonResponse(data)

@login_required
def send_recap_mail(request):
    success=True
    errors=[]
    parts = Part.objects.filter(organisation = request.user.organisation, notify_status_to_client = True).order_by('date')
    email_list = CustomUser.objects.filter(organisation = request.user.organisation).values_list('email', flat=True)
    send_email(
        'digital/mail_templates/client_update_status.html',
        { 'user': request.user, 'parts':parts },
        'Update on your Parts',
        'contact@sp3d.co',
        list(email_list),
        )
    parts.update(notify_status_to_client = False)
    data={
        "success":success,
        "errors":errors,
        }
    return JsonResponse(data)

@login_required
def get_part_history(request):
    success=True
    errors=[]
    id_part = request.GET.get("id_part")
    part = Part.objects.get(id=id_part)
    if part.organisation == request.user.organisation:
        events = PartEvent.objects.filter(part = part).order_by('date')
    else:
        success=False
        errors.append("this part does not belong to your organisation")
    data={
        "success":success,
        "errors":errors,
        "events":serializers.serialize('json', events, use_natural_foreign_keys=True),
        }
    return JsonResponse(data)

@login_required
def new_part(request):
    if request.method == 'POST':
        # initialize default values
        success = True
        errors = []
        part=None
        print request.POST
        form = PartForm(request.POST, created_by=request.user)
        form_charac = CharacteristicsForm(request.POST)
        if not form.is_valid():
            print "Part form is not valid"
        if not form_charac.is_valid():
            print "Charac form is not valid"
        if all((form.is_valid(), form_charac.is_valid())):
            _characteristics = form_charac.save()
            print "ALL FORMS ARE VALID"
            _new_part = form.save(characteristics = _characteristics)
            _new_part = findTechnoMaterial(_new_part, fallback_mode=False)
            _new_part = UpdateFinancialAnalysis(_new_part, **{'refreshing':True})
            part = serializers.serialize("json", [_new_part],  use_natural_foreign_keys=True)[1:-1]
        else:
            print "FORM IS NOT VALID"
            success = False
            errors.append("form is not valid")
        data={
            "success":success,
            "errors":errors,
            "part":part,
            }
        return JsonResponse(data)

    return HttpResponseRedirect("/digital/parts/")

@login_required
def update_part_card(request):
    if request.method == 'POST':
        # initialize default values
        success = True
        errors = []
        new_part = None
        part = Part.objects.get(id=request.POST.get("id_part"))
        if part.organisation == request.user.organisation:
            print request.POST
            form = PartForm(request.POST, created_by = request.user, instance = part)
            if part.characteristics is None:
                form_charac = CharacteristicsForm(request.POST)
            else:
                form_charac = CharacteristicsForm(request.POST, instance=part.characteristics)
            if form.is_valid():
                print "PART FORM IS VALID"
                # if characteristics attached save charac, otherwise remove them
                if form_charac.is_valid():
                    print "CHARAC FORM IS VALID"
                    _characteristics = form_charac.save()
                    _new_part = form.save(characteristics = _characteristics)
                else:
                    print "CHARAC FORM IS NOT VALID"
                    _new_part = form.save()
                    if _new_part.characteristics:
                        _new_part.characteristics.delete()
                        _new_part.characteristics = None
                        _new_part.save() #important because triggers final card removal in case no characteristics
                _new_part = findTechnoMaterial(_new_part, fallback_mode=False)
                _new_part = UpdateFinancialAnalysis(_new_part, **{'refreshing':True})
                new_part = serializers.serialize("json", [_new_part],  use_natural_foreign_keys=True)[1:-1]
            else:
                print "PART FORM IS NOT VALID"
                success = False
                errors.append("form is not valid")
        else:
            print "NOT RIGHT ORGANISATION OR PART"
            success = False
            errors.append("Part doesn't belong to Organisation")

        data={
            "success":success,
            "errors":errors,
            "part":new_part,
            }
        return JsonResponse(data)

    return HttpResponseRedirect("/digital/parts/")

@login_required
def update_final_card(request):
    if request.method == 'POST':
        success = True
        errors = []
        print request.POST
        print request.POST["id_part"]
        part = Part.objects.get(id=request.POST.get("id_part"))
        if part.organisation == request.user.organisation:
            if part.final_card is None:
                form = FinalCardForm(request.POST)
                if form.is_valid():
                    _final_card = form.save()
                    part.final_card = _final_card
                    part.save()
                else:
                    success = False
                    errors.append("Form is not Valid Step 1")
            else:
                form = FinalCardForm(request.POST, instance=part.final_card)
                if form.is_valid():
                    _final_card= form.save()
                else:
                    success = False
                    errors.append("Form is not Valid Step 2")
            final_card = serializers.serialize("json", [_final_card],  use_natural_foreign_keys=True)[1:-1]
        else:
            print "NOT RIGHT ORGANISATION OR PART"
            success = False
            errors.append("Part doesn't belong to Organisation")

        data={
            "success":success,
            "errors":errors,
            "final_card":final_card,
            }
        return JsonResponse(data)

    return HttpResponseRedirect("/digital/parts/")



@login_required
def update_profile(request):
    if request.method == 'POST':
        success = True
        errors = []
        print request.POST
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
        else:
            success = False
            errors.append("Form not valid")
        data={
            "success":success,
            "errors":errors,
            }
        return JsonResponse(data)
    return HttpResponseRedirect("/digital/account/")


@login_required
def update_organisation(request):
    if request.method == 'POST':
        success = True
        errors = []
        print request.POST
        form = OrganisationForm(request.POST, instance=request.user.organisation)
        if form.is_valid():
            form.save()
        else:
            success = False
            errors.append("Form not valid")
        data={
            "success":success,
            "errors":errors,
            }
        return JsonResponse(data)
    return HttpResponseRedirect("/digital/account/")



@login_required
def upload_solution_matrix(request):
    if request.method == 'POST' and request.user.is_staff:
        # initialize default values
        success = True
        errors = []
        warnings=[]
        print request.POST
        print request.FILES
        if request.FILES == None:
            success = False
            errors.append("No files attached")
        else:
            filename, file_extension = os.path.splitext('%s'%request.FILES.get('file'))
            errors, warnings = translate_matrix(request.FILES.get('file'))
            print "errors: %s"%errors
        data={
            "success":success,
            "errors":errors,
            "warnings":warnings,
            }
        return JsonResponse(data)

    return HttpResponseRedirect("/digital/parts/")



@login_required
def get_characteristics(request):
    if request.method == 'POST':
        # initialize default values
        success = True
        errors = []
        characteristics = None
        if request.POST.get('id_type', None):
            part_type = get_object_or_404(PartType, id = request.POST.get('id_type'))
            if part_type.characteristics:
                characteristics = part_type.characteristics.natural_key()
            else:
                success = False
                errors.append("NO CHARACTERISTICS ATTACHED TO PART TYPE")
        else:
            success=False
            errors.append("NO ID_TYPE IN REQUEST")

        data={
            "success":success,
            "errors":errors,
            'characteristics':characteristics,
        }
        return JsonResponse(data)

    return HttpResponseRedirect("/digital/parts/")


@login_required
def get_part_type(request):
    if request.method == 'POST':
        # initialize default values
        success = True
        errors = []
        id_part_type = None
        id_appliance_family = None
        characteristics = None
        if request.POST.get('part_name', None):
            part_type = part_type_from_name(request.POST.get('part_name'))
            if part_type:
                id_part_type = part_type['part_type'].id
                id_appliance_family = part_type['part_type'].appliance_family.id
                characteristics = part_type['part_type'].characteristics.natural_key()
            else:
                success=False
                errors.append("PAR NAME DID NOT MATCH ANY PART")
        else:
            success=False
            errors.append("NO PART_NAME IN REQUEST")

        data={
            "success":success,
            "errors":errors,
            'id_part_type':id_part_type,
            'id_appliance_family':id_appliance_family,
            'characteristics':characteristics,
        }
        return JsonResponse(data)

    return HttpResponseRedirect("/digital/parts/")





@login_required
def team_notification(request):
    if request.method == 'POST':
        # initialize default values
        data={
            "success":True,
            "errors":[],
        }
        id_recipient = request.POST.get('notif-recipient',None)
        verb = request.POST.get('notif-verb',None)
        level = request.POST.get('notif-level',None)
        description = request.POST.get('notif-description',None)
        if id_recipient:
            try:
                recipient = CustomUser.objects.get(id=id_recipient)
                if not recipient.organisation == request.user.organisation:
                    data["success"] = False
                    data["errors"].append("This person is NOT in your team")
                    return JsonResponse(data)
            except CustomUser.DoesNotExist:
                data["success"] = False
                data["errors"].append("Reciptent does not exist in database")
                return JsonResponse(data)


        if recipient and verb and description and level:
            notify.send(
                request.user,
                recipient = recipient,
                verb = verb,
                # action_object= new_order,
                # target = new_order,
                level=level,
                description=description,
                public = False,
                # target_path = "/jb/orders/order-detail/%s/"%new_order.id,
                # quantity=2
            )
            success = True
        else:
            success = False
            errors.append("Some information is missing or other error")

        return JsonResponse(data)
    return HttpResponseRedirect("/digbuildFakeDistribital/parts/")





@login_required
def mark_notif_as_read(request):
    try:
        id_notif = request.GET.get('id_notif', None)
        notif = Notification.objects.get(id=id_notif)
        print "notif: %s"%notif
        notif.mark_as_read()
        data = {
            "success": "notification %s marked as read successfully"%notif.id
        }
    except ValueError as err:
        data = {
            "error": err
        }
    except Exception as e:
        data = {
            "error": "%s"%e
        }
    return JsonResponse(data)




@login_required
def bulk_parts_upload(request):
    if request.method == 'POST' and request.user.is_admin:
        # initialize default values
        data={
            "success":True,
            "errors":[],
            "warnings":[],
        }
        kwargs = {}
        kwargs['repricing'] = request.POST.get('repricing', False)
        kwargs['analysis-type'] = request.POST.get('analysis-type', None)
        kwargs['catalogue-id'] = request.POST.get('catalogue-id', None)
        if not request.FILES.get('file', None):
            data["success"] = False
            data["errors"].append("No files attached, or wrong file input name")
        else:
            upload_bulk_parts(request.FILES.get('file'), request.user, **kwargs)

        data['catalogue'] = kwargs['catalogue-id']
        return JsonResponse(data)

    return HttpResponseRedirect("/digital/analysis/")



@login_required
def yearly_margin_analysis(request):
    if request.method == 'POST':
        errors = []
        data={
            "success":True,
            "errors":[],
            "warnings":[],
            'yearly_margin_list':[],
        }
        kwargs = {}
        data['currency'] = request.user.currency.sign
        try:
            volume_decrease_rate = request.POST.get('decrease-rate', None)
            volume_decrease_rate = float(volume_decrease_rate)/100
            if volume_decrease_rate<0:raise Exception
        except:
            errors.append("decrease rate is not as expected")

        id_part = request.POST.get('id_part', None)
        if id_part:
            kwargs['id_part'] = id_part

        yearly_margin_list = margin_yearly_analysis(request, **kwargs)
        data['yearly_margin_list'] = yearly_margin_list

        return JsonResponse(data)
    return HttpResponseRedirect("/digital/analysis/")


@login_required
@transaction.atomic
def refresh_financial_analysis(request):
    query_begin = len(connection.queries)
    id_cat = request.GET.get("catalogue", None)
    try:
        catalogues = Catalogue.objects.filter(organisation = request.user.organisation, id = id_cat)
    except:
        catalogues = Catalogue.objects.filter(organisation = request.user.organisation)

    data={
        "success":True,
        "errors":[],
        "warnings":[],
    }
    latest_bulk_upload = BulkPartUpload.objects.filter(created_by__organisation = request.user.organisation).order_by('-date_created').first()
    parts = Part.objects\
        .filter(organisation = request.user.organisation, catalogue__in = catalogues)\
        .select_related('financial_card', 'final_card', 'final_card__techno_material', 'organisation__financial_settings', 'type__appliance_family')
    i = 0
    for part in parts.iterator():
        # print "DB REQUEST A1: %s"%len(connection.queries)
        i += 1
        print i
        UpdateFinancialAnalysis(part, **{'refreshing':True})
        # print "SIZE: %s"%len(connection.queries)
        # print connection.queries
    print "DB REQUEST BEGINNING: %s"%query_begin
    print "DB REQUEST END: %s"%len(connection.queries)
    return JsonResponse(data)



@login_required
def export_analysis(request):
    data={
        "success":True,
    }
    catalogue = request.GET.get('catalogue', None)
    export = analysis_to_csv(request.user, catalogue)
    if export:
        data['file']=export.file.url
    else:
        data['success']=False
    return JsonResponse(data)

@login_required
def get_analysis_status(request):
    data={
        "finished":False,
        "analysed_parts":0,
    }
    latest_bulk_upload = BulkPartUpload.objects.filter(created_by__organisation = request.user.organisation).order_by('-date_created').first()
    if latest_bulk_upload:
        data['finished'] = latest_bulk_upload.finished
        data['analysed_parts'] = latest_bulk_upload.finished_entries
    return JsonResponse(data)



@login_required
def update_filters(request):
    data={
        "success":False,
    }
    if request.method == 'POST':
        form_filters = PartFiltersForm(request.POST, user = request.user)
        if form_filters.is_valid():
            form_filters.save()
            data['success']=True
        else:
            print "FILTERS FORM NOT VALID"
    return JsonResponse(data)
    # return HttpResponseRedirect("/digital/parts/?catalogue=%s"%request.POST.get('catalogue', ''))



@login_required
def update_appliance_prices(request):
    if request.method == 'POST':
        data = {
            'success' : True,
        }
        formset = Applianceformset(request.POST, form_kwargs={'organisation': request.user.organisation})
        # print request.POST
        # print formset.is_valid()
        # print formset.cleaned_data
        if formset.is_valid():
            formset.save()
        else:
            print "FORM NOT VALID"
        return JsonResponse(data)
    return HttpResponseRedirect("/digital/analysis/")



@login_required
def update_columns(request):
    if request.method == 'POST':
        print request.POST
        form_columns = PartColumnsForm(request.POST, user = request.user)
        if form_columns.is_valid():
            form_columns.save()
        else:
            print "COLUMN FORM NOT VALID"
    return HttpResponseRedirect("/digital/parts/?catalogue=%s"%request.POST.get('catalogue',''))


@login_required
def test_unit_cost(request):
    data = {
        'unit_cost':None,
    }
    if request.method == 'POST':
        yearly_volume = request.POST.get('yearly_volume', None)
        id_part = request.POST.get('id_part', None)
        print request.POST
        print id_part
        print yearly_volume
        if yearly_volume and id_part:
            part=None
            try:
                part = Part.objects.get(organisation = request.user.organisation, id = id_part)
            except Exception as e:
                print "part not found"
                print e
            if part:
                unit_cost = getPartCost(part, yearly_volume)
                if unit_cost: unit_cost = round(getPartCost(part, yearly_volume) * request.user.currency.rate,2)
                data['unit_cost'] = unit_cost
    return JsonResponse(data)

def saveRequestFilters(user, dic):
    if hasattr(user, 'part_filters'):
        filters = user.part_filters
    else:
        filters = UserPartFilter.objects.create(user = user)
    # reset filters first
    filters.reset()

    # look for filters in dic
    appliance = dic.get('appliance', None)
    technology = dic.get('technology', None)
    material = dic.get('material', None)
    parttype = dic.get('parttype', None)
    identified = dic.get('identified', None)
    reorder = dic.get('restock', None)
    printable = dic.get('printable', None)
    obsolete = dic.get('obsolete', None)
    longtail = dic.get('longtail', None)
    shortage = dic.get('shortage', None)
    pex = dic.get('pex', None)

    filters.analysis = "ALL"
    if appliance:
        appliance_list = appliance.split('--')
        appliance_list = list(ApplianceFamily.objects.filter(industry__in = user.organisation.industry.all(), name__in = appliance_list).values_list("id",flat=True))
        filters.appliance_list = "%s"%appliance_list
    if parttype:
        parttype_list = list(PartType.objects.filter(appliance_family__industry__in = user.organisation.industry.all(), name = parttype).distinct().values_list('name',flat=True))
        filters.parttype_list = "%s"%parttype_list
    if technology:
        technology_list = technology.split('--')
        technology_list = list(Technology.objects.filter(name__in = technology_list).values_list("id",flat=True))
        filters.technology_list = "%s"%technology_list
    if material:
        material_list = material.split('--')
        material_list = list(Material.objects.filter(name__in = material_list).values_list("id",flat=True))
        filters.material_list = "%s"%material_list
    if identified:
        filters.printable = 'IDENTIFIED'
    if printable:
        filters.printable = 'PRINTABLE'
    if reorder:
        filters.reorder = '[1,2,3,4,5]'
    if obsolete:
        filters.obsolete = True
    if longtail:
        filters.longtail = True
    if shortage:
        filters.shortage = True
    if pex:
        filters.pex = True

    filters.save()




def pretty_errors(error_list):
    for error in error_list:
        error.pop('find_techno_material', None)
        row_id = error.pop('row_index', None)
        if error:
            print 'row %s:'%row_id
            for key, value in error.items():
                print '\t%s: %s'%(key, value)

@transaction.atomic
def transfer_part_type(appliance_family_name, from_name, to_name =None):
    if to_name:
        new_type = PartType.objects.get(name=to_name, appliance_family__name = appliance_family_name)
    else:
        new_type = None
    parts = Part.objects.filter(type__appliance_family__name = appliance_family_name, type__name=from_name)
    i=0
    for part in parts:
        part.type = new_type
        part.save()
        if part.final_card:
            part.final_card.delete()
        if part.financial_card:
            part.financial_card.delete()
        i += 1
        print i
    print "TOTAL PARTS MODIFIED: %s"%i
