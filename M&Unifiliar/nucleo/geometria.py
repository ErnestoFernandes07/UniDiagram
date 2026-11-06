def transformar(item, dx, dy):
    if item.get("espelho", False):
        dx = -dx
    for _ in range(item.get("rotacao", 0) // 90):
        dx, dy = -dy, dx
    return item["x"] + dx, item["y"] + dy
