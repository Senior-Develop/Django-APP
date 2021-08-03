"""DjangoApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
#from cuser.forms import AuthenticationForm
#from django.conf.urls import include, url
#from django.contrib.auth.views import LoginView

from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout_request, name="logout"),
    
#    url(r'^accounts/login/$', LoginView.as_view(authentication_form=AuthenticationForm), name='login'),
#    url(r'^accounts/', include('django.contrib.auth.urls')),
    
    path("login/", views.login_request, name="login"),
    path("upload/", views.upload, name="upload"),
    path("freqloc/", views.freqloc, name="freqloc"),
    path("gtakelog/", views.google_takeout_login, name="gtakelog"),

]
