from django.urls import path
from .views import SocialLoginView, ProfileView, FollowView, LikeView

urlpatterns = [
    path('/social_login', SocialLoginView.as_view()),
    path('/profile', ProfileView.as_view()),
    path('/follow', FollowView.as_view()),
    path('/like', LikeView.as_view()),
]
