from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('trading/', include('trading.urls')),
    path('analytics/', include('analytics.urls')),
    path('alerts/', include('alerts.urls')),
]
