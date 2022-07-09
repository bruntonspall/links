from flask_login import UserMixin


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
