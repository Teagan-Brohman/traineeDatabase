"""
URL configuration for trainee_tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib.auth import logout
from django.urls import path, include
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('/admin/login/')

# Override admin index to redirect to tracker
_original_admin_index = admin.site.index
def custom_admin_index(request, extra_context=None):
    """Redirect to tracker after login (superusers can access admin with ?admin=1)"""
    if request.user.is_superuser and request.GET.get('admin') == '1':
        return _original_admin_index(request, extra_context)
    return redirect('trainee_list')

admin.site.index = custom_admin_index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tracker/', include('tracker.urls')),
    path('logout/', logout_view, name='logout'),
    path('', lambda request: redirect('trainee_list')),
]
