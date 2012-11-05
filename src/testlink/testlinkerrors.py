# -*- coding: utf-8 -*-



class TestLinkError(Exception):
    """ Basic error handler
    Return message pass as argument
    """
    def __init__(self, msg):
        self.__msg = msg

    def __str__(self):
        return self.__msg

