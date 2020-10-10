import time

table_name = 'category_manager'

key_category_id = 'category_id'
key_category_name = 'categoryName'
key_create_date = 'createDate'
key_track_date = 'trackDate'

model_schema = [
    {
        "name": key_category_id,
        "type": "varchar(100)",
        "rule": "PRIMARY KEY"
    }, {
        "name": key_category_name,
        "type": "varchar(100)"
    }, {
        "name": key_create_date,
        "type": "bigint"
    }, {
        "name": key_track_date,
        "type": "bigint"
    }
]


def create_category(category_id, category_name):
    return {
        key_category_id: category_id,
        key_category_name: category_name,
        key_create_date: int(time.time())
    }



