from django.conf.urls import url, include 

from applications.hr2 import views
from applications.hr2.api import form_views

app_name = 'hr2'

urlpatterns = [

    url(r'^$', views.service_book, name='hr2'),
    url(r'^hradmin/$', views.hr_admin, name='hradmin'),
    url(r'^edit/(?P<id>\d+)/$', views.edit_employee_details,
        name='editEmployeeDetails'),
    url(r'^viewdetails/(?P<id>\d+)/$',
        views.view_employee_details, name='viewEmployeeDetails'),
    url(r'^editServiceBook/(?P<id>\d+)/$',
        views.edit_employee_servicebook, name='editServiceBook'),
    url(r'^administrativeProfile/$', views.administrative_profile,
        name='administrativeProfile'),
    url(r'^addnew/$', views.add_new_user, name='addnew'),
    url(r'^ltc_form/(?P<id>\d+)/$', views.ltc_form,
        name='ltcForm'),
    
    url(r'^view_ltc_form/(?P<id>\d+)/$', views.view_ltc_form,
        name='view_ltc_form'),
    url(r'^form_mangement_ltc/',views.form_mangement_ltc, name='form_mangement_ltc'),
    url(r'dashboard/', views.dashboard, name='dashboard'),
    url(r'^form_mangement_ltc_hr/(?P<id>\d+)/$',views.form_mangement_ltc_hr, name='form_mangement_ltc_hr'),
    url(r'^form_mangement_ltc_hod/',views.form_mangement_ltc_hod, name='form_mangement_ltc_hod'),
    url(r'^search_employee/', views.search_employee, name='search_employee'),
    url(r'^track_file/(?P<id>\d+)/$', views.track_file, name='track_file'),
    url('form_view_ltc/(?P<id>\d+)/$', views.form_view_ltc, name='form_view_ltc'),
    # url('file_handle/', views.file_handle, name='file_handle'),
    url('file_handle_cpda/', views.file_handle_cpda, name='file_handle_cpda'),
    url('file_handle_leave/', views.file_handle_leave, name='file_handle_leave'),
    url('file_handle_ltc/', views.file_handle_ltc, name='file_handle_ltc'),
    url('file_handle_appraisal/', views.file_handle_appraisal, name='file_handle_appraisal'),
    url('file_handle_cpda_reimbursement/', views.file_handle_cpda_reimbursement, name='file_handle_cpda_reimbursement'),

    url(r'^cpda_form/(?P<id>\d+)/$', views.cpda_form,name='cpdaForm'),
    url(r'^view_cpda_form/(?P<id>\d+)/$', views.view_cpda_form,name='view_cpda_form'),
    url(r'^form_mangement_cpda/',views.form_mangement_cpda, name='form_mangement_cpda'),
    url(r'^form_mangement_cpda_hr/(?P<id>\d+)/$',views.form_mangement_cpda_hr, name='form_mangement_cpda_hr'),
    url(r'^form_mangement_cpda_hod/',views.form_mangement_cpda_hod, name='form_mangement_cpda_hod'),
    url('form_view_cpda/(?P<id>\d+)/$', views.form_view_cpda, name='form_view_cpda'),
    url(r'^api/',include('applications.hr2.api.urls')),

    url(r'^cpda_reimbursement_form/(?P<id>\d+)/$', views.cpda_reimbursement_form,name='cpdaReimbursementForm'),
    url(r'^view_cpda_reimbursement_form/(?P<id>\d+)/$', views.view_cpda_reimbursement_form,name='view_cpda_reimbursement_form'),
    url(r'form_view_cpda_reimbursement/(?P<id>\d+)/$', views.form_view_cpda_reimbursement, name='form_view_cpda_reimbursement'),
    url(r'^form_mangement_cpda_reimbursement/',views.form_mangement_cpda_reimbursement, name='form_mangement_cpda_reimbursement'),
    url(r'^form_mangement_cpda_reimbursement_hr/(?P<id>\d+)/$',views.form_mangement_cpda_reimbursement_hr, name='form_mangement_cpda_reimbursement_hr'),
    url(r'^form_mangement_cpda_reimbursement_hod/',views.form_mangement_cpda_reimbursement_hod, name='form_mangement_cpda_reimbursement_hod'),

    url(r'^leave_form/(?P<id>\d+)/$', views.leave_form,name='leaveForm'),
    url(r'^view_leave_form/(?P<id>\d+)/$', views.view_leave_form,name='view_leave_form'),
    url(r'^form_mangement_leave/',views.form_mangement_leave, name='form_mangement_leave'),
    url(r'^form_mangement_leave_hr/(?P<id>\d+)/$',views.form_mangement_leave_hr, name='form_mangement_leave_hr'),
    url(r'^form_mangement_leave_hod/',views.form_mangement_leave_hod, name='form_mangement_leave_hod'),
    url('form_view_leave/(?P<id>\d+)/$', views.form_view_leave, name='form_view_leave'),



    url(r'^appraisal_form/(?P<id>\d+)/$', views.appraisal_form,name='appraisalForm'),
    url(r'^view_appraisal_form/(?P<id>\d+)/$', views.view_appraisal_form,name='view_appraisal_form'),
    url(r'^form_mangement_appraisal/',views.form_mangement_appraisal, name='form_mangement_appraisal'),
    url(r'^form_mangement_appraisal_hr/(?P<id>\d+)/$',views.form_mangement_appraisal_hr, name='form_mangement_appraisal_hr'),
   
    url(r'^form_view_appraisal/(?P<id>\d+)/$', views.form_view_appraisal, name='form_view_appraisal'),
    url(r'^getform/$', views.getform , name='getform'),
    url(r'^getformcpdaAdvance/$', views.getformcpdaAdvance , name='getformcpdaAdvance'),
    url(r'^getformLeave/$', views.getformLeave , name='getformLeave'),  
    url(r'^getformAppraisal/$', views.getformAppraisal , name='getformAppraisal'),
    url(r'^getformcpdaReimbursement/$', views.getformcpdaReimbursement , name='getformcpdaReimbursement'),



    # New routes for React api Date:28-10-2024 --------------------------------------------------------------------------------------------------
    
    # search employee
    url(r'api/search_employee', views.search_employee_by_username, name='search_employee_by_username'),
    url(r'api/get_my_details', views.get_my_details, name='get_my_details'),

    url(r'api/get_leave_requests', views.get_leave_requests, name='get_leave_requests'),
    url(r'api/get_leave_inbox', views.get_leave_inbox, name='get_leave_inbox'),
    url(r'api/get_leave_archive', views.get_leave_archive, name='get_leave_archive'),
    url(r'^api/submit_leave_form', views.submit_leave_form, name='submit_leave_form'),
    url(r'api/view_leave_form_data/(?P<id>\d+)/$', views.view_leave_form_data, name='view_leave_form_data'), #change 1st nov 2024


    #url for tracking the files of all workflow
    url(r'api/get_track_file/(?P<id>\d+)/$', views.track_file_react, name='track_file_react'),






    

    url(r'api/get_ltc_requests', views.get_ltc_requests, name='get_ltc_requests'),
    url(r'api/get_ltc_inbox', views.get_ltc_inbox, name='get_ltc_inbox'),
    url(r'api/get_ltc_archive', views.get_ltc_archive, name='get_ltc_archive'),
    url(r'api/get_ltc_inbox_track/(?P<id>\d+)/$', views.track_file_react,name='leaveForm'),
    
    


    url(r'api/get_cpda_adv_requests', views.get_cpda_adv_requests, name='get_cpda_adv_requests'),
    url(r'api/get_cpda_adv_inbox', views.get_cpda_adv_inbox, name='get_cpda_adv_inbox'),
    url(r'api/get_cpda_adv_archive', views.get_cpda_adv_archive, name='get_cpda_adv_archive'),
    url(r'api/submit_cpda_adv_form/', views.submit_cpda_adv_form, name='submit_cpda_adv_form'), #change 29th oct 2024
    url(r'api/view_cpda_adv_form_data/(?P<id>\d+)/$', views.view_cpda_adv_form_data, name='view_cpda_adv_form_data'), #change 1st nov 2024


    url(r'api/get_cpda_claim_requests', views.get_cpda_claim_requests, name='get_cpda_claim_requests'),
    url(r'api/get_cpda_claim_inbox', views.get_cpda_claim_inbox, name='get_cpda_claim_inbox'),
    url(r'api/get_cpda_claim_archive', views.get_cpda_claim_archive, name='get_cpda_claim_archive'),

    url(r'api/get_appraisal_requests', views.get_appraisal_requests, name='get_appraisal_requests'),
    url(r'api/get_appraisal_inbox', views.get_appraisal_inbox, name='get_appraisal_inbox'),
    url(r'api/get_appraisal_archive', views.get_appraisal_archive, name='get_appraisal_archive'),




]
