class Reference:
    def __init__(self, data):
        self.id = data.get('id')
        self.title = data.get('title')
        self.name = data.get('name')

        self.location = data.get('location')
        self.description = data.get('description')
        self.code = data.get('code')
        self.short_title = data.get('short_title')
        self.quality = data.get('quality')
