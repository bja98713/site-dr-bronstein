from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('examens/', views.exam_list, name='exam_list'),
    path('examens/<slug:slug>/', views.exam_detail, name='exam_detail'),
    path('consultations/', views.consultations, name='consultations'),
    path('prendre-rendez-vous/', views.appointment, name='appointment'),
    path('pathologies/', views.pathology_list, name='pathologies'),
    path('pathologies/<slug:slug>/', views.pathology_detail, name='pathology_detail'),
    path('guides/', views.guides, name='guides'),
    path('symptomes/', views.symptom_index, name='symptomes'),
    path('faq/', views.faq, name='faq'),
    path('blog/', views.blog_list, name='blog_list'),
    path('actualites/', views.blog_list, name='actualites'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
]
