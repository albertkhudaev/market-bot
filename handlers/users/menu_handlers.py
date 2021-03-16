from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from states import EditState
from keyboards.inline.menu_keyboards import menu_cd, categories_keyboard, subcategories_keyboard, \
    items_keyboard, item_keyboard, admin_keyboard, item_edit_keyboard
from loader import dp
from utils.db_api.db_commands import get_item, count_all, get_items, add_item
from loader import storage


# Хендлер на команду /menu
@dp.message_handler(Command("menu"))
async def show_menu(message: types.Message):
    # Выполним функцию, которая отправит пользователю кнопки с доступными категориями
    await list_categories(message)


# Та самая функция, которая отдает категории. Она может принимать как CallbackQuery, так и Message
# Помимо этого, мы в нее можем отправить и другие параметры - category, subcategory, item_id,
# Поэтому ловим все остальное в **kwargs
async def list_categories(message: Union[CallbackQuery, Message], **kwargs):
    # Клавиатуру формируем с помощью следующей функции (где делается запрос в базу данных)
    markup = await categories_keyboard("customer")

    # Проверяем, что за тип апдейта. Если Message - отправляем новое сообщение
    if isinstance(message, Message):
        await message.answer("Меню магазина", reply_markup=markup)

    # Если CallbackQuery - изменяем это сообщение
    elif isinstance(message, CallbackQuery):
        call = message
        await call.message.edit_text(text="Меню магазина", reply_markup=markup)


# Функция, которая отдает кнопки с подкатегориями, по выбранной пользователем категории
async def list_subcategories(callback: CallbackQuery, category, **kwargs):
    markup = await subcategories_keyboard(category, "customer")

    # Изменяем сообщение, и отправляем новые кнопки с подкатегориями
    await callback.message.edit_reply_markup(markup)


# Функция, которая отдает кнопки с Названием и ценой товара, по выбранной категории и подкатегории
async def list_items(callback: CallbackQuery, category, subcategory, **kwargs):
    markup = await items_keyboard(category, subcategory, "customer")

    # Изменяем сообщение, и отправляем новые кнопки с подкатегориями
    await callback.message.edit_text(text="Меню магазина", reply_markup=markup)


# Функция, которая отдает уже кнопку Купить товар по выбранному товару
async def show_item(callback: CallbackQuery, category, subcategory, item_id):
    markup = item_keyboard(category, subcategory, item_id, "customer")

    # Берем запись о нашем товаре из базы данных
    item = await get_item(item_id)
    text = f"Купи {item.name}"
    await callback.message.edit_text(text=text, reply_markup=markup)


# Функция, которая обрабатывает ВСЕ нажатия на кнопки в этой менюшке
@dp.callback_query_handler(menu_cd.filter())
async def navigate(call: CallbackQuery, callback_data: dict):
    """

    :param call: Тип объекта CallbackQuery, который прилетает в хендлер
    :param callback_data: Словарь с данными, которые хранятся в нажатой кнопке
    """

    # Получаем текущий уровень меню, который запросил пользователь
    current_level = callback_data.get("level")

    # Получаем категорию, которую выбрал пользователь (Передается всегда)
    category = callback_data.get("category")

    # Получаем подкатегорию, которую выбрал пользователь (Передается НЕ ВСЕГДА - может быть 0)
    subcategory = callback_data.get("subcategory")

    # Получаем айди товара, который выбрал пользователь (Передается НЕ ВСЕГДА - может быть 0)
    item_id = int(callback_data.get("item_id"))

    # Прописываем "уровни" в которых будут отправляться новые кнопки пользователю
    levels = {
        "0": list_categories,
        "1": list_subcategories, 
        "2": list_items,
        "3": show_item,
        "10": list_categories_edit,
        "11": list_subcategories_edit,
        "12": list_items_edit,
        "13": show_item_edit,
        "14": edit_name,
        "15": edit_price,
        "16": edit_description,
        "20": list_categories_new,
        "21": list_subcategories_new,
        #"22": new_item,
        "99": admin_keyboard
    }

    # Забираем нужную функцию для выбранного уровня
    current_level_function = levels[current_level]

    # Выполняем нужную функцию и передаем туда параметры, полученные из кнопки
    await current_level_function(
        call,
        category=category,
        subcategory=subcategory,
        item_id=item_id
    )


