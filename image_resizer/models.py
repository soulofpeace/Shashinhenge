from django.db import models
from djangotoolbox import fields

# Create your models here.
class Image(models.Model):
	image_id = models.CharField(max_length=255)
	image_data = fields.BlobField()
	version = models.BigIntegerField()
	