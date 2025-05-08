from django.db import models

class Job(models.Model):
    company_name = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

class Project(models.Model):
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty_rating = models.IntegerField(default=1)
    start_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Technology(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField(max_length=300)

    def __str__(self):
        return self.name