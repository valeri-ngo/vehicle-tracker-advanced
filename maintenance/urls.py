from django.urls import include, path

from maintenance.views import (
    MaintenanceItemCreateView,
    MaintenanceItemDeleteView,
    MaintenanceItemDetailView,
    MaintenanceItemListView,
    MaintenanceItemUpdateView,
    MaintenanceScheduleCreateView,
    MaintenanceScheduleDeleteView,
    MaintenanceScheduleDetailView,
    MaintenanceScheduleListView,
    MaintenanceScheduleUpdateView,
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

maintenance_item_detail_patterns = [
    path(
        "",
        MaintenanceItemDetailView.as_view(),
        name="maintenance-item-detail",
    ),
    path(
        "edit/",
        MaintenanceItemUpdateView.as_view(),
        name="maintenance-item-update",
    ),
    path(
        "delete/",
        MaintenanceItemDeleteView.as_view(),
        name="maintenance-item-delete",
    ),
]

maintenance_item_patterns = [
    path(
        "",
        MaintenanceItemListView.as_view(),
        name="maintenance-item-list",
    ),
    path(
        "create/",
        MaintenanceItemCreateView.as_view(),
        name="maintenance-item-create",
    ),
    path(
        "<int:pk>/",
        include(maintenance_item_detail_patterns),
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
        "maintenance-items/",
        include(maintenance_item_patterns),
    ),
]
