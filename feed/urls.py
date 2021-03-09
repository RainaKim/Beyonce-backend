from django.urls import path, include
from .views import FeedListView, FeedDetailView, FeedUploadView

urlpatterns = [
    path('/<str:page_type>/<int:category_id>',FeedListView.as_view()),
    path('/<int:feed_id>',FeedDetailView.as_view()),
    path('',FeedUploadView.as_view())
]
