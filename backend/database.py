from collections import defaultdict
import pickle

class Database():
    def __init__(self, filename = './db.pkl') -> None:
        self.db = None
        self.filename = filename
        
    def storeData(self):
        # Save the db to pkl
        with open(self.filename, 'wb') as dbfile:
            pickle.dump(self.db, dbfile)

    def loadData(self):
        # load data from pkl file and return the db
        try:
            with open(self.filename, 'rb')  as dbfile:
                self.db = pickle.load(dbfile)
        except:
            self.db = {
                "passwords" : dict(),
                "messages": defaultdict(list)
            }
        return self.db

    def get_db(self):
        # 
        return self.db