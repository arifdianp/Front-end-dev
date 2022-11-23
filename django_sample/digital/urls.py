# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

app_name = 'digital_'
urlpatterns = [

    url(r'^$', views.dashboard, name=app_name + 'dashboard'),
    url(r'^account/$', views.account, name=app_name+'account'),
    url(r'^account/upload-profile-pic/$', views.upload_profile_pic, name=app_name+'upload_profile_pic'),
    url(r'^account/upload-company-logo/$', views.upload_company_logo, name=app_name+'upload_company_logo'),
    url(r'^account/update-profile/$', views.update_profile, name=app_name+'update_profile'),
    url(r'^account/update-organisation/$', views.update_organisation, name=app_name+'update_organisation'),
    url(r'^qualification/$', views.qualification, name=app_name+'qualification'),
    url(r'^parts/$', views.parts, name=app_name+'parts'),
    url(r'^parts/upload-part-bulk-file/$', views.upload_part_bulk_file, name=app_name+'upload_part_bulk_file'),
    url(r'^parts/upload-part-image/$', views.upload_part_image, name=app_name+'upload_part_image'),
    url(r'^parts/delete-bulk-file/$', views.delete_bulk_file, name=app_name+'delete_bulk_file'),
    url(r'^parts/request-for-indus/$', views.request_for_indus, name=app_name+'request_for_indus'),
    url(r'^parts/change-part-status/$', views.change_part_status, name=app_name+'change_part_status'),
    url(r'^parts/get-part-history/$', views.get_part_history, name=app_name+'get_part_history'),
    url(r'^parts/new-part/$', views.new_part, name=app_name+'new_part'),
    url(r'^parts/send-recap-mail/$', views.send_recap_mail, name=app_name+'send_recap_mail'),
    url(r'^parts/update-final-card/$', views.update_final_card, name=app_name+'update_final_card'),
    url(r'^parts/update-part-card/$', views.update_part_card, name=app_name+'update_part_card'),
    url(r'^parts/get-characteristics/$', views.get_characteristics, name=app_name+'get_characteristics'),
    url(r'^parts/get-part-type/$', views.get_part_type, name=app_name+'get_part_type'),
    url(r'^parts/update-filters/$', views.update_filters, name=app_name+'update_filters'),
    url(r'^parts/update-columns/$', views.update_columns, name=app_name+'update_columns'),
    url(r'^parts/delete-catalogue/$', views.delete_catalogue, name=app_name+'delete_catalogue'),
    url(r'^parts/test-unit-cost/$', views.test_unit_cost, name=app_name+'test_unit_cost'),
    url(r'^upload-solution-matrix/$', views.upload_solution_matrix, name=app_name+'upload_solution_matrix'),
    url(r'^billing/$', views.billing, name=app_name+'billing'),
    url(r'^table/$', views.table, name=app_name+'table'),
    url(r'^notifications/$', views.notifications, name=app_name+'notifications'),
    url(r'^notifications/mark-as-read/$', views.mark_notif_as_read, name=app_name+'mark_notif_as_read'),
    url(r'^notifications/team-notification/$', views.team_notification, name=app_name+'team_notification'),
    url(r'^typography/$', views.typography, name=app_name+'typography'),
    url(r'^icons/$', views.icons, name=app_name+'icons'),
    url(r'^maps/$', views.maps, name=app_name+'maps'),
    url(r'^analysis/$', views.analysis, name=app_name+'analysis'),
    url(r'^analysis/bulk-part-upload/$', views.bulk_parts_upload, name=app_name+'bulk_parts_upload'),
    url(r'^analysis/yearly-margin-analysis/$', views.yearly_margin_analysis, name=app_name+'yearly_margin_analysis'),
    url(r'^analysis/refresh-financial-analysis/$', views.refresh_financial_analysis, name=app_name+'refresh_financial_analysis'),
    url(r'^analysis/export-analysis/$', views.export_analysis, name=app_name+'export_analysis'),
    url(r'^analysis/analysis-status/$', views.get_analysis_status, name=app_name+'get_analysis_status'),
    url(r'^analysis/update-appliance-prices/$', views.update_appliance_prices, name=app_name+'update_appliance_prices'),
    url(r'^new-catalogue/$', views.new_catalogue, name=app_name+'new_catalogue'),

]
