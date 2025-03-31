from django.db import models

from utilities.generator import primary_key_generator, public_id_generator


class Certificate(models.Model):
    name = models.CharField(max_length=200, blank=True)
    organization = models.TextField()
    url = models.URLField()
    date_issued = models.DateField()
    file_url = models.URLField(blank=True, null=True)
    published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    public_id = models.CharField(max_length=50, db_index=True, blank=True)

    def save(self, *args, **kwargs):
        if self._state.adding or not self.public_id:
            _id = self.pk or primary_key_generator()
            self.public_id = public_id_generator(_id, "Certificate")
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name
