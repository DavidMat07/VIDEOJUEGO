from platform import Platform

maps = [
    {
        "name": "Mapa 1",
        "bg_color": (100, 150, 200),
        "platforms": [
            Platform(100, 460, 800, 35, True),
            Platform(260, 330, 200, 20, False),
            Platform(540, 270, 200, 20, False)
        ]
    },
    {
        "name": "Mapa 2",
        "bg_color": (200, 180, 100),
        "platforms": [
            Platform(150, 480, 700, 30, True),
            Platform(100, 300, 150, 20, False),
            Platform(400, 260, 200, 20, False),
            Platform(750, 300, 150, 20, False)
        ]
    },
    {
        "name": "Mapa 3",
        "bg_color": (180, 200, 180),
        "platforms": [
            Platform(300, 480, 400, 30, True),  # <-- Plataforma principal más grande
            Platform(450, 360, 120, 20, False),
            Platform(450, 240, 120, 20, False)
        ]
    },
    {
        "name": "Mapa 4",
        "bg_color": (220, 150, 200),
        "platforms": [
            Platform(200, 460, 600, 35, True)
        ]
    }
]
