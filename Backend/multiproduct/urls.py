
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('auth/', include(('authApp.urls', 'authApp'), namespace='authApp')),
    path('services/', include(('serviceApp.urls', 'serviceApp'), namespace='serviceApp')),
]
