import os

from dotenv import load_dotenv

load_dotenv()

# Заберем токен нашего бота (прописать в файле ".env")
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))

# Заберем данные для подключения к базе данных (юзер, пароль, название бд) - тоже прописать в файле ".env"
PGUSER = str(os.getenv("PGUSER"))
PGPASSWORD = str(os.getenv("PGPASSWORD"))
DATABASE = str(os.getenv("DATABASE"))
admin_id = os.getenv("ADMIN_ID")
super_id = os.getenv("SUPER_ID")
admins = [
    os.getenv("SUPER_ID"),
]
dbsource = str(os.getenv("DBSOURCE"))

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
