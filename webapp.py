from flask import Flask, render_template, request,send_file, jsonify
from tempfile import *
import os
import etl as e
from retriving_data import *
import psycopg2


app = Flask(__name__, template_folder='templates')

CONF_FILE = "./config/00.yml"
db_config = e.read_config(CONF_FILE)

# Set the database connection URI in the app configuration

username = db_config['database']['username']
password = db_config['database']['password']
host = db_config['database']['host']
port = db_config['database']['port']
database = db_config['database']['database']

conn = psycopg2.connect(f"dbname='{database}' user='{username}' host='{host}' password='{password}'")


app.config['SQLALCHEMY_DATABASE_URI'] = conn

@app.route('/')
def index():
    """The index function retunrs the html template

    """
    return render_template('index.html')


@app.route('/getreport', methods=['GET','POST'])
def report():
    """The report function runs the backend python scripts
    Args:
        
    """
    if request.method == 'POST':
        date1 = request.form['fi']
        date2 = request.form['ff']
        Initial_date = f"'{str(date1)}'"
        Final_date = f"'{str(date2)}'"
        #print(Initial_date)
# calling the main function in retriving_data script
        main(CONF_FILE, Initial_date, Final_date)
            
        dir_path = os.path.dirname(os.path.realpath(__file__))
        tempfile=dir_path+ "\\Env_Lisbon_report.pdf"
#       tempfile=dir_path+ "\\pdfs\\Env_Lisbon_report.pdf"
        return send_file(tempfile, attachment_filename='python.pdf')
    else:
        return render_template('index.html')


# GET method to get all values from the env_variables table
@app.route('/values', methods=['GET'])
def get_all_values():
    """The get_all_values returns all values from the env_variables table.

    Args:
       
    """
    
    try:
        cur = conn.cursor()
        cur.execute("""SELECT * from us.env_variables""")
        rows = cur.fetchall()
        print(rows)
        return jsonify(rows)
    except Exception as e:
        return []


# GET method to get all values from specific sensor
@app.route('/values/id_sensor=<id_sensor>', methods=['GET'])
def get_sensor_values(id_sensor:str):

    """The get_sensor_values returns all values for specific sensor from the env_variables table.

    Args:
       
    """
    
    try:
        cur = conn.cursor()
        cur.execute("""SELECT * from us.env_variables where id_sensor= %s""",[id_sensor])
        rows = cur.fetchall()
        print(rows)
        return jsonify(rows)
    except Exception as e:
        return []


if __name__ == '__main__':
    app.run(host = 'localhost', port = 5001, debug=True)