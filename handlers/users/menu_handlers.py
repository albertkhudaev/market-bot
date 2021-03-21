from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from states import EditState, NewState
from keyboards.inline.menu_keyboards import menu_cd, categories_keyboard, subcategories_keyboard, \
    items_keyboard, item_keyboard, admin_keyboard, item_edit_keyboard, delete_question_keyboard
from loader import dp
from utils.db_api.db_commands import get_item, count_all, get_items, add_item, delete_item
from loader import storage
from utils.misc.translate import codeformer


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
        await call.message.answer(text="Меню магазина", reply_markup=markup)


# Функция, которая отдает кнопки с подкатегориями, по выбранной пользователем категории
async def list_subcategories(callback: CallbackQuery, category, cat_name, **kwargs):
    markup = await subcategories_keyboard(category, cat_name, "customer")

    # Изменяем сообщение, и отправляем новые кнопки с подкатегориями
    await callback.message.answer(text="Меню магазина", reply_markup=markup)


# Функция, которая отдает кнопки с Названием и ценой товара, по выбранной категории и подкатегории
async def list_items(callback: CallbackQuery, category, subcategory, **kwargs):
    markup = await items_keyboard(category, subcategory, "customer")

    # Изменяем сообщение, и отправляем новые кнопки с подкатегориями
    await callback.message.answer(text="Меню магазина", reply_markup=markup)


