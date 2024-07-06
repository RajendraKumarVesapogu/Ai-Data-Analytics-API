# models.py
from django.db import models
class GameData(models.Model):
    AppID = models.IntegerField(primary_key=True)
    Name = models.CharField(max_length=255)
    Release_date = models.DateField()
    Required_age = models.IntegerField()
    Price = models.DecimalField(max_digits=10, decimal_places=2)
    DLC_count = models.IntegerField()
    About_the_game = models.TextField()
    Supported_languages = models.TextField()
    Windows = models.BooleanField()
    Mac = models.BooleanField()
    Linux = models.BooleanField()
    Positive = models.IntegerField()
    Negative = models.IntegerField()
    Score_rank = models.CharField(max_length=50)  # Assuming this is a string representation
    Developers = models.TextField()
    Publishers = models.TextField()
    Categories = models.TextField()
    Genres = models.TextField()
    Tags = models.TextField()

    def __str__(self):
        return self.Name
    
    from django.db import models
