import os, django_rq, shutil

from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import post_save, post_delete

from ..models import Video
from .tasks import process_video_to_hls

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):

    if created:
        print("Video created, queueing processing tasks...")
        print(f"Video ID: {instance.id}, Video Path: {instance.video_file.path}")

        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(process_video_to_hls, video_id=instance.id)

@receiver(post_delete, sender=Video)
def delete_video(sender, instance, **kwargs):
    video_id = instance.id

    if getattr(instance, "video_file", None) and instance.video_file:
        try:
            if os.path.exists(instance.video_file.path):
                os.remove(instance.video_file.path)
        except Exception:
            pass

    if getattr(instance, "thumbnail", None) and instance.thumbnail:
        try:
            if os.path.exists(instance.thumbnail.path):
                os.remove(instance.thumbnail.path)
        except Exception:
            pass

    hls_dir = os.path.join(getattr(settings, "MEDIA_ROOT", ""), "hls", str(video_id))
    try:
        if os.path.exists(hls_dir):
            shutil.rmtree(hls_dir)
    except Exception:
        pass