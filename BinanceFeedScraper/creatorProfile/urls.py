from django.urls import path
from . import views

urlpatterns = [
    path('creatorProfile/info/', views.creator_info, name='creator_info'),
    path('creatorProfile/posts/', views.creator_posts, name='creator_posts'),
    path('creatorProfile/singlePost/<int:post_id>/', views.single_post, name='single_post'),
]

