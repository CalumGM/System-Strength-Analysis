class Circle:
    '''
    This class was made to conviniently access the infomation relevant to each circle
    '''
    def __init__(self, name, centre_coords, linestring, filename, color='red', x=[], y=[]):
        self.linestring = linestring
        self.centre_coords = centre_coords
        self.name = name
        self.color = color  # colour is purely for testing purposes. In the final release, all circles will be the same colour
        self.filename = filename  # store linestring and other list info in this file for ease of viewing
        self.x = x
        self.y = y

    def __str__(self):
        return "Centre of {} at {} \nLinestring saved in {}\n".format(self.name, self.centre_coords, self.filename)