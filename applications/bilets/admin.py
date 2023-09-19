from django.contrib import admin

from applications.bilets.models import Comment, Ticket


@admin.register(Ticket)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'like_count']
    list_filter = ['owner']
    search_fields = ['title']

    def like_count(self, obj):
        return obj.likes.filter(is_like=True).count()


admin.site.register(Comment)
