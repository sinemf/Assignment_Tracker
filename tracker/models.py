from django.db import models


class Assignment(models.Model):
   course = models.CharField(max_length=100)
   title = models.CharField(max_length=200)
   description = models.TextField(blank=True)
   due_date = models.DateField()
   completed = models.BooleanField(default=False)


   def __str__(self):
       return f"{self.course}: {self.title}"
