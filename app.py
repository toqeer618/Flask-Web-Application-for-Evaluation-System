from flask import Flask, jsonify, request, redirect, render_template
import mysql.connector as connector
from mysql.connector import errorcode
from werkzeug.security import generate_password_hash, check_password_hash
from utils import Grade_Map
from db import db_connect
app = Flask(__name__)

def get_json_data(e_id):
    keys = ['cand_id','q1_response', 'q2_response', 'q3_response', 'q4_response', 'q5_response', "q1_score", "q2_score",
       "q3_score", "q4_score", "q5_score", "total", "grade"]
    dic = {key:'' for key in keys}

    conn = db_connect()
    cursor = conn.cursor()
    qry = "select * from evaluations where evaluator_id = %s"
    qry1= "select response from responses where candidate_id = %s"
    json_obj ={"q1_response": ''}
    cursor.execute(qry, e_id)
    data = cursor.fetchall()

    dic_lis =[]
    for val in data:
        dic['cand_id']=val[1]
        cursor.execute(qry1, (val[1],))
        data_1 = cursor.fetchall()
        for i in range(len(data_1)):
            dic['q'+str(i+1)+"_response"]=data_1[i][0]
            
        dic['q1_score']=float(val[2])
        dic['q2_score']= float(val[3])
        dic['q3_score']=float(val[4])
        dic['q4_score']=float(val[5])
        dic['q5_score']= float(val[6])
        dic['total']= float(val[7])
        dic['grade']=val[8]
        dic_lis.append(dic)
    cursor.close()
    conn.close()
    return dic_lis



@app.route('/')
def index():
    return render_template('index.htm')

@app.route('/register', methods=['POST'])
def regiter():
    conn = db_connect()
    cursor = conn.cursor()
    user = "insert into user (user_name, email, password, role) values (%s,%s, %s,%s)"

    if request.method == 'POST':
        data = (request.form['user_name'], request.form['email'], generate_password_hash(request.form['password']), request.form['role'])
        cursor.execute(user, data)
        conn.commit()
        conn.close()
        return redirect('/')


@app.route("/login", methods=['POST'])
def login():

    conn = db_connect()
    cursor = conn.cursor()
    qry = "SELECT evaluator_id, password FROM user WHERE user_name = %(user_name)s "
    
    username = (request.form['user_name'])
    password = request.form['password']
    data ={'user_name':username}
    # Check if the username and password match a user in the database
    cursor.execute(qry, data)
    data = cursor.fetchall()
    db_pass = data[0][1]
    ev_id = (data[0][0],)


    # print(password, db_pass)
    cursor.close()
    conn.close()
    if check_password_hash(db_pass, password):
        data = get_json_data(ev_id)
        # print(data)
        return render_template('index.htm', data=jsonify(data))

    return jsonify({'message': 'Incorrect username or password'})
    
@app.route('/update', methods=['PUT'])

def update():

    q1_score = request.form['q1_score']
    q2_score = request.form['q2_score']
    q3_score = request.form['q3_score']
    q4_score = request.form['q4_score']
    q5_score = request.form['q5_score']
    total = (q1_score+q2_score+q3_score+q4_score+q5_score)/5
    grade = Grade_Map(total)
    
    conn = db_connect()
    cursor = conn.cursor()
    qry = """"update evaluations set  quiz_1_score=%s, quiz_2_score=%s, quiz_3_score=%s, quiz_4_score=%s, quiz_5_score=%s, total=%s, grade=%s where candidate_id = %s """
    cursor.execute(qry, (q1_score, q2_score, q3_score, q4_score, q5_score, total, grade, cand))
    conn.commit()
    conn.close()

    return render_template('index.htm')

if __name__ == '__main__':
    app.run(debug=True)