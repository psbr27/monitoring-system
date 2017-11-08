#!/usr/bin/python
from flask import Flask, jsonify
from flaskext.mysql import MySQL
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'escmonit'
app.config['MYSQL_DATABASE_PASSWORD'] = 'passcode'
app.config['MYSQL_DATABASE_DB'] = 'escdb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

@app.route('/fetch_esc_info')
def get():
        cur = mysql.connect().cursor()
        cur.execute('''select * from escdb.esc_tbl''')
        r = [dict((cur.description[i][0], value)
              for i, value in enumerate(row)) for row in cur.fetchall()]
        return jsonify({'myCollection' : r})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090, threaded=True)
