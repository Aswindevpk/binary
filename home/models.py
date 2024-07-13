from django.db import models
from accounts.models import BaseModel
from accounts.models import CustomUser 
from autoslug import AutoSlugField


class Category(BaseModel):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name',unique=True,always_update=True)

    def __str__(self):
        return self.name

class Tag(BaseModel):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name',unique=True,always_update=True)

    def __str__(self):
        return self.name


class Blog(BaseModel):
    author_id = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    slug = AutoSlugField(populate_from='uid',unique=True,default=None)
    category_id = models.ForeignKey(Category,on_delete=models.CASCADE,blank=True,null=True,default=None)
    published = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class BlogTags(BaseModel):
    blog_id = models.ForeignKey(Blog,on_delete=models.CASCADE)
    tag_id = models.ForeignKey(Tag,on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.blog_id} {self.tag_id}"
    
    
class Comment(BaseModel):
    author_id = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    blog_id = models.ForeignKey(Blog, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return self.content
    
class Claps(BaseModel):
    blog_id = models.ForeignKey(Blog,related_name='claps', on_delete=models.CASCADE)
    user_id = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    
class Followers(BaseModel):
   follower = models.ForeignKey(CustomUser, related_name='following', on_delete=models.CASCADE)
   followed = models.ForeignKey(CustomUser, related_name='followers', on_delete=models.CASCADE)
    
class Views(BaseModel):
    blog_id = models.ForeignKey(Blog,on_delete=models.CASCADE)
    user_id = models.ForeignKey(CustomUser,on_delete=models.CASCADE)


class UploadedImage(models.Model):
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.name
    

