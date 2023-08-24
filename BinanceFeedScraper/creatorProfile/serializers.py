from rest_framework import serializers
from .models import Post

class CreatorInfoSerializer(serializers.Serializer):
    avatar_name = serializers.CharField()
    avatar_image = serializers.URLField()
    followers_count = serializers.IntegerField()
    liked_count = serializers.IntegerField()
    shared_count = serializers.IntegerField()
    bio_text = serializers.CharField()
    last_post = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", input_formats=["%Y-%m-%d %H:%M:%S"])

# Define a serializer class for your Post model
class PostSerializer(serializers.ModelSerializer):
    # Specify the fields that you want to include in the JSON output
    class Meta:
        model = Post
        fields = ['title', 'summary', 'url', 'created_at']
