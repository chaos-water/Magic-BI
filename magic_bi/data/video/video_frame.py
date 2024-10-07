import uuid


class ChatFrame():
    def __init__(self):
        # self.id: int = int(time.time()*1000)
        self.id: str = uuid.uuid1().hex
        self.file_id: str = ''
        self.file_name: str = ''
        self.frame_storage_id: str = ''
        self.file_timeoffset: int = 0
        self.frame_description: str = ''
        self.vector: list = []
        self.collection_id: str = ''

    def get_payload(self):
        return {"id": self.id, "file_name": self.file_name, "frame_storage_id": self.frame_storage_id,
                "file_timeoffset": self.file_timeoffset, "frame_description": self.frame_description,
                "file_id": self.file_id, "collection_id": self.collection_id}
