from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path





urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    
    path('blog/', views.blog, name='blog'),
    path("article/<slug:slug>/", views.blog_detail, name="blog_detail"),
    
    path('contact/', views.contact_view, name='contact'),
    
    path('portfolio/<slug:slug>/', views.portfolio, name='portfolio'),
    path('portfolio/projets/<slug:slug>/', views.project_detail, name='project_detail'),
    
    
    path('pricing/', views.pricing, name='pricing'),
    
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),
    path('services/', views.services, name='services'),
    
    path('starter-page/', views.starter_page, name='starter-page'),
    
    path('team/', views.team, name='team'),
    path('testimonials/', views.testimonials, name='testimonials'),
    
    
    #__________________________________Included sections
    path('customers/', views.customerSection, name='customers'),
    path('aboutSection/', views.aboutSection, name='aboutSection'),
    
]

# Ajoute cette ligne pour servir les fichiers médias en mode développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)