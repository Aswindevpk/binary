from django.urls import path,include


urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('creators/', include('creators.urls')),
    path('home/', include('home.urls')),
]