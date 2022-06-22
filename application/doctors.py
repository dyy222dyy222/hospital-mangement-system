import logging
from sqlalchemy import text

FULL_FETCH = """
SELECT
	e.employee_id,
	e.first_name,
	e.last_name,
	e.email,
	e.contact_number,
	e.designation,
	e.gender,
	d.dep_name,
	dr.specialization,
	e.dob,
	e.hiredate,
	e.salary,
	dr.license_number
FROM
	employee e,
	doctor dr,
	department d
WHERE
	e.employee_id = dr.employee_id
AND e.department_id = d.department_id
"""

STD_FETCH = """
SELECT
	e.employee_id,
	e.first_name,
	e.last_name,
	e.email,
	e.contact_number,
	e.designation,
	e.gender,
	d.dep_name,
	dr.specialization
FROM
	employee e,
	doctor dr,
	department d
WHERE
	e.employee_id = dr.employee_id
AND e.department_id = d.department_id
"""

queryMap = {
    'recent_consult': " AND e.employee_id IN (SELECT ad.employee_id FROM advise ad, consult cs WHERE ad.consult_id = cs.consult_id AND	to_char(now(), 'YYYY') = to_char(cs.consult_to, 'YYYY'))",
    'first_name': " AND e.first_name LIKE '%%{}%%'",
    'email': " AND e.email LIKE '%%{}%%'",
    'dep_name': " AND d.dep_name LIKE '%%{}%%'",
    'specialization': " AND dr.specialization LIKE '%%{}%%'",
    'sort': " ORDER BY e.employee_id"
}

def fetch(args):
    query = FULL_FETCH if 'sensitive' in args else STD_FETCH
    print(str(args))
    query += queryMap['recent_consult'] if 'recent_consult' in args else ""
    query += queryMap['first_name'].format(args['first_name']) if 'first_name' in args else ""
    query += queryMap['email'].format(args['email']) if 'email' in args else ""
    query += queryMap['dep_name'].format(args['dep_name']) if 'dep_name' in args else ""
    query += queryMap['specialization'].format(args['specialization']) if 'specialization' in args else ""
    query += queryMap['sort'] if 'sort' in args else ""
    print(str(query))
    return query