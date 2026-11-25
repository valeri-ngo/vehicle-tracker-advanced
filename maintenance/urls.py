from django.urls import include, path

from maintenance.views import (
    MaintenanceScheduleCreateView,
    MaintenanceScheduleDeleteView,
    MaintenanceScheduleDetailView,
    MaintenanceScheduleListView,
    MaintenanceScheduleUpdateView,
    PartCreateView,
    PartDeleteView,
    PartDetailView,
    PartListView,
    PartUpdateView,
    ServiceRecordCreateView,
    ServiceRecordDeleteView,
    ServiceRecordDetailView,
    ServiceRecordListView,
    ServiceRecordUpdateView,
)

app_name = "maintenance"

service_record_detail_patterns = [
    path(
        "",
        ServiceRecordDetailView.as_view(),
        name="service-record-detail",
    ),
    path(
        "edit/",
        ServiceRecordUpdateView.as_view(),
        name="service-record-update",
    ),
    path(
        "delete/",
        ServiceRecordDeleteView.as_view(),
        name="service-record-delete",
    ),
]

maintenance_schedule_detail_patterns = [
    path(
        "",
        MaintenanceScheduleDetailView.as_view(),
        name="maintenance-schedule-detail",
    ),
    path(
        "edit/",
        MaintenanceScheduleUpdateView.as_view(),
        name="maintenance-schedule-update",
    ),
    path(
        "delete/",
        MaintenanceScheduleDeleteView.as_view(),
        name="maintenance-schedule-delete",
    ),
]

part_detail_patterns = [
    path(
        "",
        PartDetailView.as_view(),
        name="part-detail",
    ),
    path(
        "edit/",
        PartUpdateView.as_view(),
        name="part-update",
    ),
    path(
        "delete/",
        PartDeleteView.as_view(),
        name="part-delete",
    ),
]

part_patterns = [
    path(
        "",
        PartListView.as_view(),
        name="part-list",
    ),
    path(
        "create/",
        PartCreateView.as_view(),
        name="part-create",
    ),
    path(
        "<int:pk>/",
        include(part_detail_patterns),
    ),
]

urlpatterns = [
    path(
        "<int:pk>/",
        ServiceRecordListView.as_view(),
        name="service-record-list",
    ),
    path(
        "<int:pk>/add/",
        ServiceRecordCreateView.as_view(),
        name="service-record-create",
    ),
    path(
        "records/<int:pk>/",
        include(service_record_detail_patterns),
    ),
    path(
        "schedules/<int:pk>/",
        MaintenanceScheduleListView.as_view(),
        name="maintenance-schedule-list",
    ),
    path(
        "schedules/<int:pk>/add/",
        MaintenanceScheduleCreateView.as_view(),
        name="maintenance-schedule-create",
    ),
    path(
        "schedules/records/<int:pk>/",
        include(maintenance_schedule_detail_patterns),
    ),
    path(
        "parts/",
        include(part_patterns),
    ),
]
