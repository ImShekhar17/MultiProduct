
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('', include(('authApp.urls', 'authApp'), namespace='authApp')),
    path('', include(('serviceApp.urls', 'serviceApp'), namespace='serviceApp')),
]
