from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=160)
    img_path = models.CharField(max_length=1024)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    created_at = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listings")

    def __str__(self):
        return f"{self.title}, {self.description}, {self.img_path}, {self.price}, {self.created_at}, {self.user}, {self.category}"

class Bid(models.Model):
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"{self.amount}, {self.listing}, {self.user}"

class Comment(models.Model):
    text = models.TextField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField()

    def __str__(self):
        return f"{self.text}, {self.listing}, {self.user}, {self.created_at}"
