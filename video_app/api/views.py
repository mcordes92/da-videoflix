from django.http import FileResponse, Http404

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from .serializers import VideoListSerializer
from .services import list_videos_queryset, get_video_by_id
from .utils import get_hls_variant_playlist_path, get_hls_variant_segment_path

class VideoListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VideoListSerializer

    def get_queryset(self):
        return list_videos_queryset()
    
    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx
    
class VideoHlsPlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id: int, resolution: str):
        try:
            get_video_by_id(movie_id)
        except Exception:
            raise Http404("Video not found")
        
        playlist_path = get_hls_variant_playlist_path(movie_id, resolution)
        if not playlist_path.exists():
            raise Http404("Playlist not found")
        
        response = FileResponse(open(playlist_path, 'rb'), content_type='application/vnd.apple.mpegurl')
        response["Content-Disposition"] = "inline; filename=index.m3u8"
        return response
    
class VideoHlsSegmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id: int, resolution: str, segment: str):
        try:
            get_video_by_id(movie_id)
        except Exception:
            raise Http404("Video not found")
        
        if "/" in segment or "\\" in segment:
            raise Http404("Segment not found")
        
        segment_path = get_hls_variant_segment_path(movie_id, resolution, segment)
        if not segment_path.exists():
            raise Http404("Segment not found")
        
        response = FileResponse(open(segment_path, 'rb'), content_type='video/MP2T')
        response["Content-Disposition"] = f"inline; filename={segment}"
        return response