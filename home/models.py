from django.db import models
from accounts.models import BaseModel
from accounts.models import CustomUser 


class Topic(BaseModel):
    name = models.CharField(max_length=200)
    def __str__(self):  
        return self.name
    
    
class Article(BaseModel):
    author = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200,blank=True,null=True)
    image = models.ImageField(upload_to="media/images")
    content = models.TextField()
    topics = models.ManyToManyField(Topic,related_name='articles')
    is_published = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    

class Bookmark(BaseModel):
    user = models.ForeignKey(CustomUser, related_name='bookmarks', on_delete=models.CASCADE)
    article = models.ForeignKey(Article, related_name='bookmarks', on_delete=models.CASCADE)
    bookmarked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} bookmarked {self.article.title}"


class ReadingHistory(BaseModel):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    article = models.ForeignKey(Article,on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user','article')
        ordering = ['-read_at']

    def __str__(self):
        return f'{self.user} read {self.article} on {self.read_at}'

    
    
class Comment(BaseModel):
    author = models.ForeignKey(CustomUser, related_name='comments',on_delete=models.CASCADE)
    article = models.ForeignKey(Article, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return self.content
    
class Clap(BaseModel):
    article = models.ForeignKey(Article,related_name='claps', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, related_name='claps' ,on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'article')

    
class Follow(BaseModel):
   follower = models.ForeignKey(CustomUser, related_name='following', on_delete=models.CASCADE)
   followed = models.ForeignKey(CustomUser, related_name='followers', on_delete=models.CASCADE)

   class Meta:
        unique_together = ('follower', 'followed')


class BlogImage(models.Model):
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.name
    

