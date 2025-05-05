"""Summary URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from SummaryApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),  # Set the landing page to the index view
    path('UserLogin', views.UserLogin, name='UserLogin'),
    path('UserLoginAction', views.UserLoginAction, name='UserLoginAction'),
    path('Signup', views.Signup, name='Signup'),
    path('SignupAction', views.SignupAction, name='SignupAction'),
    path('TrainNLP', views.TrainNLP, name='TrainNLP'),
    path('GenerateSummary', views.GenerateSummary, name='GenerateSummary'),
    path('GenerateSummaryAction', views.GenerateSummaryAction, name='GenerateSummaryAction'),
    path('Aboutus', views.Aboutus, name='Aboutus'),
]
