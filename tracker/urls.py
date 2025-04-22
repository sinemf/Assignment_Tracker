from django.urls import path
from . import views


urlpatterns = [
   path('', views.dashboard, name='dashboard'),
   path('add/', views.add_assignment, name='add'),
   path('add/<str:due_date>/', views.add_assignment_with_date, name='add_with_date'),
   path('edit/<int:id>/', views.edit_assignment, name='edit'),
   path('export/', views.export_calendar, name='export_ics'),
   path("delete/<int:id>/", views.delete_assignment, name="delete"),
]
