"""ReUnite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views as user_views

admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',user_views.homepage, name = 'home'),
    path('signup/',user_views.signup, name = 'signup'),
    path('profile/',user_views.profile, name = 'profile'),
    path('missing-child/',user_views.missing_child, name = 'missing_child'),
    path('search-child/',user_views.search_child, name = 'search_child'),
    path('search-child/<int:pk>',user_views.search_child, name = 'individual_search_child_view'),
    path('sighted-child/',user_views.sighted_child, name = 'sighted_child'),
    path('login/',auth_views.LoginView.as_view(template_name = 'login.html', extra_context = {'title': 'Log In'}), name = 'login'),
    path('logout/',auth_views.LogoutView.as_view(template_name = 'logout.html', extra_context = {'title': 'Log Out'}), name = 'logout'),
    path('about/',user_views.about, name = 'about'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
