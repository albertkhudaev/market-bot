from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, Chat

from states import EditState, NewState, NewAdminState, BuyItemState
from keyboards.inline.menu_keyboards import menu_cd, categories_keyboard, subcategories_keyboard, \
    items_keyboard, item_keyboard, admin_keyboard, item_edit_keyboard, delete_question_keyboard
from loader import dp
from utils.db_api.db_commands import get_item, count_all, get_items, add_item, delete_item, get_all_items
from loader import storage
from utils.misc.translate import codeformer, get_id
from data.config import super_id, admins
from loader import bot


# Хендлер на команду /menu
@dp.message_handler(Command("menu"))
async def show_menu(message: types.Message):
    # Выполним функцию, которая отправит пользователю кнопки с доступными категориями
    await list_categories(message)

@dp.message_handler(Text("Показать меню"))
async def show_menu(message: types.Message):
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
async def list_subcategories(callback: CallbackQuery, category, cat_name, **kwargs):
    markup = await subcategories_keyboard(category, cat_name, "customer")

    # Изменяем сообщение, и отправляем новые кнопки с подкатегориями
    await callback.message.edit_text(text="Меню магазина", reply_markup=markup)


# Функция, которая отдает кнопки с Названием и ценой товара, по выбранной категории и подкатегории
async def list_items(callback: CallbackQuery, category, cat_name, subcategory, **kwargs):
    markup = await items_keyboard(category, subcategory, "customer")
    # Изменяем сообщение, и отправляем новые кнопки с товарами
    if cat_name == "photo":
        await callback.message.answer(text="Меню магазина", reply_markup=markup)
    else:
        await callback.message.edit_text(text="Меню магазина", reply_markup=markup)


# Функция, которая отдает уже кнопку Купить товар по выбранному товару
async def show_item(callback: CallbackQuery, category, subcategory, item_id, **kwargs):
    # Берем запись о нашем товаре из базы данных
    item = await get_item(item_id)
    text = f"{item.name} \n{item.description}"
    photo = f"{item.photo}"
    if item.photo != "-":
        markup = item_keyboard(category, subcategory, item_id, "photo")
        await callback.message.answer_photo(photo=photo, caption=text, reply_markup=markup)
    else:
        markup = item_keyboard(category, subcategory, item_id, "customer")
        await callback.message.edit_text(text=text, reply_markup=markup)

async def buy_item(callback: CallbackQuery, item_id, **kwargs):
    await callback.message.answer("Как к вам можно обращаться?")
    await BuyItemState.name.set()
    state = Dispatcher.get_current().current_state()
    await state.update_data(item_id=item_id)

