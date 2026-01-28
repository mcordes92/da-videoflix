from rest_framework import serializers

from ..models import Video

class VideoListSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ["id", "created_at", "title", "description", "thumbnail_url", "category"]

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if not obj.thumbnail:
            return None
        url = obj.thumbnail.url
        if request:
            return request.build_absolute_uri(url)
        return url
    
