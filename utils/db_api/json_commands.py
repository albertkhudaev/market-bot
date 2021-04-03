import json
import asyncio
from aiofile import AIOFile

class Item(dict):
    def __init__(self, item):
        self.item = item
        self.id = item["id"]
        self.name = item["name"]
        self.category_name = item["category_name"]
        self.category_code = item["category_code"]
        self.subcategory_name = item["subcategory_name"]
        self.subcategory_code = item["subcategory_code"]
        self.price = item["price"]
        self.photo = item["photo"]
        self.description = item["description"]

async def aswriter(data):
    async with AIOFile("./utils/database.json", "w+") as f:
        await f.write(data)

async def asreader():
    async with AIOFile("./utils/database.json", "r") as f:
        data = json.loads(await f.read())
    return data

async def add_item(**kwargs):
    data = await asreader()
    data[kwargs["id"]] = kwargs
    data = json.dumps(data)
    await aswriter(data)

async def count_all():
    return(len(await asreader()))

async def count_items(category_code, subcategory_code=None):
    data = await asreader()
    numer = 0
    if subcategory_code:
        for i in range(len(data)):
            i = str(i + 1)
            if data[i]["category_code"] == category_code and data[i]["subcategory_code"] == subcategory_code:
                numer += 1
    else:
        for i in range(len(data)):
            i = str(i + 1)
            if data[i]["category_code"] == category_code:
                numer += 1
    return numer

async def get_categories():
    data = await asreader()
    categories = []
    items = []
    for i in range(len(data)):
        i = str(i + 1)
        if data[i]["category_name"] not in categories:
            categories.append(data[i]["category_name"])
            items.append(Item(data[i]))
    return items

async def get_subcategories(category_code):
    data = await asreader()
    subcategories = []
    items = []
    for i in range(len(data)):
        i = str(i + 1)
        if data[i]["subcategory_name"] not in subcategories and data[i]["category_code"] == category_code:
            subcategories.append(data[i]["subcategory_name"])
            items.append(Item(data[i]))
    return items

async def get_items(category_code, subcategory_code):
    data = await asreader()
    items = []
    for i in range(len(data)):
        i = str(i + 1)
        if data[i]["category_code"] == category_code and data[i]["subcategory_code"] == subcategory_code:
            items.append(Item(data[i]))
    return items

async def get_item(item_id):
    data = await asreader()
    return Item(data[str(item_id)])

async def get_all_items():
    data = await asreader()
    all_items = []
    for i in range(len(data)):
        i = str(i + 1)
        all_items.append(data[i])
    return all_items

async def delete_item(item_id):
    data = await asreader()
    del data[str(item_id)]
    data = json.dumps(data)
    await aswriter(data)

