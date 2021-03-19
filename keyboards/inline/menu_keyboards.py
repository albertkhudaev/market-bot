from loader import bot
from data.config import admin_id
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.utils.callback_data import CallbackData

from utils.db_api.db_commands import get_subcategories, count_items, get_items, get_categories, count_all

# Создаем CallbackData-объекты, которые будут нужны для работы с менюшкой
menu_cd = CallbackData("show_menu", "level", "category", "subcategory", "item_id", "cat_name", "subcat_name")
buy_item = CallbackData("buy", "item_id")


# С помощью этой функции будем формировать коллбек дату для каждого элемента меню, в зависимости от
# переданных параметров. Если Подкатегория, или айди товара не выбраны - они по умолчанию равны нулю
def make_callback_data(level, category="0", subcategory="0", item_id="0", cat_name="0", subcat_name="0", new=False):
    return menu_cd.new(level=level, category=category, cat_name=cat_name, subcategory=subcategory, subcat_name=subcat_name, item_id=item_id)


# Создаем функцию, которая отдает клавиатуру с доступными категориями
async def categories_keyboard(user):
    # Указываем, что текущий уровень меню - 0, при заходе обычным пользователем
    if user == "customer":
        CURRENT_LEVEL = 0
    # Указываем, что текущий уровень меню - 10, при заходе с редактированием
    elif user == "edit":
        CURRENT_LEVEL = 10
    # Указываем, что текущий уровень меню - 20, при заходе с созданием
    elif user == "new":
        CURRENT_LEVEL = 20

    # Создаем Клавиатуру
    markup = InlineKeyboardMarkup()

    # Забираем список товаров из базы данных с РАЗНЫМИ категориями и проходим по нему
    categories = await get_categories()
    for category in categories:
        # Чекаем в базе сколько товаров существует под данной категорией
        number_of_items = await count_items(category.category_code)

        # Сформируем текст, который будет на кнопке
        button_text = f"{category.category_name} ({number_of_items} шт)"

        # Сформируем колбек дату, которая будет на кнопке. Следующий уровень - текущий + 1, и перечисляем категории
        callback_data = make_callback_data(level=CURRENT_LEVEL + 1, category=category.category_code, cat_name=f"{category.category_name}")

        # Вставляем кнопку в клавиатуру
        markup.row(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )
    
    if user == "new":
        markup.row(
        InlineKeyboardButton(
            text="Создать категорию",
            callback_data=make_callback_data(level=22))
    )
    
    # Если меню администратора - добавляем возможность выхода в меню магазина
    if user == "edit" or user == "new":
        markup.row(
        InlineKeyboardButton(
            text="Выход",
            callback_data=make_callback_data(level=0))
    )
    #await bot.send_message(chat_id=admin_id, text=make_callback_data(level=10))
    #await bot.send_message(chat_id=admin_id, text=CURRENT_LEVEL)
    # Возвращаем созданную клавиатуру в хендлер
    return markup


# Создаем функцию, которая отдает клавиатуру с доступными подкатегориями, исходя из выбранной категории
async def subcategories_keyboard(category, cat_name, user):
    # Указываем, что текущий уровень меню - 1, при заходе обычным пользователем
    if user == "customer":
        CURRENT_LEVEL = 1
    # Указываем, что текущий уровень меню - 11, при заходе с редактированием
    elif user == "edit":
        CURRENT_LEVEL = 11
    # Указываем, что текущий уровень меню - 21, при заходе с созданием
    elif user == "new":
        CURRENT_LEVEL = 21
        items = await count_all()
    markup = InlineKeyboardMarkup()

    # Забираем список товаров с РАЗНЫМИ подкатегориями из базы данных с учетом выбранной категории и проходим по ним
    subcategories = await get_subcategories(category)
    for subcategory in subcategories:
        # Чекаем в базе сколько товаров существует под данной подкатегорией
        number_of_items = await count_items(category_code=category, subcategory_code=subcategory.subcategory_code)

        # Сформируем текст, который будет на кнопке
        button_text = f"{subcategory.subcategory_name} ({number_of_items} шт)"

        # Сформируем колбек дату, которая будет на кнопке
        if user == "new":
            callback_data = make_callback_data(level=13,
                                            category=category, cat_name=cat_name, subcategory=subcategory.subcategory_code,
                                            item_id=items + 1)
        else:
            callback_data = make_callback_data(level=CURRENT_LEVEL + 1,
                                            category=category, cat_name=cat_name, subcategory=subcategory.subcategory_code)
        markup.row(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )

    # кнопка для создания новой категории, если режим редактирования включен
    if user == "new":
        markup.row(
        InlineKeyboardButton(
            text="Создать подкатегорию",
            callback_data=make_callback_data(level=23, category=category, cat_name=cat_name))
        )
    
    # Создаем Кнопку "Назад", в которой прописываем колбек дату такую, которая возвращает
    # пользователя на уровень назад - на уровень 0.
    markup.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=make_callback_data(level=CURRENT_LEVEL - 1))
    )
    return markup


