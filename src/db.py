import sqlite3
from config import db_file

def create_db(db_loc):
        conn = sqlite3.connect(db_file + "/experiments.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE experiments(model_id varchar[40],learning_rate double, "
                       "number_of_layers INTEGER ,"
                       "number_of_steps INTEGER,accuracy double )")
        cursor.execute("CREATE TABLE models_current(model_id varchar[40] PRIMARY KEY,learning_rate double, "
                       "number_of_layers INTEGER ,"
                       "number_of_steps INTEGER,traing_image_loc varchar[200])")
        conn.commit()



def create_model(model_id,i,j,k,training_image_loc):
    conn = sqlite3.connect(db_file + "/experiments.db")
    cursor = conn.cursor()
    cursor.execute("insert or replace into models_current values (?,?,?,?,?)", (str(model_id), str(i), str(j), str(k), training_image_loc))
    conn.commit()

def get_model (model_id):
    conn = sqlite3.connect(db_file + "/experiments.db")

    cursor = conn.cursor()
    cursor.execute("select model_id, learning_rate, number_of_layers, number_of_steps,traing_image_loc from models_current where model_id = ?", (str(model_id),))
    results = cursor.fetchone()
    result_dict = {}
    if results is not None:
        result_dict["model_id"] = results[0]
        result_dict["i"] = results[1]
        result_dict["j"] = results[2]
        result_dict["k"] = results[3]
        result_dict["training_image_loc"] = results[4]
    return result_dict

def write_experiments(model_id,i,j,k,accuracy):
    conn = sqlite3.connect(db_file + "/experiments.db")

    cursor = conn.cursor()
    cursor.execute("insert into experiments values (?,?,?,?,?)",(model_id,str(i),str(j),str(k),str(accuracy)))
    conn.commit()
    conn.close()

def fetch_best_params(model_id):
    conn = sqlite3.connect(db_file + "/experiments.db")

    cursor = conn.cursor()
    cursor.execute("select model_id, learning_rate, number_of_layers, number_of_steps,max from (select *,"
                       "max(accuracy) as max from experiments group by model_id) as m where model_id =  ?",
                       (str(model_id),))
    results = cursor.fetchone()
    result_dict = {}
    if results is not None:
            result_dict["model_id"] = results [0]
            result_dict["i"] = results[1]
            result_dict["j"] = results[2]
            result_dict["k"] = results[3]
            result_dict["accuracy"] = results[4]
            conn.commit()
    return result_dict

