import config


class Video:

    def __init__(self, data):
        self.title = data.get('title')

        video_files = None
        if config.QUALITY is not None:
            video_files = [i for i in data['files'] if i['quality'] == config.QUALITY]
            if len(video_files) == 0:
                video_files = None
            else:
                video_files = video_files[0]

        if video_files is None:
            video_files = sorted(data['files'], key=lambda x: x.get('quality_id'))[-1]

        self.video = video_files['url'][config.PROTOCOL]

    def to_multivideo_entry(self):
        entry = {
            "label": self.title,
            #"playerLabel": self.title,
            'action': self.msx_action()
        }
        return entry

    def msx_action(self):
        return f"video:plugin:{config.PLAYER}?url={self.video}"
