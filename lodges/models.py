from django.db import models
from places.models import Park, CountryIndex


class Lodge(models.Model):
    name = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    website = models.CharField(max_length=700)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=700)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    park = models.ForeignKey(Park, on_delete=models.PROTECT)
    countryIndex = models.ForeignKey(
        CountryIndex, on_delete=models.PROTECT)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Lodge, self).save(*args, **kwargs)