@dp.message_handler(state=BuyItemState.name, content_types=types.ContentTypes.TEXT)
async def buy_item_namestate(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите пожалуйста номер телефона для связи:")
    await BuyItemState.telephone.set()

@dp.message_handler(state=BuyItemState.telephone, content_types=types.ContentTypes.TEXT)
async def buy_item_telephonestate(message: types.Message, state: FSMContext):
    await state.update_data(telephone=message.text)
    data = await state.get_data()
    await message.answer("Спасибо! Мы с вами скоро свяжемся")
    await state.finish()
    item = await get_item(data['item_id'])
    for admin in admins:
        await bot.send_message(admin, f"{data['name']} хочет купить {item.name} за {item.price}$. \n Номер телефона: {data['telephone']}")

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
        "4": buy_item,
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
        "80": admin_add,
        "81": admin_del,
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
async def show_admin_menu(message: Message):
    if str(message.chat.id) in admins:
        # Клавиатуру формируем с помощью следующей функции с аргументом администратор
        markup = await admin_keyboard()
        await message.answer("Меню администратора", reply_markup=markup)
    else:
        await message.answer("Недостаточно прав")

#Функции с категориями, подкатегориями и товарами редактирования
async def list_categories_edit(callback: CallbackQuery, **kwargs):
    if str(callback.message.chat.id) in admins:
        markup = await categories_keyboard("edit")
        await callback.message.edit_text(text="Меню редактирования товара", reply_markup=markup)
    else:
        await callback.message.edit_text(text="Недостаточно прав")

async def list_subcategories_edit(callback: CallbackQuery, category, cat_name, **kwargs):
    if str(callback.message.chat.id) in admins:
        markup = await subcategories_keyboard(category, cat_name, "edit")
        await callback.message.edit_text(text="Меню редактирования товара", reply_markup=markup)
    else:
        await callback.message.edit_text(text="Недостаточно прав")

async def list_items_edit(callback: CallbackQuery, category, subcategory, **kwargs):
    if str(callback.message.chat.id) in admins:
        markup = await items_keyboard(category, subcategory, "edit")
        await callback.message.edit_text(text="Меню редактирования товара", reply_markup=markup)
    else:
        await callback.message.edit_text(text="Недостаточно прав")

#Функции для редактирования товара
async def show_item_edit(message: Union[CallbackQuery, Message, InputMediaPhoto], category, cat_name, subcategory, subcat_name, item_id, new):
    items = await count_all()
    all_id = []
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
        all_items = await get_all_items()
        for item in all_items:
            all_id.append(item.id)
        next_id = get_id(1, all_id)
        await add_item(id=next_id, name=" ",
                   category_name=category_name, category_code=category_code,
                   subcategory_name=subcategory_name, subcategory_code=subcategory_code,
                   price=1, photo="-", description="Описание товара")
        item_id = next_id
    item = await get_item(item_id)
    name = f"{item.name}"
    price = f"{item.price}"
    description = f"{item.description}"
    photo = f"{item.photo}"
    markup = item_edit_keyboard(category, subcategory, item_id, name, price, description, photo)
    if isinstance(message, Message):
        if str(message.chat.id) in admins:
            await message.answer(f"Редактирование {item.name}", reply_markup=markup)
        else:
            await message.answer("Недостаточно прав")
    elif isinstance(message, InputMediaPhoto):
        if str(message.chat.id) in admins:
            await message.answer(f"Редактирование {item.name}", reply_markup=markup)
        else:
            await message.answer("Недостаточно прав")
    elif isinstance(message, CallbackQuery):
        callback = message
        if str(callback.message.chat.id) in admins:
            text = f"Редактирование {item.name}"
            await callback.message.edit_text(text=text, reply_markup=markup)
        else:
            await callback.message.edit_text(text="Недостаточно прав")
    

async def edit_name(callback: CallbackQuery, category, cat_name, subcategory, subcat_name, item_id, new):
    if str(callback.message.chat.id) in admins:
        await callback.message.edit_text(text="Введите новое имя:")
        await EditState.name.set()
        state = Dispatcher.get_current().current_state()
        await state.update_data(category=category, cat_name=cat_name, subcategory=subcategory, subcat_name=subcat_name, item_id=item_id, new=new)
    else:
        await callback.message.edit_text(text="Недостаточно прав")

@dp.message_handler(state=EditState.name, content_types=types.ContentTypes.TEXT)
async def edit_name_handler(message: types.Message, state: FSMContext):
    if str(message.chat.id) in admins:
        data = await state.get_data()
        item = await get_item(data['item_id'])
        await item.update(name=message.text).apply()
        await state.finish()
        await show_item_edit(message, data['category'], data['cat_name'], data['subcategory'], data['subcat_name'], data['item_id'], data['new'])
    else:
        await message.answer("Недостаточно прав")
        await state.finish()

async def edit_price(callback: CallbackQuery, category, cat_name, subcategory, subcat_name, item_id, new):
    if str(callback.message.chat.id) in admins:
        await callback.message.answer(text="Введите новую цену:")
        await EditState.price.set()
        state = Dispatcher.get_current().current_state()
        await state.update_data(category=category, cat_name=cat_name, subcategory=subcategory, subcat_name=subcat_name, item_id=item_id, new=new)
    else:
        await callback.message.edit_text(text="Недостаточно прав")
        await state.finish()

@dp.message_handler(state=EditState.price, content_types=types.ContentTypes.TEXT)
async def edit_price_handler(message: types.Message, state: FSMContext):
    if str(message.chat.id) in admins:
        data = await state.get_data()
        item = await get_item(data['item_id'])
        await item.update(price=int(message.text)).apply()
        await state.finish()
        await show_item_edit(message, data['category'], data['cat_name'], data['subcategory'], data['subcat_name'], data['item_id'], data['new'])
    else:
        await message.answer("Недостаточно прав")
        await state.finish()

async def edit_description(callback: CallbackQuery, category, cat_name, subcategory, subcat_name, item_id, new):
    if str(callback.message.chat.id) in admins:
        await callback.message.answer(text="Введите новое описание:")
        await EditState.description.set()
        state = Dispatcher.get_current().current_state()
        await state.update_data(category=category, cat_name=cat_name, subcategory=subcategory, subcat_name=subcat_name, item_id=item_id, new=new)
    else:
        await callback.message.edit_text(text="Недостаточно прав")

@dp.message_handler(state=EditState.description, content_types=types.ContentTypes.TEXT)
async def edit_description_handler(message: types.Message, state: FSMContext):
    if str(message.chat.id) in admins:
        data = await state.get_data()
        item = await get_item(data['item_id'])
        await item.update(description=message.text).apply()
        await state.finish()
        await show_item_edit(message, data['category'], data['cat_name'], data['subcategory'], data['subcat_name'], data['item_id'], data['new'])
    else:
        await message.answer("Недостаточно прав")
        await state.finish()


async def edit_photo(callback: CallbackQuery, category, cat_name, subcategory, subcat_name, item_id, new):
    if str(callback.message.chat.id) in admins:
        await callback.message.answer(text="Отправьте новое фото:")
        await EditState.photo.set()
        state = Dispatcher.get_current().current_state()
        await state.update_data(category=category, cat_name=cat_name, subcategory=subcategory, subcat_name=subcat_name, item_id=item_id, new=new)
    else:
        await callback.message.edit_text(text="Недостаточно прав")


@dp.message_handler(state=EditState.photo, content_types=['photo'])
async def edit_photo_handler(message: InputMediaPhoto, state: FSMContext):
    data = await state.get_data()
    item = await get_item(data['item_id'])
    photo_id = message.photo[0].file_id
    await item.update(photo=photo_id).apply()
    await state.finish()
    await show_item_edit(message, data['category'], data['cat_name'], data['subcategory'], data['subcat_name'], data['item_id'], data['new'])

# Функции с категориями, подкатегориями и товарами для создания товара

async def list_categories_new(callback: CallbackQuery, **kwargs):
    if str(callback.message.chat.id) in admins:
        markup = await categories_keyboard("new")
        await callback.message.edit_text(text="Меню редактирования товара", reply_markup=markup)
    else:
        await callback.message.edit_text(text="Недостаточно прав")

async def list_subcategories_new(callback: CallbackQuery, category, cat_name, **kwargs):
    if str(callback.message.chat.id) in admins:
        markup = await subcategories_keyboard(category, cat_name, "new")
        await callback.message.edit_text(text="Меню редактирования товара", reply_markup=markup)
    else:
        await callback.message.edit_text(text="Недостаточно прав")

async def new_category(callback: CallbackQuery, **kwargs):
    if str(callback.message.chat.id) in admins:
        await callback.message.edit_text(text="Введите имя категории:")
        await NewState.newcat.set()
    else:
        await callback.message.edit_text(text="Недостаточно прав")

@dp.message_handler(state=NewState.newcat, content_types=types.ContentTypes.TEXT)
async def new_category_handler(message: types.Message, state: FSMContext):
    if str(message.chat.id) in admins:
        cat_name = str(message.text)
        category = await codeformer(message.text, "category")
        await state.finish()
        await new_subcategory(message, category, cat_name)
    else:
        await message.answer("Недостаточно прав")
        await state.finish()

async def new_subcategory(message: Union[CallbackQuery, Message], category, cat_name, **kwargs):
    if isinstance(message, Message):
        if str(message.chat.id) in admins:
            await message.answer("Введите имя подкатегории")
        else:
            await message.answer("Недостаточно прав")
            return
    elif isinstance(message, CallbackQuery):
        if str(message.message.chat.id) in admins:
            await message.message.edit_text(text="Введите имя подкатегории:")
        else:
            await message.message.edit_text(text="Недостаточно прав")
            return
    await NewState.newsubcat.set()
    state = Dispatcher.get_current().current_state()
    await state.update_data(category=category, cat_name=cat_name)

@dp.message_handler(state=NewState.newsubcat, content_types=types.ContentTypes.TEXT)
async def new_category_handler(message: types.Message, state: FSMContext):
    if str(message.chat.id) in admins:
        data = await state.get_data()
        subcat_name = str(message.text)
        subcategory = await codeformer(message.text, "subcategory", category=data['category'])
        item_id = (await count_all()) + 1
        new = True
        await state.finish()
        await show_item_edit(message, data['category'], data['cat_name'], subcategory, subcat_name, item_id, new)
    else:
        await message.answer("Недостаточно прав")
        await state.finish()

async def list_categories_delete(callback: CallbackQuery, **kwargs):
    if str(callback.message.chat.id) in admins:
        markup = await categories_keyboard("del")
        await callback.message.edit_text(text="Меню удаления товара", reply_markup=markup)
    else:
        await callback.message.edit_text(text="Недостаточно прав")

async def list_subcategories_delete(callback: CallbackQuery, category, cat_name, **kwargs):
    if str(callback.message.chat.id) in admins:
        markup = await subcategories_keyboard(category, cat_name, "del")
        await callback.message.edit_text(text="Меню удаления товара", reply_markup=markup)
    else:
        await callback.message.edit_text(text="Недостаточно прав")

async def list_items_delete(callback: CallbackQuery, category, subcategory, **kwargs):
    if str(callback.message.chat.id) in admins:
        markup = await items_keyboard(category, subcategory, "del")
        await callback.message.edit_text(text="Меню удаления товара", reply_markup=markup)
    else:
        await callback.message.edit_text(text="Недостаточно прав")

async def item_question_delete(callback: CallbackQuery, category, subcategory, item_id, **kwargs):
    if str(callback.message.chat.id) in admins:
        markup = delete_question_keyboard(category, subcategory, item_id)
        await callback.message.edit_text(text="Вы уверены что хотите удалить товар?", reply_markup=markup)
    else:
        await callback.message.edit_text(text="Недостаточно прав")

async def item_yes_delete(callback: CallbackQuery, item_id, **kwargs):
    if str(callback.message.chat.id) in admins:
        await delete_item(item_id)
        markup = await admin_keyboard()
        await callback.message.edit_text(text="Меню администратора", reply_markup=markup)
    else:
        await callback.message.edit_text(text="Недостаточно прав")

async def admin_panel(callback: CallbackQuery, **kwargs):
    if str(callback.message.chat.id) in admins:
        markup = await admin_keyboard()
        await callback.message.edit_text(text="Меню администратора", reply_markup=markup)
    else:
        await callback.message.edit_text(text="Недостаточно прав")

async def admin_add(callback: CallbackQuery, **kwargs):
    if str(callback.message.chat.id) == super_id:
        await callback.message.edit_text(text="Введите chat id администратора:")
        await NewAdminState.newadmin.set()
    else:
        print(callback.message.chat.id)
        await callback.message.edit_text(text="Недостаточно прав")

@dp.message_handler(state=NewAdminState.newadmin, content_types=types.ContentTypes.TEXT)
async def new_category_handler(message: types.Message, state: FSMContext):
    new_admin_id = str(message.text)
    admins.append(new_admin_id)
    print(admins)
    await message.answer(text=f"Администратор с id {new_admin_id} добавлен!")
    await state.finish()

async def admin_del(callback: CallbackQuery, **kwargs):
    if str(callback.message.chat.id) == super_id:
        await callback.message.edit_text(text="Введите chat id администратора:")
        await NewAdminState.deladmin.set()
    else:
        print(callback.message.chat.id)
        await callback.message.edit_text(text="Недостаточно прав")

@dp.message_handler(state=NewAdminState.deladmin, content_types=types.ContentTypes.TEXT)
async def new_category_handler(message: types.Message, state: FSMContext):
    new_admin_id = str(message.text)
    admins.remove(new_admin_id)
    print(admins)
    await message.answer(text=f"Администратор с id {new_admin_id} удален!")
    await state.finish()
