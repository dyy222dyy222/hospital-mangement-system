FETCH_PATIENT = """
    SELECT * FROM patient pt
    WHERE 1 = 1 
"""

INSERT_PATIENT = """
    INSERT INTO patient VALUES ({patient_id}, '{first_name}', '{last_name}', '{insurance_id}', '{dob}', '{gender}')
"""

MAX_PAT_ID = """
    SELECT MAX(patient_id) FROM patient
"""

queryMap = {
    'patient_id': " AND pt.patient_id IN ({})",
    'first_name': " AND pt.first_name LIKE '%%{}%%'",
    'last_name': " AND pt.last_name LIKE '%%{}%%'",
    'insurance_id': " AND pt.insurance_id IN ('{}')"
}


def fetch_patients(args):
    query = FETCH_PATIENT
    query += queryMap['patient_id'].format(args['patient_id']) if 'patient_id' in args and len(args['patient_id']) > 0 else ""    
    query += queryMap['first_name'].format(args['first_name']) if 'first_name' in args and len(args['first_name']) > 0 else ""
    query += queryMap['last_name'].format(args['last_name']) if 'last_name' in args and len(args['last_name']) > 0 else ""
    query += queryMap['insurance_id'].format(args['insurance_id']) if 'insurance_id' in args and len(args['insurance_id']) > 0 else ""
    return query

def add_patients(pat_id, args):
    add_pt = INSERT_PATIENT
    add_pt = add_pt.format(patient_id = str(int(pat_id) + 1), first_name = args['first_name'], last_name = args['last_name'], insurance_id=args['insurance_id'], dob = args['dob'], gender=args['gender'])
    return add_pt