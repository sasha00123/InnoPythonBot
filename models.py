import peewee
import config


class BaseModel(peewee.Model):
    class Meta:
        database = config.DB


class Note(BaseModel):
    title = peewee.CharField(index=True)
    text = peewee.TextField()

