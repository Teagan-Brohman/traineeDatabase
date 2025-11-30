from django.urls import path
from . import views

urlpatterns = [
    # Trainee orientation tracking
    path('', views.trainee_list, name='trainee_list'),
    path('export/', views.export_cohort_excel, name='export_current_cohort'),
    path('export/<int:cohort_id>/', views.export_cohort_excel, name='export_cohort'),
    path('archive/', views.archive_list, name='archive_list'),
    path('archive/<int:cohort_id>/', views.archive_detail, name='archive_detail'),
    path('bulk-signoff/', views.bulk_sign_off, name='bulk_sign_off'),

    # Advanced training (must come before <str:badge_number> catch-all)
    path('advanced/', views.advanced_staff_list, name='advanced_staff_list'),
    path('advanced/main/', views.advanced_staff_main, name='advanced_staff_main'),
    path('advanced/removed/', views.advanced_staff_removed, name='advanced_staff_removed'),
    path('advanced/export/', views.export_advanced_excel, name='export_advanced_excel'),
    path('advanced/export/removed/', views.export_advanced_excel_removed, name='export_advanced_excel_removed'),
    path('advanced/printable-list/', views.advanced_staff_printable_list, name='advanced_staff_printable_list'),
    path('advanced/import/get-trainees/', views.get_trainees_for_import, name='get_trainees_for_import'),
    path('advanced/import/import-trainees/', views.import_trainees_to_advanced, name='import_trainees_to_advanced'),
    path('advanced/update-training/', views.update_advanced_training, name='update_advanced_training'),
    path('advanced/update-staff-status/', views.update_advanced_staff_status, name='update_advanced_staff_status'),
    path('advanced/delete-training/<int:training_id>/', views.delete_advanced_training, name='delete_advanced_training'),
    path('advanced/<str:badge_number>/', views.advanced_staff_detail, name='advanced_staff_detail'),

    # Trainee detail (catch-all for badge numbers)
    path('<str:badge_number>/', views.trainee_detail, name='trainee_detail'),
    path('<str:badge_number>/signoff/<int:task_id>/', views.sign_off_task, name='sign_off_task'),
    path('<str:badge_number>/unsign/<int:task_id>/', views.unsign_task, name='unsign_task'),
]
