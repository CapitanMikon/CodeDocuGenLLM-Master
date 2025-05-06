class ExtNotSupported(Exception):
    def __init__(self, ext):
        self.__ext = ext

    def __str__(self):
        return f"Unsupported extension. Provided {self.__ext} !"
