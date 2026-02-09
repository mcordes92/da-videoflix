"""API views for video listing and HLS streaming."""
from django.http import FileResponse, Http404

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from .serializers import VideoListSerializer
from .services import list_videos_queryset, get_video_by_id
from .utils import get_hls_variant_playlist_path, get_hls_variant_segment_path

class VideoListView(ListAPIView):
    """List all available videos."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = VideoListSerializer

    def get_queryset(self):
        """Return queryset of all videos."""
        return list_videos_queryset()
    
    def get_serializer_context(self):
        """Include request in serializer context."""
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx
    
class VideoHlsPlaylistView(APIView):
    """Serve HLS playlist files for video streaming."""
    
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id: int, resolution: str):
        """Return HLS playlist file for specified video and resolution."""
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
    """Serve HLS video segments for streaming."""
    
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id: int, resolution: str, segment: str):
        """Return HLS video segment file for specified video, resolution, and segment."""
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