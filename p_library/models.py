from django.db import models
from django.contrib.auth.models import User, AbstractUser
from allauth.socialaccount.models import SocialAccount

# Create your models here.


class UserProfile(models.Model):    
    socacc = models.OneToOneField(SocialAccount, on_delete=models.CASCADE, verbose_name="Social account")
    user = models.OneToOneField(User, on_delete=models.CASCADE)    


class Author(models.Model):  
    full_name = models.TextField()  
    birth_year = models.SmallIntegerField()  
    country = models.CharField(max_length=2)

    def __str__(self):
        return "{}, {}".format(self.full_name, self.birth_year)


class Publisher(models.Model):
    name = models.TextField(unique=True)

    def __str__(self):
        return self.name


class Friend(models.Model):
    name = models.TextField()
    
    def __str__(self):
        return self.name


class Book(models.Model):  
    ISBN = models.CharField(max_length=13)  
    title = models.TextField()  
    description = models.TextField()  
    year_release = models.SmallIntegerField()  
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    copy_count = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=30, decimal_places=2)
    publisher = models.ForeignKey(Publisher, null=True, blank=True, on_delete=models.CASCADE)
    lendedto = models.ForeignKey(Friend, null=True, blank=True, on_delete=models.CASCADE)
    cover = models.ImageField(upload_to="covers", blank=True)

    def __str__(self):
        return self.title