# Хендлер на команду /admin
@dp.message_handler(Command("admin"))
async def show_admin_menu(message: types.Message):
    # Клавиатуру формируем с помощью следующей функции с аргументом администратор
    markup = await admin_keyboard()
    await message.answer("Меню администратора", reply_markup=markup)

#Функции с категориями, подкатегориями и товарами редактирования
async def list_categories_edit(callback: CallbackQuery, **kwargs):
    markup = await categories_keyboard("edit")
    text = "Меню редактирования товара"
    await callback.message.edit_text(text=text, reply_markup=markup)

async def list_subcategories_edit(callback: CallbackQuery, category, **kwargs):
    markup = await subcategories_keyboard(category, "edit")
    await callback.message.edit_reply_markup(markup)

async def list_items_edit(callback: CallbackQuery, category, subcategory, **kwargs):
    markup = await items_keyboard(category, subcategory, "edit")
    await callback.message.edit_reply_markup(markup)

#Функции для редактирования товара
async def show_item_edit(message: Union[CallbackQuery, Message], category, subcategory, item_id):
    items = await count_all()
    if item_id > items:
        itemz = await get_items(category, subcategory)
        item = itemz[1]
        await add_item(id=(items + 1), name=" ",
                   category_name=f"{item.category_name}", category_code=f"{item.category_code}",
                   subcategory_name=f"{item.subcategory_name}", subcategory_code=f"{item.subcategory_code}",
                   price=1, photo="-", description="Описание товара")
        item_id = items + 1
    item = await get_item(item_id)
    name = f"{item.name}"
    price = f"{item.price}"
    description = f"{item.description}"
    markup = item_edit_keyboard(category, subcategory, item_id, name, price, description)
    if isinstance(message, Message):
        await message.answer(f"Редактирование {item.name}", reply_markup=markup)
    elif isinstance(message, CallbackQuery):
        callback = message
        text = f"Редактирование {item.name}"
        await callback.message.edit_text(text=text, reply_markup=markup)
    

async def edit_name(callback: CallbackQuery, category, subcategory, item_id):
    await callback.message.answer(text="Введите новое имя:")
    await EditState.name.set()
    state = Dispatcher.get_current().current_state()
    await state.update_data(category=category, subcategory=subcategory, item_id=item_id)

@dp.message_handler(state=EditState.name, content_types=types.ContentTypes.TEXT)
async def edit_name_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item = await get_item(data['item_id'])
    await item.update(name=message.text).apply()
    await state.finish()
    await show_item_edit(message, data['category'], data['subcategory'], data['item_id'])

async def edit_price(callback: CallbackQuery, category, subcategory, item_id):
    await callback.message.answer(text="Введите новую цену:")
    await EditState.price.set()
    state = Dispatcher.get_current().current_state()
    await state.update_data(category=category, subcategory=subcategory, item_id=item_id)

@dp.message_handler(state=EditState.price, content_types=types.ContentTypes.TEXT)
async def edit_price_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item = await get_item(data['item_id'])
    await item.update(price=int(message.text)).apply()
    await state.finish()
    await show_item_edit(message, data['category'], data['subcategory'], data['item_id'])

async def edit_description(callback: CallbackQuery, category, subcategory, item_id):
    await callback.message.answer(text="Введите новое описание:")
    await EditState.description.set()
    state = Dispatcher.get_current().current_state()
    await state.update_data(category=category, subcategory=subcategory, item_id=item_id)

@dp.message_handler(state=EditState.description, content_types=types.ContentTypes.TEXT)
async def edit_description_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item = await get_item(data['item_id'])
    await item.update(description=message.text).apply()
    await state.finish()
    await show_item_edit(message, data['category'], data['subcategory'], data['item_id'])

# Функции с категориями, подкатегориями и товарами для создания товара

async def list_categories_new(callback: CallbackQuery, **kwargs):
    markup = await categories_keyboard("new")
    text = "Меню редактирования товара"
    await callback.message.edit_text(text=text, reply_markup=markup)

async def list_subcategories_new(callback: CallbackQuery, category, **kwargs):
    markup = await subcategories_keyboard(category, "new")
    await callback.message.edit_reply_markup(markup)

#async def new_item(callback: CallbackQuery, category, subcategory, **kwargs):
