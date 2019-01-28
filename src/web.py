from flask import Flask, request, flash, abort, jsonify
from config import img_base_path
from model import Model,ModelCache
from db import create_db,fetch_best_params,db_get_experiments
from rq import Queue
from redis import from_url
import os
from subprocess import Popen
from experiment import perform_experiment
import config
from rq.job import Job
app = Flask(__name__)


@app.route('/models/create', methods=['POST'])
def create_model():
    data = request.get_json()
    i = None
    j = None
    k = None
    if data is not None:
        i = data.get("i", None)
        j = data.get("j", None)
        k = data.get("k", None)
    model = Model(i=i, j=j, k=k)
    model.write_model_to_db()
    model_cache.put(model.id, model)

    return jsonify({"model_id": model.id})


@app.route('/models/experiments/create', methods=['POST'])
def create_experiments():
    print(model_cache.cache)
    model_id = request.args.get("model_id")
    if model_id is None:
        abort(404)
    data = request.get_json()
    i = None
    j = None
    k = None
    if data is not None:
        i = data.get("i", None)
        j = data.get("j", None)
        k = data.get("k", None)
    model = model_cache.get(model_id)
    if model is None:
        abort(404)
    model = model_cache.get(model_id)
    model.generate_experiments(i, j, k)
    return "Experiments generated with i: " + str(model.i) + " ,j: " + str(model.j) + " ,k: " + str(model.k)


@app.route('/models/train', methods=['POST'])
def train():
    model_id = request.args.get("model_id")
    if model_id is None:
        abort(404)
    model = model_cache.get(model_id)
    if model is None:
        abort(404)
    # we ensure only one job exists per model
    result = {}
    try:
        if Job.fetch(str(model_id),redis_conn):
            result = {"status_message": "An experiment is already executing for this model. "
                                          "Wait till it completes before starting any more"}
    except:
        q.enqueue(perform_experiment, model_id, model.i, model.j, model.k, model.training_images_loc, timeout='10h',
                    job_id=str(model_id))
        result = {"status_message": "Experiment queued"}
    finally:
        return jsonify(result)


@app.route('/models/best', methods=['POST'])
def fetch_best():
    model_id = request.args.get("model_id")
    if model_id is None:
        abort(404)
    if model_cache.get(model_id) is None:
        abort(404)
    result = fetch_best_params(model_id)
    try:
        print(result)
        if not Job.fetch(str(model_id), redis_conn).is_finished:
            result["status_message"] = "Some experiments are still running for this model. Hence this result may change" \
                                   "Try again after sometime for more up to date results"
    except :
        print("No such Job")
    finally:
        return jsonify(result)


@app.route('/models/upload', methods=['POST'])
def upload_file():
    # single file image
    print("doing something")
    if request.method == 'POST':
        model_id = request.args.get("model_id")
        if model_id is None:
            abort(404)
        if model_cache.get(model_id) is None:
            abort(404)
        if 'file' not in request.files:
            flash('No file part')
            return "no image found"
        file = request.files['file']
        upload_path = img_base_path + "/"+ model_id
        if file:
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            file.save(os.path.join(upload_path,file.filename))

        return jsonify({"status_message": "Experiment queued"})

@app.route('/models/experiments', methods=['POST'])
def get_experiments():
    if request.method == 'POST':
        model_id = request.args.get("model_id")
        if model_id is None:
            abort(404)
        if model_cache.get(model_id) is None:
            abort(404)
        db_get_experiments(model_id)

        return jsonify(db_get_experiments(model_id))


if __name__ == '__main__':
    redis_conn = from_url(config.redis_url)
    if not os.path.exists(config.db_file):
        os.makedirs(config.db_file)
    if not os.path.exists(config.img_base_path):
        os.makedirs(config.img_base_path)
    db_conn = create_db(config.db_file)
    q = Queue(connection=redis_conn)
    model_cache = ModelCache()
    p = Popen(["rq","worker", "default"])
    app.run(host='0.0.0.0')

