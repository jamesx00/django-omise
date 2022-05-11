from django.db import models


class DeletedStatusQueryset(models.QuerySet):
    def live(self):
        return self.filter(deleted=False)

    def deleted(self):
        return self.filter(deleted=True)


class NotDeletedManager(models.Manager):
    def get_queryset(self):
        return DeletedStatusQueryset(self.model, using=self._db)

    def live(self):
        return self.get_queryset().live()

    def deleted(self):
        return self.get_queryset().deleted()
