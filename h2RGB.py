def getRGB(temp):
    # Mapează temperatura din intervalul [-100, 100] în intervalul [0, 360] grade
    temp_min = -100
    temp_max = 100
    temp = max(temp_min, min(temp, temp_max))  # limităm între -100 și 100
    deg = int((temp - temp_min) * 360 / (temp_max - temp_min))  # scala pe 360°

    m = 1 / 60
    if deg >= 0 and deg < 60:
        R = 1
        G = 0
        B = m * deg
    elif deg < 120:
        R = 1 - m * (deg - 60)
        G = 0
        B = 1
    elif deg < 180:
        R = 0
        G = m * (deg - 120)
        B = 1
    elif deg < 240:
        R = 0
        G = 1
        B = 1 - m * (deg - 180)
    elif deg < 300:
        R = m * (deg - 240)
        G = 1
        B = 0
    else:
        R = 1
        G = 1 - m * (deg - 300)
        B = 0

    return R, G, B
