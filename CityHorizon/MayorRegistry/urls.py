from django.urls import path
from .views import Add, List, Update, Delete, ProvinceList, CityList, AddMayorCity, ListMayorCity, RemoveMayorCity, \
                   CityMayors, ProvinceMayors, MayorComplex

urlpatterns = [
    path('add/', Add.as_view()),
    path('list/', List.as_view()),
    path('update/', Update.as_view()),
    path('delete/', Delete.as_view()),
    path('provinces/', ProvinceList.as_view()),
    path('cities/', CityList.as_view()),
    path('add-mayor-city/', AddMayorCity.as_view()),
    path('list-mayor-city/', ListMayorCity.as_view()),
    path('remove-mayor-city/', RemoveMayorCity.as_view()),
    path('mayors-of-city/', CityMayors.as_view()),
    path('mayors-of-province/', ProvinceMayors.as_view()),
    path('mayor-complex-list/', MayorComplex.as_view()),
]