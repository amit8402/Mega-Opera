def fcfs(requests, head):
    seek = 0
    seq = [head]
    for r in requests:
        seek += abs(head - r)
        head = r
        seq.append(r)
    return seq, seek


def sstf(requests, head):
    seek = 0
    seq = [head]
    req = requests.copy()
    while req:
        c = min(req, key=lambda x: abs(x - head))
        seek += abs(head - c)
        head = c
        seq.append(c)
        req.remove(c)
    return seq, seek


def scan(requests, head, direction="right", disk_size=200):
    seek = 0
    seq = [head]
    left = sorted([r for r in requests if r < head])
    right = sorted([r for r in requests if r >= head])

    if direction == "left":
        for r in reversed(left):
            seek += abs(head - r)
            head = r
            seq.append(r)
        seek += abs(head - 0)
        head = 0
        seq.append(0)
        for r in right:
            seek += abs(head - r)
            head = r
            seq.append(r)
    else:
        for r in right:
            seek += abs(head - r)
            head = r
            seq.append(r)
        seek += abs(head - (disk_size - 1))
        head = disk_size - 1
        seq.append(head)
        for r in reversed(left):
            seek += abs(head - r)
            head = r
            seq.append(r)

    return seq, seek
