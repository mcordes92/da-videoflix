import os, subprocess, django_rq

from pathlib import Path

from django.conf import settings
from ..models import Video


HLS_VARIANTS = [
    {"name": "360p", "height": 360, "v_bitrate": "800k", "maxrate": "856k", "bufsize": "1200k", "bandwidth": 900000},
    {"name": "480p", "height": 480, "v_bitrate": "1400k", "maxrate": "1498k", "bufsize": "2100k", "bandwidth": 1600000},
    {"name": "720p", "height": 720, "v_bitrate": "2800k", "maxrate": "2996k", "bufsize": "4200k", "bandwidth": 3200000},
    {"name": "1080p", "height": 1080, "v_bitrate": "5000k", "maxrate": "5350k", "bufsize": "7500k", "bandwidth": 5800000},
]

def process_video_to_hls(video_id: int):
    """
    Verarbeitet Video sequentiell: eine Variante nach der anderen
    """
    video = Video.objects.get(id=video_id)
    input_path = Path(video.video_file.path)

    output_root = Path(getattr(settings, 'MEDIA_ROOT')) / 'hls' / str(video.id)
    output_root.mkdir(parents=True, exist_ok=True)

    created_variants = []

    # Verarbeite jede Variante nacheinander (CPU-schonend)
    for v in HLS_VARIANTS:
        print(f"Processing {v['name']} for video {video_id}...")
        
        variant_dir = output_root / v["name"]
        variant_dir.mkdir(parents=True, exist_ok=True)

        playlist_path = transcode_variant_to_hls(
            input_path=input_path,
            output_dir=variant_dir,
            height=v["height"],
            v_bitrate=v["v_bitrate"],
            maxrate=v["maxrate"],
            bufsize=v["bufsize"]
        )

        created_variants.append({
            "name": v["name"],
            "height": v["height"],
            "bandwidth": v["bandwidth"],
            "playlist_rel": f"{v['name']}/{Path(playlist_path).name}"
        })
        
        print(f"Completed {v['name']} for video {video_id}")

    # Master-Playlist am Ende erstellen
    master_path = write_master_playlist(output_root, created_variants)
    
    print(f"All variants completed for video {video_id}")

    return {
        "video_id": video.id,
        "output_dir": str(output_root),
        "master_playlist": str(master_path),
        "variants": created_variants
    }


def transcode_variant_to_hls(
    input_path: Path,
    output_dir: Path,
    height: int,
    v_bitrate: str,
    maxrate: str,
    bufsize: str,
    hls_time: int = 6  # Längere Segmente = weniger CPU
):

    variant_playlist = output_dir / "index.m3u8"
    segment_pattern = output_dir / "seg_%05d.ts"

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(input_path),
        # Einfaches Scaling
        "-vf", f"scale=-2:{height}",
        # Video-Codec - MINIMALE Einstellungen
        "-c:v", "libx264",
        "-preset", "ultrafast",  # Schnellste Encoding
        "-tune", "zerolatency",  # Niedrige Latenz
        "-crf", "28",  # Höherer CRF = weniger CPU, kleinere Dateien
        # Einfache Keyframe-Einstellungen
        "-g", "150",  # Alle 6 Sekunden ein Keyframe (bei 25fps)
        "-keyint_min", "150",
        "-sc_threshold", "0",
        # Bitrate (nur wenn nötig)
        "-maxrate", maxrate,
        "-bufsize", bufsize,
        # Audio - einfach kopieren wenn möglich, sonst re-encoden
        "-c:a", "aac",
        "-b:a", "96k",  # Niedrigere Audio-Bitrate
        "-ac", "2",
        # HLS
        "-hls_time", str(hls_time),
        "-hls_playlist_type", "vod",
        "-hls_segment_filename", str(segment_pattern),
        # Performance
        "-threads", "2",  # Limitiere Threads (weniger CPU-Last)
        str(variant_playlist),
    ]

    run_ffmpeg(cmd)
    return str(variant_playlist)


def write_master_playlist(output_root: Path, variants: list):
    master_path = output_root / "master.m3u8"

    lines = ["#EXTM3U", "#EXT-X-VERSION:3"]

    for v in sorted(variants, key=lambda x: x["height"]):
        lines.append(f'#EXT-X-STREAM-INF:BANDWIDTH={v["bandwidth"]},RESOLUTION=1920x{v["height"]}')
        lines.append(v["playlist_rel"])
    
    master_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(master_path)


def run_ffmpeg(cmd: list):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=os.environ.copy())
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: (code {p.returncode}) {p.stderr}")