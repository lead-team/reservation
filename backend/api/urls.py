from django.urls import path
from . import views
urlpatterns = [
    path('get-menu/',views.filter_meals),
    path('get-reservations/',views.get_all_reservations),
    path('reserve/',views.reserve_meal),
    path('shiftmeal/create/',views.create_shift_meal)
]