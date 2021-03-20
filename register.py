class Session:

    def __init__(self):
        self.names = []

    def __contains__(self, item):
        return item in self.names

    def add_user(self, name):
        self.names.append(name)

    def get_users(self):
        return self.names

    def new_user_joined(self, name):
        self.add_user(name)
        print(name, "just joined the session!")
