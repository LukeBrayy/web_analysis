import sqlite3
from sqlite3 import Error
import pandas as pd


def create_connection():
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect("scraped.db")
    except Error as e:
        print(e)

    return conn


def generic_query(sql, values):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    conn = create_connection()
    with conn:
        cur = conn.cursor()
        cur.execute(sql, values)
        rows = cur.fetchall()
    return rows

def generic_insert(sql, values):
    conn = create_connection()
    with conn:
        cur = conn.cursor()
        cur.execute(sql, values)
        conn.commit()
    return

def order_rows(headers, data):
    return [data.get(header, "") for header in headers]

def rows_to_dict(rows, headers):
    out = []
    for row in rows:
        out_row = {header:row[n] for n, header in enumerate(headers)}
        out.append(out_row)
    return out

def insert_gumtree(data):
    rows = ["url", "title", "price", "location", "main_description", "full_description", "date_listed", "last_edited", "seller_type", "variant", "kilometres", "transmission", "drive_train", "fuel_type", "colour", "air_conditioning", "registered", "registration_number", "first_photo", "year", "make", "model", "body_type", "search_name"]
    ordered_data  = order_rows(rows, data)
    formatted_fields = ",".join(rows)
    question_marks = ",".join(["?"]*len(rows))
    query = """
            INSERT INTO gumtree({})
            VALUES({})
            """.format(formatted_fields, question_marks)
    generic_insert(query, ordered_data)



def generic_query_gumtree(kms, price):
    headers = ["title", "price", "location", "variant", "kilometres", "transmission", "drive_train", "fuel_type", "main_description", "date_listed", "last_edited", "seller_type", "colour", "air_conditioning", "registered", "registration_number", "first_photo", "year", "make", "model", "body_type", "url", "search_name"]
    formatted_fields = ",".join(headers)
    if kms[1] == "*":
        kms[1] = 10000000000
    if price[1] == "*":
        price[1] = 1000000000

    query = """ SELECT {} FROM gumtree
        WHERE (? <= price) AND (price <= ?) AND (? <= kilometres) AND (kilometres <= ?) """.format(formatted_fields)
    rows = generic_query(query, (price[0], price[1], kms[0], kms[1],))

    new_rows = []
    for row in rows:
        new_row = []
        for n, item in enumerate(row):
            if n == 1:
                new_row.append("${}".format(str(item)))
            else:
                new_row.append(item)
        new_rows.append(new_row)
    return headers, new_rows


def make_all_not_still_on():
    query = """ UPDATE gumtree
                SET still_on = 0"""
    generic_query(query, ())


def set_still_on_for_car(car_url):
    query = """ UPDATE gumtree SET still_on=1 WHERE url = ? """
    generic_query(query, (car_url,))


def check_if_inserted(car_url):
    query = """ SELECT * FROM gumtree where url = ?"""
    rows = generic_query(query, (car_url,))
    # print(len(rows))
    if len(rows) > 0:
        set_still_on_for_car(car_url)
        return True
    return False


def export_csv():
    conn = sqlite3.connect("scraped.db", isolation_level=None,
                       detect_types=sqlite3.PARSE_COLNAMES)
    db_df = pd.read_sql_query("SELECT * FROM gumtree", conn)
    db_df.to_csv('automatic_scraped_export.csv', index=False)




if __name__ == "__main__":
    #generic_query_gumtree([80000, 200000000], [1, 5000000000])
    export_csv()
