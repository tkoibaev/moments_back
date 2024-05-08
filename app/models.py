from django.db import models
from datetime import datetime
from django.utils import timezone
from django.db.models import Q
from django.db.models import CheckConstraint
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)



class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    avatar = models.CharField(max_length=155,null=True, blank=True)
    bio = models.CharField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username


class Tag(models.Model):
    name = models.CharField(max_length=100)


class MomentManager(models.Manager):
    
    def get_all_moments(self):
        return self.all()
    def get_user_moments(self, username):
        return self.filter(author__username=username)
    
    def delete_moment(self, moment_id):
        self.filter(id=moment_id).delete()

    def create_moment(self, author, description, image=None, tags=None):
        moment = self.create(author=author,description=description,image=image)
        if tags:
            for tag in tags:
                moment.tag.add(tag)
    
    def get_top_moments(self):
        return self.all()[:10]
                
    def get_likes_for_moment(self, moment_id):
        likes = Like.objects.likes_for_moment(moment_id)
        return [like.author for like in likes]
class Moment(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    image = models.CharField(max_length=155,blank=True, null=True)
    tag = models.ManyToManyField(Tag, null=True)
    
    objects = MomentManager()


class CommentManager(models.Manager):
    def comments_for_moment(self, moment_id):
        return self.filter(moment_id=moment_id)
    def get_random_comments_for_moment(self, moment_id):
        comments = self.filter(moment_id=moment_id)
        return comments
class Comment(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE) 
    moment = models.ForeignKey(Moment, on_delete=models.CASCADE) 
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    objects = CommentManager()



class LikeManager(models.Manager):
    def likes_for_moment(self, moment_id):
        return self.filter(moment_id=moment_id)
    def likes_for_comment(self, comment_id):
        return self.filter(comment_id=comment_id)
class Like(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE) 
    moment = models.ForeignKey(Moment, on_delete=models.CASCADE, null=True) 
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True) 
    date_created = models.DateTimeField(auto_now_add=True)
    objects = LikeManager()



class SubscriptionManager(models.Manager):
    def get_subscribers_for_user(self, username):
        return self.filter(subscriber__username=username)

    def get_subscriptions_for_user(self, username):
        return self.filter(author__username=username)
class Subscription(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='authored_subscriptions')
    subscriber = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='subscribed_to')
    date_created = models.DateTimeField(auto_now_add=True)

    objects = SubscriptionManager()

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(author=models.F('subscriber')),
                name='author_subscriber_not_same'
            )
        ]




