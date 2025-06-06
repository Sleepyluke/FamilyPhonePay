import queue

listeners = []

def add_listener():
    q = queue.Queue()
    listeners.append(q)
    return q


def remove_listener(q):
    try:
        listeners.remove(q)
    except ValueError:
        pass


def send_event(data: str):
    for q in list(listeners):
        q.put(data)
