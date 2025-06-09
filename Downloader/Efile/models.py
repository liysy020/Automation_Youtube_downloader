from django.db import models

class FileDB (models.Model):
    id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=100)
    file_object = models.FileField(upload_to='Storage/')
    time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file_name
    
    def delete (self, *args, **kwargs):
        self.file_object.delete()
        super().delete(*args, **kwargs)