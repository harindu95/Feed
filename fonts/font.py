from PyQt6.QtGui import QFontDatabase, QFont


def loadFonts():
    import glob
    from os import path
    list = glob.glob(path.join(path.dirname(__file__), '*.otf'))
    print("fonts:", list)
    for font in list:
        id = QFontDatabase.addApplicationFont(font)
        family = QFontDatabase.applicationFontFamilies(id)[0]
        if id < 0:
            print("Failed to load: ", font)
        else:
            print("font-family: ", family)


def loadFont(font):
    from os import path

    path = path.join(path.dirname(__file__), font)
    id = QFontDatabase.addApplicationFont(path)
    if id < 0:
        print("Failed to load: ", font)
        return None
    else:
        family = QFontDatabase.applicationFontFamilies(id)[0]
        print("font-family: ", family)
        return QFont(family)
