from django.urls import path
from .views import creator_details, PostListCreateAPIView, post_details

urlpatterns = [
    # This URL pattern matches the creator_profile view that returns the profile information of a specific user
    path('details/', creator_details, name='creator_details'),
    # This URL pattern matches the PostListCreateAPIView view that returns a list of posts created by a specific user or creates a new post
    path('posts/', PostListCreateAPIView.as_view(), name='creator_posts'),
    # This URL pattern matches the post_detail view that returns a single post with its details
    path('singlePost/<int:post_id>/', post_details, name='post_detail'),
]

