class Reference:
    def __init__(
        self,
        data
    ):
        self.id = data.get('id')
        self.title = data.get('title')
        self.name = data.get('name')
