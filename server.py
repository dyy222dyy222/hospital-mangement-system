import os, sys
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
import json
import logging


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
conf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf')
app = Flask(__name__, template_folder=tmpl_dir)
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app'))
import application.doctors
import application.appointments
import application.medicines
import application.patient


# Import login details from configuration file.
with open(conf_dir + '/configuration.json') as f:
  config = json.load(f)

DATABASEURI = "postgresql://" + config['user'] + ":" + config['passphrase'] + "@34.73.36.248/project1" 

engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
  try:
    logging.debug("In-flight request: Attempting to establish connection to DB")
    g.conn = engine.connect()
    logging.debug("In-flight request: Connection established!")
  except:
    logging.ERROR("In-flight request: Error connectiong to database!")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def index():
  return render_template("home.html")

@app.route("/doctors/", methods=["POST", "GET"])
def doctors_render():
  if "GET" == request.method:
    return render_template("doctors.html")
  else:
    query = application.doctors.fetch(request.form)
    cursor = g.conn.execute(query)
    result = []
    for c in cursor:
      result.append(c)
    return render_template("doctors.html", **dict(data = result))

@app.route("/nurses/", methods=["POST", "GET"])
def nurse_render():
  if "GET" == request.method:
    return render_template("nurses.html")
  else:
    query = application.nurses.fetch(request.form)
    cursor = g.conn.execute(query)
    result = []
    for c in cursor:
      result.append(c)
    return render_template("nurses.html", **dict(data = result))

@app.route("/patients/", methods=["POST", "GET"])
def patient_master():
  if "GET" == request.method:
    return render_template("patients.html")
  return redirect("/")

@app.route("/find_patients/", methods=["POST", "GET"])
def patient_find():
  if "POST" == request.method:
    rows = ["Patient ID", "First Name", "last Name", "Insurance ID", "DOB", "Gender"]
    query = application.patient.fetch_patients(request.form)
    cursor = g.conn.execute(query)
    result = []
    for c in cursor:
        result.append(dict(zip(rows, c)))
    return render_template("/patient_view.html", **dict(apt = result))
  return redirect("/")

@app.route("/add_patients/", methods=["POST", "GET"])
def patient_add():
  if "POST" == request.method:
    rows = ["Patient ID", "First Name", "last Name", "Insurance ID", "DOB", "Gender"]
    query = application.patient.MAX_PAT_ID
    cursor = g.conn.execute(query)
    pat_id = 0
    for c in cursor:
      pat_id = c
    query = application.patient.add_patients(pat_id[0], request.form)
    cursor = g.conn.execute(query)
    query = application.patient.fetch_patients(request.form)
    cursor = g.conn.execute(query)
    result = []
    for c in cursor:
        result.append(dict(zip(rows, c)))
    return render_template("/patient_view.html", **dict(apt = result))
  return redirect("/")

@app.route("/appointments/", methods=["GET"])
def appointments_render():
  return render_template("appointments.html")

@app.route("/search_appointments", methods=["POST"])
def search_appointments():
  rows = ["Consult ID", "Patient ID", "First Name", "Last Name", "Payment Reference Number", "Consult From", "Consult To", "Consult Type", "Insurance ID", "Gender", "DOB", "Payment Status", "Doctor ID", "Doctor Licence Number"]
  print(str(request.form))
  query = application.appointments.fetch_appointments(request.form)
  cursor = g.conn.execute(query)
  result = []
  for c in cursor:
    result.append(dict(zip(rows, c)))
  query_med = application.appointments.fetch_meds_prescribed(request.form)
  cursor = g.conn.execute(query_med)
  result_med = []
  for c in cursor:
    result_med.append(c)
  return render_template("appointment_view.html", **dict(apt = result, vmeds = result_med))

@app.route("/book_appointments", methods=["POST"])
def book_appointments():
  query = application.appointments.MAX_ID_PAY_REF
  cursor = g.conn.execute(query)
  pay_ref = 0
  for c in cursor:
    pay_ref = c
  query = application.appointments.MAX_ID_CONSULT
  cursor = g.conn.execute(query)
  consult_id = 0
  for c in cursor:
    consult_id = c
  query = application.appointments.book_payment(request.form, pay_ref[0])
  g.conn.execute(query)
  query = application.appointments.book_apt(request.form, consult_id[0], pay_ref[0])  
  print(query)
  g.conn.execute(query)
  query = application.appointments.book_adv(request.form, consult_id[0])  
  print(query)
  g.conn.execute(query)
  return redirect("/")

@app.route("/update_appointments", methods=["POST"])
def update_appointments():
  query = application.appointments.update_apt(request.form)
  for q in query:
    g.conn.execute(q)
  return redirect("/")

@app.route("/medicines/", methods=["POST", "GET"])
def med_render():
  if "GET" == request.method:
    query = application.medicines.fetch_medicines()
    cursor = g.conn.execute(query)
    result = []
    for c in cursor:
      result.append(c)
    return render_template("medicines.html", **dict(data = result))
  else:
    query = application.medicines.MAX_ID_MED
    cursor = g.conn.execute(query)
    med_ref = 0
    for c in cursor:
      med_ref = c
    query = application.medicines.add_medicine(med_ref[0],request.form)
    return redirect("/medicines")

@app.route("/admin/", methods=["POST","GET"])
def admin_render():
  if "GET" == request.method:
    query = application.admin.GET_DEPTS
    cursor = g.conn.execute(query)
    depts = []
    for c in cursor:
      depts.append(c)
    query = application.admin.GET_UNITS
    cursor = g.conn.execute(query)
    units = []
    for c in cursor:
      units.append(c)
    return render_template("admin.html", **dict(dpt = depts, unt = units))
  return redirect("/admin")

@app.route("/admin_create_doctor/", methods=["POST"])
def admin_doctor():
  query = application.admin.GET_MAX_EMP_ID
  cursor = g.conn.execute(query)
  eid = 0
  for c in cursor:
    eid = c
  query = application.admin.create_doctor(eid[0], request.form)
  cursor = g.conn.execute(query[0])
  cursor = g.conn.execute(query[1])
  return redirect("/admin")

@app.route("/admin_create_nurse/", methods=["POST"])
def admin_nurse():
  query = application.admin.GET_MAX_EMP_ID
  cursor = g.conn.execute(query)
  eid = 0
  for c in cursor:
    eid = c
  query = application.admin.create_nurse(eid[0], request.form)
  cursor = g.conn.execute(query[0])
  cursor = g.conn.execute(query[1])
  return redirect("/admin")

@app.route("/admin_create_assoc/", methods=["POST"])
def admin_assoc():
  query = application.admin.create_assoc(request.form)
  cursor = g.conn.execute(query)
  return redirect("/admin")

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click
  logging.basicConfig(filename='server.log', format= '%(asctime)s %(message)s', level=logging.DEBUG)
  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
