from data.config import dbsource
if dbsource == "pg":
    from .db_commands import count_items, get_items, get_categories