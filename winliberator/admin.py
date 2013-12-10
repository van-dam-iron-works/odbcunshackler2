from django.contrib import admin
from models import OdbcDatabase


class OdbcDatabaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'dsn']
admin.site.register(OdbcDatabase, OdbcDatabaseAdmin)
