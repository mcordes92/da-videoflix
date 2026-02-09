"""Serializers for video API endpoints."""
from rest_framework import serializers

from ..models import Video

class VideoListSerializer(serializers.ModelSerializer):
    """Serializer for video list with thumbnail URL."""
    
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ["id", "created_at", "title", "description", "thumbnail_url", "category"]

    def get_thumbnail_url(self, obj):
        """Generate absolute URL for video thumbnail."""
        request = self.context.get('request')
        if not obj.thumbnail:
            return None
        url = obj.thumbnail.url
        if request:
            return request.build_absolute_uri(url)
        return url
    
