from django.urls import path, include

urlpatterns = [
    path('user', include('user.urls')),
    path('feed', include('feed.urls')),
    path('story', include('story.urls')),
]
