from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^quick-quote/$', views.quick_quote, name='quick-quote'),
    url(r'^quick-quote1/$', views.quick_quote1, name='quick-quote1'),
    url(r'^upload-files/$', views.upload_files, name='upload-files'),
    url(r'^technologies/$', views.technologies , name="technologies"),
    url(r'^technologies/(?P<techno_url_name>[^/]+)/$', views.technologies , name="technology_detail"),
    url(r'^materials/$', views.materials , name="materials"),
    url(r'^standards/$', views.standards , name="standards"),
    url(r'^send-quote-form/$', views.send_quote_form , name="send_quote_form"),



]
