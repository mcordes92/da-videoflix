from pathlib import Path
from django.conf import settings

def get_hls_root_dir(video_id: int) -> Path:
    return Path(getattr(settings, 'MEDIA_ROOT')) / 'hls' / str(video_id)


def get_hls_variant_dir(video_id: int, resolution: str) -> Path:
    return get_hls_root_dir(video_id) / resolution


def get_hls_variant_playlist_path(video_id: int, resolution: str) -> Path:
    return get_hls_variant_dir(video_id, resolution) / 'index.m3u8'


def get_hls_variant_segment_path(video_id: int, resolution: str, segment: str) -> Path:
    return get_hls_variant_dir(video_id, resolution) / segment