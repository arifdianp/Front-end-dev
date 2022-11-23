# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from .models import Quote, Model3D, Material, Bulk_Files, Quote_Form, Technology
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from django.template.loader import get_template
import ast
import os
import yaml
import urllib2
import requests
import json
import time
from quotation.decorators import postpone

from django.shortcuts import render, render_to_response, redirect
from datetime import datetime
from django.template import RequestContext, Context
from django.core.urlresolvers import reverse

S3_BUCKET = 'https://s3-ap-southeast-1.amazonaws.com/sp3dquotation/'
SLACK_WEBHOOK_SALES = 'https://hooks.slack.com/services/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'

# Create your views here.
def index(request):
    search = request.GET.get('search','No Search')
    techno_list = []
    technos_yaml = Technology.objects.all().order_by('-priority')
    for techno_yaml in technos_yaml:
        if techno_yaml.file_name in os.listdir('content/technos/'):
            techno = yaml.load(file("content/technos/%s"%techno_yaml.file_name, 'r'))
            techno['url_name'] = techno_yaml.url_name
            techno['id'] = techno_yaml.id
            techno_list.append(techno)

    context={
        'techno_list':techno_list,
    }
    # print request.scheme
    # print request.body
    # print request.content_params
    # pretty_dic(request.META)
    return render(request, 'quotation/index.html', context)

def quick_quote(request):
    search = request.GET.get('search','No Search')
    context={'search':search,}
    return render(request, 'quotation/quick-quote.html', context)

def quick_quote1(request):
    section = request.GET.get('section','')
    request_success = request.GET.get('request_success','')
    techno = request.GET.get('techno','')
    service = request.GET.get('service','')
    techno_list = Technology.objects.all()
    context = {
        'section':section,
        'techno':techno,
        'service':service,
        'request_success':request_success,
        'techno_list': techno_list,
        }
    
    return render(request, 'quotation/quick-quote1.html', context)

def standards(request):
    standards = []
    for filename in sorted(os.listdir('content/standards/')):
        if filename.rsplit(".",1)[1]=="yaml":
            standard = yaml.load(file("content/standards/%s"%filename, 'r'))
            standards.append(standard)
    # techno = yaml.load(urllib2.urlopen(S3_BUCKET + "media/private/content/technos/sls.yaml"))

    context={
        'standards':standards,
    }
    return render(request, 'quotation/standards.html', context)

def technologies(request, techno_url_name=None):
    # get specific techno requested
    try:
        _technology = Technology.objects.filter(url_name = techno_url_name).first()
        technology = yaml.load(file("content/technos/%s"%_technology.file_name, 'r'))
        technology['url_name'] = _technology.url_name
        technology['id'] = _technology.id
        technology['tag_description'] = _technology.tag_description
        technology['tag_title'] = _technology.tag_title
    except:
        technology = ""

    # get all technos in list:
    techno_list = []
    technos_yaml = Technology.objects.all().order_by('-priority')
    for techno_yaml in technos_yaml:
        if techno_yaml.file_name in os.listdir('content/technos/'):
            techno = yaml.load(file("content/technos/%s"%techno_yaml.file_name, 'r'))
            techno['url_name'] = techno_yaml.url_name
            techno['id'] = techno_yaml.id
            techno_list.append(techno)

    context={
        'techno':technology,
        'techno_list':techno_list,
    }
    return render(request, 'quotation/technologies.html', context)

def materials(request):
        # get specific techno requested
        material_requested = request.GET.get('material','')
        if material_requested:
            material = yaml.load(file("content/materials/%s.yaml"%material_requested, 'r'))
        else:
            material = ""

        # get all technos in list:
        material_list = []
        print "LIST MATERIALS"
        print sorted(os.listdir('content/materials/'))
        for filename in sorted(os.listdir('content/materials/')):
            if filename.rsplit(".",1)[1]=="yaml":
                material1 = yaml.load(file("content/materials/%s"%filename, 'r'))
                material_list.append(material1)

        context={
            'material':material,
            'material_list':material_list,
        }
        return render(request, 'quotation/materials.html', context)

def upload_files(request):
    if request.method == 'POST':
        file=request.FILES['model3d_file']
        print "FILE TYPE IS : %s"%type(file)
        form=request.POST
        # create a session key
        if not request.session.exists(request.session.session_key):
            request.session.create()
            request.session['quotation_pending']=True
        # session = request.session.keys()
        # session_e = request.session.get_expiry_date()
        # if request.session.session_key request.session.cycle_key()
        session_key = request.session.session_key


        file_extension = file.name.rsplit(".",1)[1].lower()
        new_model3d = Model3D.objects.create()
        # TODO: Change this path when transfer to AWS
        # file_path = os.path.join(S3_BUCKET,"models", "%s.%s"%(new_model3d.id,file_extension))
        new_model3d.file.save(file.name, file)
        # file_path = os.path.join("/home/user01/quote_project/sp3d_quotation/quotation/static/quotation/stl", "%s.%s"%(new_model3d.id,file_extension))
        # new_model3d.file_path = file_path
        # new_model3d.file_name = file.name
        new_model3d.save()

        # create quote if doesn't exist
        quotes = Quote.objects.filter(last_session_key = request.session.session_key).order_by("-creation_date")
        print "QUOTATION PENDING: %s"%request.session.get('quotation_pending',False)
        print "QUOTES ARE: %s"%quotes
        if quotes:
            quote = quotes[0]
        else:
            quote = Quote.objects.create(creation_date = datetime.now(), last_session_key=request.session.session_key)


        # store new_file ans update models3d attached to quote
        # with open(file_path, "w+") as f:
        #     for line in file:
        #         f.write(line)

        # update quote part list
        model_list = quote.list_models3d_quantity
        if model_list:
            model_list = ast.literal_eval(quote.list_models3d_quantity)
        else:
            model_list={}
        model_list[new_model3d.id]=1
        quote.list_models3d_quantity = "%s"%model_list
        quote.save()
        print "FILE URL IS: %s"%new_model3d.file.url
        print "FILE name IS: %s"%new_model3d.file.name
        print "FILE size IS: %s"%new_model3d.file.size
        print "FILE ID IS: %s"%new_model3d.id

        data= {
        "status_code":200,
        "result":"uploaded on server side",
        # TODO: Change filepath for migration to AWS
        # "filepath":"/static/quotation/stl/%s.%s"%(new_model3d.id,file_extension),
        "filepath":new_model3d.file.url,
        "filename":new_model3d.file.name,
        "filesize":new_model3d.file.size,
        "model_id":new_model3d.id,
        }
    return JsonResponse(data)

