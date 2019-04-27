from taurex.log import Logger


class Opacity(Logger):
    """
    This is the base class for computing opactities

    """
    
    def __init__(self,name):
        super().__init__(name)

    


    def opacity(self,temperature,pressure):
        raise NotImplementedError
