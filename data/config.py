import os

from dotenv import load_dotenv

load_dotenv()

# Заберем токен нашего бота (прописать в файле ".env")
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
dbsource = str(os.getenv("DBSOURCE"))

# Заберем данные для подключения к базе данных (юзер, пароль, название бд) - тоже прописать в файле ".env"
admin_id = os.getenv("ADMIN_ID")
super_id = os.getenv("SUPER_ID")
admins = [
    os.getenv("SUPER_ID"),
]

if dbsource == "pg":
    PGUSER = str(os.getenv("PGUSER"))
    PGPASSWORD = str(os.getenv("PGPASSWORD"))
    DATABASE = str(os.getenv("DATABASE"))
    ip = os.getenv("ip")



# Ссылка подключения к базе данных
    POSTGRES_URI = f"postgresql://{PGUSER}:{PGPASSWORD}@{ip}/{DATABASE}"
    aiogram_redis = {
        'host': ip,
    }

    redis = {
        'address': (ip, 6379),
        'encoding': 'utf8'
    }
