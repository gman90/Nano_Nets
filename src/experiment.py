import subprocess, ast
from db import write_experiments


def perform_experiment(model_id,list_i,list_j,list_k,training_images_loc):
    for i in list_i:
        for j in list_j:
            for k in list_k:
                current_args = ["--i"] +[str (i)] + ["--j"]+ [str(j)] + ["--k"] + [str(k)] + ["--images"] + \
                               [training_images_loc]

                process = subprocess.check_output(["python","train.py"] + current_args)
                result_dict = ast.literal_eval(process.decode("utf-8").rstrip())
                print(result_dict.get('accuracy'))
                write_experiment_results(model_id, result_dict.get("i"), result_dict.get("j"), result_dict.get("k"),result_dict.get("accuracy"))


def write_experiment_results(model_id,i,j,k,accuracy):
    print(accuracy)
    write_experiments(model_id,i,j,k,accuracy)

