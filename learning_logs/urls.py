"""
URL configuration for learning_logs project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView

from accounts.views import home
from accounts.views import signIn, register
from dashboard.views import home, boards, newBoard, boardPage, newConcept, setTags, toggleTags, deleteTag, updateConcept, deleteConcept
from user_logs.views import newLog, logBreakdown

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', home, name='home'),

    # All Authentication URLs
    path('signIn/', signIn, name='signIn'),
    path('register/', register, name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # All Dashboards URLs
    path('dashboard/', boards, name='dashboard'),
    path('newBoard/', newBoard, name='newBoard'),
    path('board/<uuid:id>/', boardPage, name='boardPage'),
    path('board/<uuid:id>/newConcept/', newConcept, name='newConcept'),
    path('board/<uuid:board_id>/<uuid:concept_id>/setTags/', setTags, name='setTags'),
    path('board/<uuid:board_id>/<uuid:concept_id>/<uuid:tag_id>/toggle/', toggleTags, name='toggleTags'),
    path('tag/<uuid:tag_id>/delete/', deleteTag, name='deleteTag'),

    # All Concept URLs
    path('concept/update/<uuid:concept_id>/', updateConcept, name='updateConcept'),
    path('concept/delete/<uuid:concept_id>/', deleteConcept, name='deleteConcept'),

    # All Logs URLs
    path('logs/newLog/<uuid:id>/', newLog, name='newLog'),
    path('logs/logBreakdown/<uuid:id>', logBreakdown, name='logBreakdown'),

    # Used to auto reload browser
    path('__reload__/', include('django_browser_reload.urls')),


]
