import asyncio
from utils.db_api.db_commands import get_subcategories, count_items, get_items, get_categories
from typing import List

trans = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zch', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 'y', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'}


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
        for category in categories:
            listcat.append(f"{category.category_code}")
    elif con == "subcategory":
        subcategories = await get_subcategories(category)
        for subcategory in subcategories:
            listcat.append(f"{subcategory.subcategory_code}")
    else:
        return error
    word = repite_cat(word, con, listcat, listsub)

    return word

##############################################################################################
#result = await codeformer("привет", "subcategory", "Electronics")
#print(result)