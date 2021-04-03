import asyncio
#from utils.db_api.db_commands import get_subcategories, count_items, get_items, get_categories
from utils.db_api.json_commands import get_subcategories, count_items, get_items, get_categories
from typing import List

trans = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zch', 
'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 
'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'c', 'ч': 'ch', 'ш': 'sh', 
'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya', 
'a': 'a', 'b':'b', 'c':'c', 'e':'e', 'f':'f', 'g':'g', 'h':'h', 'i':'i', 'j':'j', 'k':'k', 
'l': 'l', 'm': 'm', 'n': 'n', 'o': 'o', 'p': 'p', 'q': 'q', 'r': 'r', 's': 's', 't': 't', 'u': 'u', 
'v': 'v', 'w': 'w', 'x': 'x', 'y': 'y', 'z': 'z', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', 
'6': '6', '7': '7', '8': '8', '9': '9', '0': '0'}


def translate(word):
    for i in word:
        if i in trans:
            word = word.replace(i, trans[i], 1)
    else:
        word.replace(i, "")
    return word 

def repite_cat(word, con, category, subcategory):
    if con == "category":
        if word in category:
            try:
                num = int(word[4:len(word)])
                num = num + 1
                word = word[:4] + str(num)
            except:
                word = word + '1'
            if word in category:
                    word = repite_cat(word, con, category, subcategory)
    elif con == "subcategory":
        if word in subcategory:
            try:
                num = int(word[4:len(word)])
                num = num + 1
                word = word[:4] + str(num)
            except:
                word = word + '1'
            if word in subcategory:
                    word = repite_cat(word, con, category, subcategory)
    else:
        return "error"
    return word
    
async def codeformer(word, con, category=None):
    listcat = []
    listsub = []
    word = word.lower()
    if len(word) > 4:
        word = word[:4]
    word = translate(word)
    if con == "category":
        categories = await get_categories()
        for cat in categories:
            print(cat)
            listcat.append(f"{cat.category_code}")
    elif con == "subcategory":
        categories = await get_categories()
        for cat in categories:
            print(cat)
            subcategories = await get_subcategories(f"{cat.category_code}")
            for subcategory in subcategories:
                listcat.append(f"{subcategory.subcategory_code}")
    else:
        return error
    word = repite_cat(word, con, listcat, listsub)

    return word

def get_id(number, place):
    while True:
        if number not in place:
            break
        else:
            number += 1
    return number