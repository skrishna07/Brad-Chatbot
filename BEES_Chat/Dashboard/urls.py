"""
URL configuration for BEES_Chat project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from . import views
urlpatterns = [
    path('login/',views.loginPage,name='login'),
    path('register/',views.signupPage,name='register'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('userEngagement/',views.userEngagement,name='userEngagement'),
    path('sessionAnalytics/',views.sessionAnalytics,name='sessionAnalytics'),
    path('logout/',views.logoutFuntion,name='logout'),
    path('chatHistory/',views.getChatHistory,name='chatHistory'),
    path('sessionHistory/',views.get_session_details,name='sessionHistory'),
    path('getUserData/',views.getUserData,name='getUserData'),
    path('delete_user/', views.delete_user, name='delete_user'),
    path('reset_password/', views.reset_password, name='reset_password'),
]
