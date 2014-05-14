
DEBUG = True

SECRET_KEY = "1234567890"
NEVERCACHE_KEY = "0987654321"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "dev.db",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    }
}
