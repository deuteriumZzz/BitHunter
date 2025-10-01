from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('trading/', include('trading.urls')),
    path('analytics/', include('analytics.urls')),
    path('alerts/', include('alerts.urls')),
    path('api/', include('api.urls')),
    path('api/auth/token/', obtain_auth_token, name='api_token_auth'),
]
