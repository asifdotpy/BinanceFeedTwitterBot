from rest_framework import serializers
from .models import Post
import xml.etree.ElementTree as ET


# Define a serializer class for your CreatorInfo model

class CreatorInfoSerializer(serializers.Serializer):
    binance_id = serializers.CharField()
    avatar_name = serializers.CharField()
    # Use the custom field class for avatar_image
    followers_count = serializers.IntegerField()
    liked_count = serializers.IntegerField()
    shared_count = serializers.IntegerField()
    bio_text = serializers.CharField()
    # Use the custom validator function for last_post and remove the format and input_formats arguments
    last_post = serializers.CharField()

    def validate_binance_id(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("binance_id must be a string")
        return value

    def validate_avatar_name(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("avatar_name must be a string")
        return value

    def validate_followers_count(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError(
                "followers_count must be an integer")
        return value

    def validate_liked_count(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError("liked_count must be an integer")
        return value

    def validate_shared_count(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError(
                "shared_count must be an integer")
        return value

    def validate_bio_text(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("bio_text must be a string")
        return value

    def validate_last_post(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("last_post must be a string")
        return value

# Define a serializer class for your Post model


class PostSerializer(serializers.ModelSerializer):
    # Specify the fields that you want to include in the JSON output
    class Meta:
        model = Post
        fields = ['title', 'summary', 'url', 'created_at']
