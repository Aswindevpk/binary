from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Blog)
admin.site.register(Comment)
admin.site.register(BlogTags)
admin.site.register(Claps)
admin.site.register(Followers)
admin.site.register(Views)
admin.site.register(UploadedImage)

