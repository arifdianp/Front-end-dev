"""sp3d_quotation URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView
import quotation

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('quotation.urls')),
    url(r'^.well-known/pki-validation/872724DAD1C34D48C5E382EB1AF0D04A.txt$', quotation.views.dcv_verif, name='dcv_verif'),
    url(r'^robots.txt$',TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), name="robots_file"),
    url(r'^sitemap.xml$',TemplateView.as_view(template_name="sitemap.xml", content_type="text/xml"), name="sitemap"),
    url(r'^urllist.txt$',TemplateView.as_view(template_name="urllist.txt", content_type="text/plain"), name="urllist"),
]