# Создаем функцию, которая отдает клавиатуру с доступными товарами, исходя из выбранной категории и подкатегории
async def items_keyboard(category, subcategory, user):
    # Указываем, что текущий уровень меню - 2, при заходе обычным пользователем
    if user == "customer":
        CURRENT_LEVEL = 2
    # Указываем, что текущий уровень меню - 12, при заходе с редактированием
    elif user == "edit":
        CURRENT_LEVEL = 12

    # Устанавливаю row_width = 1, чтобы показывалась одна кнопка в строке на товар
    markup = InlineKeyboardMarkup(row_width=1)

    # Забираем список товаров из базы данных с выбранной категорией и подкатегорией, и проходим по нему
    items = await get_items(category, subcategory)
    for item in items:
        # Сформируем текст, который будет на кнопке
        button_text = f"{item.name} - ${item.price}"

        # Сформируем колбек дату, которая будет на кнопке
        callback_data = make_callback_data(level=CURRENT_LEVEL + 1,
                                           category=category, subcategory=subcategory,
                                           item_id=item.id)
        markup.row(
            InlineKeyboardButton(
                text=button_text, callback_data=callback_data)
        )

    # Создаем Кнопку "Назад", в которой прописываем колбек дату такую, которая возвращает
    # пользователя на уровень назад - на уровень 1 - на выбор подкатегории
    markup.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=make_callback_data(level=CURRENT_LEVEL - 1,
                                             category=category))
    )
    return markup


# Создаем функцию, которая отдает клавиатуру с кнопками "купить" и "назад" для выбранного товара
def item_keyboard(category, subcategory, item_id, user):
    # Указываем, что текущий уровень меню - 3, при заходе обычным пользователем
    if user == "customer":
        CURRENT_LEVEL = 3
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text=f"Купить",
            callback_data=buy_item.new(item_id=item_id)
        )
    )
    markup.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=make_callback_data(level=CURRENT_LEVEL - 1,
                                             category=category, subcategory=subcategory))
    )
    return markup


# Создаем функцию, которая отдает клавиатуру панели администратора
async def admin_keyboard():
    CURRENT_LEVEL = 99
    # Создаем Клавиатуру
    markup = InlineKeyboardMarkup()
    markup.row(
            InlineKeyboardButton(text="Редактировать товар", callback_data=make_callback_data(level=10))
            #InlineKeyboardButton(text="Добавить товар", callback_data=make_callback_data(level=20))
        )
    markup.row(
            InlineKeyboardButton(text="Добавить товар", callback_data=make_callback_data(level=20))
    )
    markup.row(
        InlineKeyboardButton(
            text="Выход",
            callback_data=make_callback_data(level=0))
    )
    return markup

def item_edit_keyboard(category, subcategory, item_id, name, price, description):
    # Указываем, что текущий уровень меню - 13
    CURRENT_LEVEL = 13
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text=name,
            callback_data=make_callback_data(level=14,
                                             category=category, subcategory=subcategory, item_id=item_id)
        )
    )

    markup.row(
        InlineKeyboardButton(
            text=price,
            callback_data=make_callback_data(level=15,
                                             category=category, subcategory=subcategory, item_id=item_id)
        )
    )

    markup.row(
        InlineKeyboardButton(
            text=description,
            callback_data=make_callback_data(level=16,
                                             category=category, subcategory=subcategory, item_id=item_id)
        )
    )

    markup.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=make_callback_data(level=CURRENT_LEVEL - 1,
                                             category=category, subcategory=subcategory, item_id=item_id))
    )

    markup.row(
        InlineKeyboardButton(
            text="Выход",
            callback_data=make_callback_data(level=0))
    )
    return markup
