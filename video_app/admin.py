from django.contrib import admin

from .models import Video

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "category", "thumbnail", "video_file")
    search_fields = ("title", "description")
    list_filter = ("category", "created_at")