from config import DB as db
from models import Note

db.connect()

db.create_tables([Note])

db.close()
