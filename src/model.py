import uuid
from config import img_base_path,model_cache_size
from db import create_model,get_model

class Model:
    def __init__(self, db_conn, id =None, i=None, j=None, k=None):
        if id is None:
            self.id = uuid.uuid4()
        if i is None:
            self.i = [0.001, 0.01, 0.1]
        else:
            self.i = i

        if j is None:
            self.j = [1, 2, 4]
        else:
            self.j = j

        if k is None:
            self.k = [1000, 2000, 4000]
        else:
            self.k = k
        self.training_images_loc = img_base_path + "/" + "/" + str(self.id)
        self.db_conn = db_conn

    def generate_experiments(self, i=None, j=None, k=None):
        if i is not None:
            self.i = i
        if j is not None:
            self.j = j
        if k is not None:
            self.k = k
        self.write_model_to_db()

    def write_model_to_db(self):
        create_model(self.id, self.i, self.j, self.k, self.training_images_loc)


class ModelCache:
    def __init__(self):
        self.cache = {}


    def put(self,model_id,model_object):

        if len(self.cache.keys()) == model_cache_size:
            # evict the first model
            self.cache.pop(self.cache.keys()[0])
        self.cache[str(model_id)] = model_object

    def get(self,model_id):
        if self.cache.get(model_id,None):
            result = get_model(model_id)
            if result is None:
                return None
            if len(self.cache.keys()) == model_cache_size:
                #evict the first model
                self.cache.pop(self.cache.keys()[0])
                self.cache["model_id"] = Model(model_id,result["i"],result["j"],result["k"])

        return self.cache.get(model_id,None)
