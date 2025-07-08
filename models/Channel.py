import config


class Channel:

    def __init__(self, data):
        self.id = data.get('id')
        self.title = data.get('title')
        self.name = data.get('name')
        logos = data.get('logos') or {}
        self.logo = logos.get('l') or logos.get('m') or logos.get('s')
        self.stream = data.get('stream')

    def to_msx(self):
        entry = {
            'title': self.title,
            'playerLabel': self.title,
            'image': self.logo,
            "action": f"video:plugin:{config.PLAYER}?url={self.stream}"
        }
        return entry
