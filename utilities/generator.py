import uuid

def id_generator(size=20):
    id = uuid.uuid4().hex

    return id[:size]

def hex_generator(size=15):
    id = uuid.uuid4().hex

    return id[:size]

