from PIL import Image

def singleton(cls):
    """
    Simple Singleton impl
    :param cls: class
    :return: instance of cls
    """
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance


class Counter:
    def __init__(
            self,
            max_value = None
    ):
        self.value = 0
        self.max_value = max_value

    def tick(self) -> int:
        self.value += 1
        if self.max_value is not None and self.value > self.max_value:
            self.value = 0
        return self.value


def load_image(path):
    return Image.open(path)