from models.database import Database
from models.user import User


def get(user_id):
    docref = Database.getDb().collection(User.collection).document(user_id).get()
    if not docref.exists:
        return None
    return User.from_dict(docref.to_dict())


def create(id_, email, name, picture):
    userdict = {
        'id': id_,
        'email': email,
        'name': name,
        'picture': picture
    }
    Database.getDb().collection(User.collection).document(id_).set(userdict)
    return User.from_dict(userdict)