# Функция, которая отдает уже кнопку Купить товар по выбранному товару
async def show_item(callback: CallbackQuery, category, subcategory, item_id, **kwargs):
    markup = item_keyboard(category, subcategory, item_id, "customer")

    # Берем запись о нашем товаре из базы данных
    item = await get_item(item_id)
    text = f"Купи {item.name} \n{item.description}"
    photo = f"{item.photo}"
    if item.photo != "-":
        await callback.message.answer_photo(photo=photo, caption=text, reply_markup=markup)
    else:
        await callback.message.answer(text=text, reply_markup=markup)


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

    cat_name = callback_data.get("cat_name")

    # Получаем подкатегорию, которую выбрал пользователь (Передается НЕ ВСЕГДА - может быть 0)
    subcategory = callback_data.get("subcategory")

    subcat_name = callback_data.get("subcat_name")

    # Получаем айди товара, который выбрал пользователь (Передается НЕ ВСЕГДА - может быть 0)
    item_id = int(callback_data.get("item_id"))

    new = callback_data.get("new")

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
        "17": edit_photo,
        "20": list_categories_new,
        "21": list_subcategories_new,
        "22": new_category,
        "23": new_subcategory,
        "30": list_categories_delete,
        "31": list_subcategories_delete,
        "32": list_items_delete,
        "33": item_question_delete,
        "34": item_yes_delete,
        "99": admin_panel
    }

    # Забираем нужную функцию для выбранного уровня
    current_level_function = levels[current_level]

    # Выполняем нужную функцию и передаем туда параметры, полученные из кнопки
    await current_level_function(
        call,
        category=category,
        cat_name=cat_name,
        subcategory=subcategory,
        subcat_name=subcat_name,
        item_id=item_id,
        new=new
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
    await callback.message.answer(text="Меню редактирования товара", reply_markup=markup)

async def list_subcategories_edit(callback: CallbackQuery, category, cat_name, **kwargs):
    markup = await subcategories_keyboard(category, cat_name, "edit")
    await callback.message.answer(text="Меню редактирования товара", reply_markup=markup)

async def list_items_edit(callback: CallbackQuery, category, subcategory, **kwargs):
    markup = await items_keyboard(category, subcategory, "edit")
    await callback.message.answer(text="Меню редактирования товара", reply_markup=markup)

#Функции для редактирования товара
async def show_item_edit(message: Union[CallbackQuery, Message], category, cat_name, subcategory, subcat_name, item_id, new):
    items = await count_all()
    if item_id > items:
        if new:
            category_name = cat_name
            category_code = category
            subcategory_name = subcat_name
            subcategory_code = subcategory
        else:
            itemz = await get_items(category, subcategory)
            item = itemz[1]
            category_name = f"{item.category_name}"
            category_code = f"{item.category_code}"
            subcategory_name = f"{item.subcategory_name}"
            subcategory_code = f"{item.subcategory_code}"
        await add_item(id=(items + 1), name=" ",
                   category_name=category_name, category_code=category_code,
                   subcategory_name=subcategory_name, subcategory_code=subcategory_code,
                   price=1, photo="-", description="Описание товара")
        item_id = items + 1
    item = await get_item(item_id)
    name = f"{item.name}"
    price = f"{item.price}"
    description = f"{item.description}"
    markup = item_edit_keyboard(category, subcategory, item_id, name, price, description, photo)
    if isinstance(message, Message):
        await message.answer(f"Редактирование {item.name}", reply_markup=markup)
    elif isinstance(message, CallbackQuery):
        callback = message
        text = f"Редактирование {item.name}"
        await callback.message.answer(text=text, reply_markup=markup)
    

async def edit_name(callback: CallbackQuery, category, cat_name, subcategory, subcat_name, item_id, new):
    await callback.message.answer(text="Введите новое имя:")
    await EditState.name.set()
    state = Dispatcher.get_current().current_state()
    await state.update_data(category=category, cat_name=cat_name, subcategory=subcategory, subcat_name=subcat_name, item_id=item_id, new=new)

@dp.message_handler(state=EditState.name, content_types=types.ContentTypes.TEXT)
async def edit_name_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item = await get_item(data['item_id'])
    await item.update(name=message.text).apply()
    await state.finish()
    await show_item_edit(message, data['category'], data['cat_name'], data['subcategory'], data['subcat_name'], data['item_id'], data['new'])

async def edit_price(callback: CallbackQuery, category, cat_name, subcategory, subcat_name, item_id, new):
    await callback.message.answer(text="Введите новую цену:")
    await EditState.price.set()
    state = Dispatcher.get_current().current_state()
    await state.update_data(category=category, cat_name=cat_name, subcategory=subcategory, subcat_name=subcat_name, item_id=item_id, new=new)

@dp.message_handler(state=EditState.price, content_types=types.ContentTypes.TEXT)
async def edit_price_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item = await get_item(data['item_id'])
    await item.update(price=int(message.text)).apply()
    await state.finish()
    await show_item_edit(message, data['category'], data['cat_name'], data['subcategory'], data['subcat_name'], data['item_id'], data['new'])

async def edit_description(callback: CallbackQuery, category, cat_name, subcategory, subcat_name, item_id, new):
    await callback.message.answer(text="Введите новое описание:")
    await EditState.description.set()
    state = Dispatcher.get_current().current_state()
    await state.update_data(category=category, cat_name=cat_name, subcategory=subcategory, subcat_name=subcat_name, item_id=item_id, new=new)

@dp.message_handler(state=EditState.description, content_types=types.ContentTypes.TEXT)
async def edit_description_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item = await get_item(data['item_id'])
    await item.update(description=message.text).apply()
    await state.finish()
    await show_item_edit(message, data['category'], data['cat_name'], data['subcategory'], data['subcat_name'], data['item_id'], data['new'])


async def edit_photo(callback: CallbackQuery, category, cat_name, subcategory, subcat_name, item_id, new):
    await callback.message.answer(text="Отправьте новое фото:")
    await EditState.photo.set()
    state = Dispatcher.get_current().current_state()
    await state.update_data(category=category, cat_name=cat_name, subcategory=subcategory, subcat_name=subcat_name, item_id=item_id, new=new)


@dp.message_handler(state=EditState.photo, content_types=['photo'])
async def edit_photo_handler(message: types.InputMediaPhoto, state: FSMContext):
    data = await state.get_data()
    item = await get_item(data['item_id'])
    photo_id = message.photo[0].file_id
    await item.update(photo=photo_id).apply()
    await state.finish()
    await show_item_edit(message, data['category'], data['cat_name'], data['subcategory'], data['subcat_name'], data['item_id'], data['new'])

# Функции с категориями, подкатегориями и товарами для создания товара

async def list_categories_new(callback: CallbackQuery, **kwargs):
    markup = await categories_keyboard("new")
    await callback.message.answer(text="Меню редактирования товара", reply_markup=markup)

async def list_subcategories_new(callback: CallbackQuery, category, cat_name, **kwargs):
    markup = await subcategories_keyboard(category, cat_name, "new")
    await callback.message.answer(markup)

async def new_category(callback: CallbackQuery, **kwargs):
    await callback.message.answer(text="Введите имя категории:")
    await NewState.newcat.set()

@dp.message_handler(state=NewState.newcat, content_types=types.ContentTypes.TEXT)
async def new_category_handler(message: types.Message, state: FSMContext):
    cat_name = str(message.text)
    category = await codeformer(message.text, "category")
    await state.finish()
    await new_subcategory(message, category, cat_name)

async def new_subcategory(message: Union[CallbackQuery, Message], category, cat_name, **kwargs):
    if isinstance(message, Message):
        await message.answer("Введите имя подкатегории")
    elif isinstance(message, CallbackQuery):
        await message.message.answer(text="Введите имя подкатегории:")
    await NewState.newsubcat.set()
    state = Dispatcher.get_current().current_state()
    await state.update_data(category=category, cat_name=cat_name)

@dp.message_handler(state=NewState.newsubcat, content_types=types.ContentTypes.TEXT)
async def new_category_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    subcat_name = str(message.text)
    subcategory = await codeformer(message.text, "subcategory", category=data['category'])
    item_id = (await count_all()) + 1
    new = True
    await state.finish()
    await show_item_edit(message, data['category'], data['cat_name'], subcategory, subcat_name, item_id, new)

async def list_categories_delete(callback: CallbackQuery, **kwargs):
    markup = await categories_keyboard("del")
    await callback.message.answer(text="Меню удаления товара", reply_markup=markup)

async def list_subcategories_delete(callback: CallbackQuery, category, cat_name, **kwargs):
    markup = await subcategories_keyboard(category, cat_name, "del")
    await callback.message.answer(text="Меню удаления товара", reply_markup=markup)

async def list_items_delete(callback: CallbackQuery, category, subcategory, **kwargs):
    markup = await items_keyboard(category, subcategory, "del")
    await callback.message.answer(text="Меню удаления товара", reply_markup=markup)

async def item_question_delete(callback: CallbackQuery, category, subcategory, item_id, **kwargs):
    markup = delete_question_keyboard(category, subcategory, item_id)
    await callback.message.answer(text="Вы уверены что хотите удалить товар?", reply_markup=markup)

async def item_yes_delete(callback: CallbackQuery, item_id, **kwargs):
    await delete_item(item_id)
    markup = await admin_keyboard()
    await callback.message.answer("Меню администратора", reply_markup=markup)

async def admin_panel(callback: CallbackQuery, **kwargs):
    markup = await admin_keyboard()
    await callback.message.answer("Меню администратора", reply_markup=markup)