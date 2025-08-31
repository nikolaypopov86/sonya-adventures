def singleton(cls):
    """
    Simple Singleton impl
    :param cls: class
    :return: instance of cls
    """
    instances = {}
    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get_instance
