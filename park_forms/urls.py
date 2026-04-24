from django.urls import path
from . import views

app_name = 'park_forms'

urlpatterns = [
    path('', views.index, name='index'),
    path('submit_form/', views.SubmitFormView.as_view(), name='submit_form'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('view/<int:form_id>/', views.view_form, name='view_form'),
    path('export_csv/', views.export_csv, name='export_csv'),
    path('stats/', views.stats_api, name='stats_api'),
]