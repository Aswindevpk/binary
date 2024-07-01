from django.db import models
from accounts.models import BaseModel
from accounts.models import CustomUser 
from autoslug import AutoSlugField


class Category(BaseModel):
    category = models.CharField(max_length=200)

    def __str__(self):
        return self.category

class Tag(BaseModel):
    tag = models.CharField(max_length=200)

    def __str__(self):
        return self.tag


class Blog(BaseModel):
    creator = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    tag=models.ForeignKey(Tag,on_delete=models.CASCADE)
    img = models.ImageField(upload_to='media')
    slug = AutoSlugField(populate_from='title',unique=True,default=None,null=True)

    def __str__(self):
        return self.title


class Comment(BaseModel):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return self.content

    

