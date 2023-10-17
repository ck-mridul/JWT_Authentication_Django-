from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view() ),
    path('', views.UsersView.as_view() ),
    path('userupdate/', views.UserUpdateView.as_view() ),
    path('userdelete/', views.DeleteUserView.as_view() ),
    
]
