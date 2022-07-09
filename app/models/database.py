from google.cloud import firestore


class Database:
    db = None

    @classmethod
    def getDb(cls):
        if not cls.db:
            cls.db = firestore.Client()
        return cls.db