def send_quote_form(request):
    print "REQUEST ARRIVED"
    if request.method == 'POST':
        files = request.FILES.getlist('form-files')
        print files
        # save file in database
        files_list_string=""
        slack_file_links=""
        files_list=[]
        for file in files:
            new_bulk_file = Bulk_Files.objects.create()
            new_bulk_file.file.save(file.name, file)
            new_bulk_file.save()
            # increment slack message and db list
            slack_file_links = slack_file_links + "<%s|%s> + "%(new_bulk_file.file.url,new_bulk_file.file.name)
            files_list_string = files_list_string + "%s,"%new_bulk_file.id
            files_list.append(new_bulk_file.file.url)

        email = request.POST.get("email")
        contact = " (" + request.POST.get("defaultCountry") + "):  (+" + request.POST.get("carrierCode") + ") " + request.POST.get("phoneNumber")
        quantity = request.POST.get("quantity")
        process = request.POST.get("process")
        service = request.POST.get("service")
        request_type = request.POST.get("request-type")
        timeline = request.POST.get("timeline")
        details = request.POST.get("details")


        new_quote_request = Quote_Form.objects.create(email=email, contact=contact, request_type = request_type, service=service, quantity=quantity, process=process, timeline=timeline, details=details, id_bulk_files=files_list_string)

        # slack message
        header = "New Request from Quotation Website :muscle:"

        if request_type == "prototype":
            message = "New request from: %s\ncontact: %s\nrequest type:%s\nprocess: %s\nquantity:%s\ntimeline: %s\ndetails: %s\nfiles: %s"%(email, contact, request_type, process, quantity, timeline, details, slack_file_links)
        elif request_type == "service":
            message = "New request from: %s\ncontact: %s\nrequest type:%s\nservice: %s\nquantity:%s\ntimeline: %s\ndetails: %s\nfiles: %s"%(email, contact, request_type, service, quantity, timeline, details, slack_file_links)
        elif request_type == "contact":
            message = "New request from: %s\ncontact: %s\nrequest type:%s\ndetails: %s"%(email, contact, request_type, details)
        slack_message(SLACK_WEBHOOK_SALES, header, message, "#e33a3a")

        print "email:%s"%email
        print "contact:%s"%contact
        print "QUANTTY:%s"%quantity
        print "process:%s"%process
        print "timeline:%s"%timeline
        print "details:%s"%details
        print "quantity:%s"%quantity
        print "files_list_string:%s"%files_list_string

        send_email(
            'quotation/mail_templates/request_success.html',
            { 'email': email },
            'SP3D: Thank you for your request !',
            'service@sp3d.co',
            [email],
            )

        send_email(
            'quotation/mail_templates/request_info.html',
            { 'email': email,  'quantity':quantity, 'process':process, 'service':service, 'request_type':request_type, 'timeline':timeline, 'details':details , 'files_list':files_list},
            'New Prototyping request !',
            'service@sp3d.co',
            ['service@sp3d.co'],
            )

    return HttpResponseRedirect(reverse('quick-quote1') + '?request_success=1')




def handler404(request):
    response = render_to_response('404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response

def dcv_verif(request):
    return HttpResponse(open('872724DAD1C34D48C5E382EB1AF0D04A.txt').read())

def pretty_dic(dict):
    print "###############################################DIC BEGINS###################################################"
    for key, value in dict.iteritems():
        print "%s: %s"%(key,value)
    print "##############################################DIC ENDS#######################################################"

def slack_message(hook, header, message, color):
    slack_data = {
                        "text": header,
                        "attachments": [
                            {
                                "text": message,
                                "color": color,
                                "attachment_type": "default"
                            }
                        ]
                    }
    print "SENDING SLACK MESSAGE"
    slack_res = requests.post(hook, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})
    print "SLACK MESSAGE SENT"
    return True

@postpone
def send_email(html_path, context, subject, from_email, to):
    html = get_template(html_path)
    html_content = html.render(context)
    # plaintext = get_template('quotation/mail_templates/request_success.txt')
    # text_content = plaintext.render(context)
    # msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    # msg.attach_alternative(html_content, "text/html")
    msg = EmailMessage(subject, html_content, from_email, to=to, reply_to=[from_email])
    msg.content_subtype = 'html'
    # print "about to send email from %s" % from_email
    msg.send()
    # send email
    # send_mail(
    #     'Subject here',
    #     'Here is the message.',
    #     'thibault.de-saint-sernin@sp3d.co',
    #     ['thibault.de-laparre-de-saint-sernin@gadz.org'],
    #     fail_silently=False,
    #     )
    return True
