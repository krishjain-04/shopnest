from django.db import models



class Slider(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    button_text = models.CharField(max_length=100, blank=True)
    button_url = models.CharField(max_length=255, blank=True)

    image = models.ImageField(upload_to='sliders/')

    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.title