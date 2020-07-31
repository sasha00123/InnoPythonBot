from decouple import config

TOKEN = config("TOKEN")
PORT = config("PORT", default=8443, cast=int)
HEROKU_APP_NAME = config("HEROKU_APP_NAME", default=None)
