from django.urls import path
from . import views

urlpatterns = [
    path('', views.trainee_list, name='trainee_list'),
    path('export/', views.export_cohort_excel, name='export_current_cohort'),
    path('export/<int:cohort_id>/', views.export_cohort_excel, name='export_cohort'),
    path('archive/', views.archive_list, name='archive_list'),
    path('archive/<int:cohort_id>/', views.archive_detail, name='archive_detail'),
    path('bulk-signoff/', views.bulk_sign_off, name='bulk_sign_off'),
    path('<str:badge_number>/', views.trainee_detail, name='trainee_detail'),
    path('<str:badge_number>/signoff/<int:task_id>/', views.sign_off_task, name='sign_off_task'),
    path('<str:badge_number>/unsign/<int:task_id>/', views.unsign_task, name='unsign_task'),
]
