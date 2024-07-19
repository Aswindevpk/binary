from django.contrib import admin
from .models import *

# Register your models here.


admin.site.register(Topic)
admin.site.register(Article)
admin.site.register(Comment)
admin.site.register(Clap)
admin.site.register(Follow)
admin.site.register(BlogImage)

