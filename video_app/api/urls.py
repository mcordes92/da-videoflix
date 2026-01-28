from django.urls import path
from .views import VideoListView, VideoHlsPlaylistView, VideoHlsSegmentView

urlpatterns = [
    path("video/", VideoListView.as_view(), name="video-list"),
    path("video/<int:movie_id>/<str:resolution>/index.m3u8", VideoHlsPlaylistView.as_view(), name="video-hls-playlist"),
    path("video/<int:movie_id>/<str:resolution>/<str:segment>/", VideoHlsSegmentView.as_view(), name="video-hls-segment"),
]
