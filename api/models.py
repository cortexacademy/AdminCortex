from django.db import models

# Create your models here.


class Subject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()


class Chapter(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

class Exam(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

class Topic(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()                                       
