from django.urls import path
from .views import Add, List, Update, Delete, ProvinceList, CityList, AddMayorZone, ListMayorZone, RemoveMayorZone

urlpatterns = [
    path('add/', Add.as_view()),
    path('list/', List.as_view()),
    path('update/', Update.as_view()),
    path('delete/', Delete.as_view()),
    path('provinces/', ProvinceList.as_view()),
    path('cities/', CityList.as_view()),
    path('add-mayor-zone/', AddMayorZone.as_view()),
    path('list-mayor-zone/', ListMayorZone.as_view()),
    path('remove-mayor-zone/', RemoveMayorZone.as_view()),
]