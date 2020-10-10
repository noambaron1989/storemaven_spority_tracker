import logging

import mysql
from mysql.connector import MySQLConnection

from models import category_manager_model, spotify_tracker_model
from src import constants


class DataProvider:
    def __init__(self, _logger):
        self.logger = _logger
        self.mydb = None

    def create_connection(self):
        user = constants.db_user
        password = constants.db_password
        ip = constants.msql_ip
        port = constants.mysql_port
        db_name = constants.db_name

        self.logger.info('connecting to db %s ip:%s port:%s', db_name, ip, port)
        self.mydb = mysql.connector.connect(
            host=ip,
            port=port,
            user=user,
            passwd=password,
            database=db_name,

        )
        self.mydb.set_charset_collation('utf8mb4', 'utf8mb4_unicode_ci')

    def close_connection(self):
        if self.mydb:
            try:
                connection_id = self.mydb.connection_id
                self.logger.info('closing db connection ID : %s', connection_id)
                self.mydb.close()
            except Exception as error:
                self.logger.error('failed disconnecting from db due to %s', error)

    def create_table_from_schema(self, model):
        cursor = self.mydb.cursor()

        sql_query = "CREATE TABLE if not exists %s (" % model.table_name
        column_count = 0
        for column in model.model_schema:
            column_count += 1
            sql_query += "%s " % column['name']
            sql_query += "%s" % column['type']
            if 'rule' in column:
                sql_query += " %s" % column['rule']
            if column_count < len(model.model_schema):
                sql_query += ","
        sql_query += ")"

        execute = cursor.execute(sql_query)
        cursor.close()
        return execute

    def insert_batch_to_table(self, table_name, rows_dict_list):
        # TODO: need to insert in batchs of 5000

        self.logger.info('inserting %s records into table %s...', len(rows_dict_list), table_name)
        example_row = rows_dict_list[0]
        cursor = self.mydb.cursor()

        columns_name = ""

        row_count = 1
        for key in example_row.keys():
            columns_name += key
            if row_count < len(example_row):
                columns_name += ","
            row_count += 1

        values = []

        for curr_row_dict in rows_dict_list:
            row_list = []
            for curr_value in curr_row_dict.values():
                try:
                    # TODO: this is a workaround for bug Incorrect string value: '\xE2\x88\x9E\xE2\x88\x9E...
                    #  need to find solution and find a way to configure db to charset='utf8mb4''
                    if hasattr(cursor, '_cnx'):
                        cursor._cnx.prepare_for_mysql(curr_value)
                    row_list.append(curr_value)
                except Exception as e:
                    self.logger.debug('failed to convert value %s to mysql due to %s - skipping this value!', curr_value, e)
            values.append(tuple(row_list))

        sql_query = "INSERT INTO %s ( %s ) VALUES ( %s )" % \
                    (table_name, columns_name, ("%s," * len(example_row))[:-1])

        cursor.executemany(sql_query, values)
        self.mydb.commit()
        rows_effected = cursor.rowcount
        self.logger.info('%s records where effected by last query', row_count)
        cursor.close()

        return rows_effected

    def insert_record_to_table(self, table_name, record):
        self.logger.info('inserting record into table %s...', table_name)

        cursor = self.mydb.cursor()

        columns_name = ""
        values = []
        row_count = 1
        for key, value in record.items():
            values.append(value)
            columns_name += key
            if row_count < len(record):
                columns_name += ","
            row_count += 1

        sql_query = "INSERT INTO %s ( %s ) VALUES ( %s )" % \
                    (table_name, columns_name, ("%s," * len(record))[:-1])

        cursor.execute(sql_query, tuple(values))
        self.mydb.commit()
        rows_effected = cursor.rowcount
        self.logger.info('%s records where effected by last query', rows_effected)
        cursor.close()

        return rows_effected

    def get_records_from_table(self, table_name, fields='*', where_values=None):
        cursor = self.mydb.cursor()

        sql_query = "SELECT %s from %s" % (fields, table_name)
        if where_values:
            sql_query += " %s" % where_values

        cursor.execute(sql_query)

        records = cursor.fetchall()

        to_return = []

        for rec in records:
            _job = {}
            i = 0
            for col in cursor.column_names:
                _job[col] = rec[i]
                i += 1
            to_return.append(_job)
        self.mydb.commit()
        cursor.close()

        return to_return

    def delete_record_from_table(self, table_name, where_value):
        self.logger.info('deleting record from table %s...', table_name)

        cursor = self.mydb.cursor()

        sql_query = "DELETE FROM %s WHERE %s" % (table_name, where_value)

        cursor.execute(sql_query)
        self.mydb.commit()
        rows_effected = cursor.rowcount
        self.logger.info('%s records where effected by last query', rows_effected)
        cursor.close()

    def update_record_in_table(self, table_name, set_value, where_value):
        self.logger.info('updating record in table %s...', table_name)

        cursor = self.mydb.cursor()

        sql_query = "UPDATE %s SET %s WHERE %s" % (table_name, set_value, where_value)

        cursor.execute(sql_query)
        self.mydb.commit()
        rows_effected = cursor.rowcount
        self.logger.info('%s records where effected by last query', rows_effected)
        cursor.close()


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)

    db = DataProvider(logger)
    db.create_connection()

    db.create_table_from_schema(category_manager_model)
    db.create_table_from_schema(spotify_tracker_model)

    db.close_connection()
