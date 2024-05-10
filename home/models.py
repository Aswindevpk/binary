from django.db import models
from accounts.models import BaseModel
from accounts.models import CustomUser 


class Category(BaseModel):
    category = models.CharField(max_length=200)

class Tag(BaseModel):
    tag = models.CharField(max_length=200)


class Blog(BaseModel):
    creator = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    tag=models.ForeignKey(Tag,on_delete=models.CASCADE)
    img = models.ImageField(upload_to='media')

class Comment(BaseModel):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    content = models.TextField()

    

