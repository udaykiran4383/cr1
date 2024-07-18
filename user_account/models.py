# models.py
from django.db import models

class College(models.Model):
    name = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    state = models.CharField(max_length=255)

    class Meta:
        unique_together = ('name', 'state', 'district')

    def __str__(self):
        return self.name

class Student(models.Model):
    name = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    years = models.DateField()
    gender = models.CharField(max_length=10)
    stream = models.CharField(max_length=50)
    year_of_study = models.CharField(max_length=50)
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=100)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student)

    def __str__(self):
        return self.name

class Task(models.Model):
    question = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=255)

    def __str__(self):
        return self.question

class CollegeLeaderboard(models.Model):
    college = models.OneToOneField(College, on_delete=models.CASCADE)
    total_points = models.IntegerField(default=0)

class IndividualLeaderboard(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
