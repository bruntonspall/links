from .database import Database


class Settings:
    collection = u"settings"

    @staticmethod
    def get(name, default="NOT SET"):
        retval = Database.getDb().collection(Settings.collection).document(name).get()
        if not retval.exists:
            Database.getDb().collection(Settings.collection).document(name).set({
                "name": name,
                "value": default
            })
            return default
        return retval.to_dict()["value"]

    @staticmethod
    def set(name, value):
        Database.getDb().collection(Settings.collection).document(name).set({
            "name": name,
            "value": value
        })
