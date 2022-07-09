from flask_login import UserMixin
from .database import Database


class User(UserMixin):
    collection = "Users"

    def __init__(self, id_, email, name, picture):
        self.id = id_
        self.email = email
        self.name = name
        self.picture = picture

    @staticmethod
    def from_dict(source):
        return User(id_=source['id'], email=source['email'], name=source['name'], picture=source['picture'])

    @staticmethod
    def get(user_id):
        docref = Database.getDb().collection(User.collection).document(user_id).get()
        if not docref.exists:
            return None
        return User.from_dict(docref.to_dict())

    @staticmethod
    def create(id_, email, name, picture):
        userdict = {
            'id': id_,
            'email': email,
            'name': name,
            'picture': picture
        }
        Database.getDb().collection(User.collection).document(id_).set(userdict)
        return User.from_dict(userdict)
