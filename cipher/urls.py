from django.urls import path
from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('encrypt/', views.encrypt_page, name='encrypt_page'),
    path('decrypt/', views.decrypt_page, name='decrypt_page'),
    path('history/', views.history_page, name='history_page'),
    path('register/', views.register_page, name='register'),  # Теперь это правильно
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('texts/', views.text_list_page, name='text_list'),
    path('texts/add/', views.add_text_page, name='add_text_page'),
    path('api/register/', views.register_user, name='register_user'),
    path('api/history/', views.user_history, name='user_history'),
    path('api/change_password/', views.change_password, name='change_password'),
    path('api/text/', views.manage_text, name='add_text'),
    path('api/text/<int:text_id>/', views.manage_text, name='manage_text'),
    path('api/encrypt/', views.encrypt_text, name='encrypt_text'),
    path('api/decrypt/', views.decrypt_text, name='decrypt_text'),
    path('texts/<int:text_id>/', views.view_text_page, name='view_text'),
    path('profile/', views.profile_page, name='profile'),
    path('api/generate_key/', views.generate_key, name='generate_key'),
    path('api/get_playfair_matrix/', views.get_playfair_matrix, name='get_playfair_matrix'),
    
    # Добавьте эту строку в конец списка urlpatterns
    path('favicon.ico', lambda request: HttpResponse(status=204)),
]
