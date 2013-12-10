from django.db import models


class OdbcDatabase(models.Model):
    name = models.CharField(max_length=16, db_index=True)
    dsn = models.CharField(max_length=255)
    notes = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return "{}: '{}'".format(self.name, self.dsn)

    class Meta:
        ordering = ['name']
