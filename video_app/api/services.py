from ..models import Video

def list_videos_queryset():
    return Video.objects.all().order_by('-created_at')

def get_video_by_id(video_id: int) -> Video:
    return Video.objects.get(id=video_id)