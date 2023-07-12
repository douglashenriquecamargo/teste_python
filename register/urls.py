from django.urls import path
from . import views

urlpatterns = [
    path('address/', views.Address.as_view()),
    path('person/', views.Person.as_view()),
    path('person/<id>', views.Person.as_view())
]