from utils.db_api.db_commands import add_item

import asyncio

from utils.db_api.database import create_db

# Используем эту функцию, чтобы заполнить базу данных товарами
async def add_items():
    await add_item(id="1", name="ASUS",
                   category_name="🔌 Электроника", category_code="Electronics",
                   subcategory_name="🖥 Компьютеры", subcategory_code="PCs",
                   price=100, photo="-", description="Описание товара")
    await add_item(id="2", name="DELL",
                   category_name="🔌 Электроника", category_code="Electronics",
                   subcategory_name="🖥 Компьютеры", subcategory_code="PCs",
                   price=100, photo="-", description="Описание товара")
    await add_item(id="3", name="Apple",
                   category_name="🔌 Электроника", category_code="Electronics",
                   subcategory_name="🖥 Компьютеры", subcategory_code="PCs",
                   price=100, photo="-", description="Описание товара")
    await add_item(id="4", name="Iphone",
                   category_name="🔌 Электроника", category_code="Electronics",
                   subcategory_name="☎️ Телефоны", subcategory_code="Phones",
                   price=100, photo="-", description="Описание товара")
    await add_item(id="5", name="Xiaomi",
                   category_name="🔌 Электроника", category_code="Electronics",
                   subcategory_name="☎️ Телефоны", subcategory_code="Phones",
                   price=100, photo="-", description="Описание товара")
    await add_item(id="6", name="PewDiePie",
                   category_name="🛍 Услуги Рекламы", category_code="Ads",
                   subcategory_name="📹 На Youtube", subcategory_code="Youtube",
                   price=100, photo="-", description="Описание товара")
    await add_item(id="7", name="Топлес",
                   category_name="🛍 Услуги Рекламы", category_code="Ads",
                   subcategory_name="📹 На Youtube", subcategory_code="Youtube",
                   price=100, photo="-", description="Описание товара")
    await add_item(id="8", name="Орлёнок",
                   category_name="🛍 Услуги Рекламы", category_code="Ads",
                   subcategory_name="🗣 На Вконтакте", subcategory_code="VK",
                   price=100, photo="-", description="Описание товара")
    await add_item(id="9", name="МДК",
                   category_name="🛍 Услуги Рекламы", category_code="Ads",
                   subcategory_name="🗣 На Вконтакте", subcategory_code="VK",
                   price=100, photo="-", description="Описание товара")

loop = asyncio.get_event_loop()
loop.run_until_complete(create_db())
loop.run_until_complete(add_items())
