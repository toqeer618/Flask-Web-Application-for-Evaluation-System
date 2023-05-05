import mysql.connector as connector
from mysql.connector import errorcode
from datetime import date
from db import db_connect
import pandas as pd
from utils import startup, evaluator, Grade_Map
import random


def add_candidate(df, conn, cursor):
    candidate = """insert into candidate (candidate_id, created_at, first_name, last_name, email) 
    values ( %s,%s ,%s, %s, %s)"""
    for i in range(len(df)):
        data = (i+1, df[df.columns[0]][i], df[df.columns[3]][i],  df[df.columns[4]][i],  df[df.columns[1]][i])
        try:
            cursor.execute(candidate, data)
        except Exception as e:
            print(e)
            conn.close()

    conn.commit()
    return True

def add_to_response(df, conn, cursor):
    response = "insert into responses (candidate_id, question_id, response, algo_score, algo_grade) values (%s, %s, %s, %s, %s) "
    cursor.execute("Select * from questions")
    question = cursor.fetchall()
    for i in range(len(df)):
        try:
            output = evaluator(df[df.columns[35]][i], question[0][1], question[0][2])
            q1_response = (i+1, 1, df[df.columns[35]][i], float(output['score']), Grade_Map(float(output['score'])))
            cursor.execute(response, q1_response)

            output = evaluator(df[df.columns[36]][i], question[1][1], question[1][2])
            q2_response = (i+1, 2, df[df.columns[36]][i], float(output['score']), Grade_Map(float(output['score'])))
            cursor.execute(response, q2_response)

            output = evaluator(df[df.columns[37]][i], question[2][1], question[2][2])
            q3_response = (i+1, 3, df[df.columns[37]][i], float(output['score']), Grade_Map(float(output['score'])))
            cursor.execute(response, q3_response)

            output = evaluator(df[df.columns[38]][i], question[3][1], question[3][2])
            q4_response = (i+1, 4, df[df.columns[38]][i], float(output['score']), Grade_Map(float(output['score'])))
            cursor.execute(response, q4_response)

            output = evaluator(df[df.columns[39]][i], question[4][1], question[4][2])
            q5_response = (i+1, 5, df[df.columns[39]][i], float(output['score']), Grade_Map(float(output['score'])))
            cursor.execute(response, q5_response)
            conn.commit()
        except Exception as e:
            print(e)
            break

def get_question():
    conn = db_connect()
    cursor = conn.cursor()
    try:
        qry = "SELECT * FROM questions"
        cursor.execute(qry)
        data = cursor.fetchall()
    except:
        cursor.close()
        conn.close()
    cursor.close()
    conn.close()

    QUESTIONS = {}
    i=1
    for question in data:
        QUESTIONS['Q'+str(i)] = [question[1], question[2]]
        i+=1
    
    return QUESTIONS
    
def score_similiarity_logs():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("select  evaluator_id from user where role='evaluator'")
    eval_id=cursor.fetchall()
    eval_id=[val[0] for val in eval_id]
    
    QUESTIONS = get_question()
#     -------------
    try:
        qry = "SELECT * FROM responses"
        cursor.execute(qry)
        response = cursor.fetchall()
        
    except:
        cursor.close()
        conn.close()
        
    
    log = """insert into logs (candidate_id, question_id, response_length, 
    prompt_simaliarity, avg_sent_length, sent_length_dev, format_issue, 
    correction_score, tone_score, n_rules, rules_violated, score_breakdown) 
    values ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    evaluation = """insert into evaluations (evaluator_id, candidate_id, quiz_1_score, quiz_2_score, quiz_3_score, quiz_4_score, quiz_5_score, total, grade) 
    values ( %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
 
    count  = 0
    cand = 0
    scores = []
    for res in response:  
        output = evaluator(res[2], QUESTIONS['Q'+str(res[1])][0], QUESTIONS['Q'+str(res[1])][1])
        
        log_data =(res[0],res[1],output['logs']['response_length'], float(output['logs']['prompt_similarity']), float(output['logs']['avg_sentence_length']),
                  float(output['logs']['dev_sentence_length']), (output['logs']['format_issues']),float(output['logs']['correction_score']),
                  float(3.0), output['logs']['n_rules_violated'], str(output['logs']['rules_violated']), str(output['score_breakdown']))
        
        scores.append(output['score'])
        cand = res[0]
        count+=1
        try:
#         print(log_data)
            cursor.execute(log, log_data)
            conn.commit()

        except:
            print('Anomoly')
#             cursor.close()
#             conn.close()
            
        if count % 5==0:
            conn = db_connect()
            cursor = conn.cursor()
            evaluation_data = (eval_id[random.randint(0,len(eval_id))], cand, float(scores[0]),float(scores[1]),float(scores[2]), float(scores[3]),float(scores[4]), float(sum(scores)/5),Grade_Map(sum(scores)/5))
            print(evaluation_data)
            scores=[]
            try:
                cursor.execute(evaluation, evaluation_data)
                conn.commit()

            except:
                print('Evaluation Anomoly')
#                 cursor.close()
#                 conn.close()
#                 break

            
    cursor.close()
    conn.close()
        
def main():
    startup()
    df = pd.read_csv('FileNAme.csv')

    conn = db_connect()
    cursor=conn.cursor()
    add_candidate(df, conn, cursor)
    add_to_response(df,conn,cursor)
    score_similiarity_logs()
    