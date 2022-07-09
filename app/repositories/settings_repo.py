from models.database import Database

collection = u"settings"


def get(name, default="NOT SET"):
    retval = Database.getDb().collection(collection).document(name).get()
    if not retval.exists:
        Database.getDb().collection(collection).document(name).set({
            "name": name,
            "value": default
        })
        return default
    return retval.to_dict()["value"]


def set(name, value):
    Database.getDb().collection(collection).document(name).set({
        "name": name,
        "value": value
    })
