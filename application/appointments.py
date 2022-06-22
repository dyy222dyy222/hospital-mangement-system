import logging

SEARCH = """
    WITH APT AS(
SELECT
	*
FROM
	consult cs NATURAL JOIN 
	patient pt NATURAL JOIN 
	payment py NATURAL JOIN 
	advise ad NATURAL JOIN 
	doctor dr
)
SELECT
	APT.consult_id,
    APT.patient_id,
	APT.first_name,
	APT.last_name,
	APT.payment_ref_no,
	APT.consult_from,
	APT.consult_to,
	APT.consult_type,
	APT.insurance_id,
	APT.gender,
	APT.dob,
	APT.payment_status,
	APT.employee_id,
	APT.license_number
FROM 
	APT
WHERE
    {criteria} = {value}
ORDER BY APT.consult_from DESC
"""

CRITERIA = {
    "consult_id": "{}",
    "patient_id": "{}"
}

MEDS_PRESC = """
SELECT
	*
FROM
	prescription ps,
	medicine md,
    consult cs
WHERE
	ps.fda_id = md.fda_id
AND cs.consult_id = ps.consult_id
AND {criteria} = {value}  
"""

INSERT = {
    "payment": "INSERT INTO payment VALUES({payment_ref_no}, {amount}, {payment_status}, {is_insured}, now())",
    "consult": "INSERT INTO consult VALUES({consult_id}, '{consult_from}', '{consult_to}', '{consult_type}', {patient_id}, {payment_ref_no})",
    "advise": "INSERT INTO advise VALUES({employee_id}, {consult_id})"
}

MAX_ID_CONSULT = """SELECT MAX(consult_id) FROM consult"""
MAX_ID_PAY_REF = """SELECT MAX(payment_ref_no) FROM payment"""

UPDATE = { 
    "payment": """UPDATE payment SET amount = {amount}, payment_status = 'CONFIRMED', is_insured='true' , pay_date=now() WHERE payment_ref_no =  (
		select payment_ref_no
		from consult cs
		where cs.consult_id = {consult_id}
	)""",
    "prescription": "INSERT INTO prescription VALUES({consult_id},{fda_id})"
}

TRGIGGERS = {
    "meds": """
            UPDATE medicine M
            SET current_stock = current_stock - 1
            WHERE M.fda_id = {fda_id}
    """
}

def fetch_appointments(args):
    query = SEARCH
    if 'consult_id' in args and len(args['consult_id']) > 0:
        query = query.format(criteria = "APT.consult_id", value = args["consult_id"])
    elif 'patient_id' in args and len(args['patient_id']) > 0:
        query = query.format(criteria = "APT.patient_id", value = args["patient_id"])
    else :
        query = query.format(criteria = "1", value = "1")

    if 'limit' in args:
        query = query + " LIMIT 1"
    print(query)
    return query

def fetch_meds_prescribed(args):
    query = MEDS_PRESC
    if 'consult_id' in args and len(args['consult_id']) > 0:
        query = query.format(criteria = "cs.consult_id", value = args["consult_id"])
    elif 'patient_id' in args and len(args['patient_id']) > 0:
        query = query.format(criteria = "cs.patient_id", value = args["patient_id"])
    else: 
        query = query.format(criteria = "1", value = "1")
    print(query)
    return query

def book_payment(args, payment_ref):
    query_pay = INSERT['payment']
    query_pay = query_pay.format(payment_ref_no = str(int(payment_ref) + 1), amount = "1", payment_status = "'PENDING'", is_insured = "true")
    return query_pay

def book_apt(args, consult_idf, payment_ref):
    query_apt = INSERT['consult']
    query_apt = query_apt.format(consult_id = str(int(consult_idf) + 1), consult_from = args['consult_from'], consult_to = args['consult_to'], consult_type = args['consult_type'], patient_id = args['patient_id'], payment_ref_no = str(int(payment_ref) + 1))
    return query_apt

def book_adv(args, consult_idf):
    query_adv = INSERT['advise']
    query_adv = query_adv.format(employee_id = args['employee_id'], consult_id = str(int(consult_idf) + 1))
    return query_adv

def update_apt(args):
    updates = []
    if 'med_prescribed' in args and len(args['med_prescribed']) > 0:
        med_prescribed = args['med_prescribed'].split(",")
        med_prescribed = [ i.strip() for i in med_prescribed ]
        for i in med_prescribed:
            updates.append(UPDATE['prescription'].format(consult_id = args['consult_id'], fda_id = i))
            updates.append(TRGIGGERS['meds'].format(fda_id = i))
    if 'amount' in args and len(args['amount']) > 0:
        updates.append(UPDATE['payment'].format(amount = args['amount'], consult_id = args['consult_id']))
    return updates

