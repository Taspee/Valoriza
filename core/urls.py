from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('chat/', views.chat_page, name='chat_page'),
    path('chat/api/', views.chat_view, name='chat_view'),
    
    # APIs JSON
    path('api/enterprises/', views.enterprises, name='api_enterprises'),
    path('api/industries/', views.industries, name='api_industries'),
    
    # Páginas HTML
    path('empresas/', views.enterprises_page, name='enterprises_page'),
    path('empresa/<int:enterprise_id>/', views.enterprise_detail, name='enterprise_detail'),
    path('industrias/', views.industries_page, name='industries_page'),
    
    # Páginas pendientes (puedes crearlas después)
    # path('clientes/', views.clients_page, name='clients_page'),
    # path('formularios/', views.forms_page, name='forms_page'),
]