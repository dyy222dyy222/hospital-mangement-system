import logging

FETCH_MED = """
    select * from medicine
"""

INSERT = """INSERT INTO medicine VALUES({fda_id}, '{name}', {retail_price}, '{prescription_required}', {current_stock})"""

MAX_ID_MED = """SELECT MAX(fda_id) FROM medicine"""

def fetch_medicines():
    query = FETCH_MED
    return query

def add_medicine(med_ref, args):
    add_med = INSERT
    add_med = add_med.format(fda_id = str(int(med_ref) + 1), name = args['name'], retail_price = args['retail_price'], prescription_required = args['prescription_required'], current_stock = args['current_stock'])
    return add_med