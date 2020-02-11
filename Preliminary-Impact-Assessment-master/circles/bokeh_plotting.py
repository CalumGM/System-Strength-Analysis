from bokeh.plotting import figure, output_file, show
import powerfactory as pf
import math

def create_circle_placemark(app, sub_coords):
    '''
    Creates a list of linestrings that trace a circle around a centre point.
    'coordinates' object is written in kml format, x_coords and y_coords are individual lists used to further calculations
    '''
    coordinates = ''
    x_coords = []
    y_coords = []

    for theta in range(629):
        x = float(sub_coords[0]) + 100*math.cos(theta/100)
        x_coords.append(x)
        y = float(sub_coords[1]) + 100*math.sin(theta/100)
        y_coords.append(y)
        coordinates = coordinates + str(x) + ',' + str(y) + ',' + '0 '
    return x_coords,y_coords


def get_closest_coord(app, coord, collection):
    '''
    Returns the closest value in a list (collection) to the given value (coords)
    '''
    return min(collection, key=lambda x:abs(x-coord))


def main():
    test_file = open('test.csv', 'w')
    app = pf.GetApplication()
    app.ClearOutputWindow()
    x1 = 0
    y1 = 40
    x2 = 40 
    y2 = 0

    # LineString circles
    x_circle1, y_circle1 = create_circle_placemark(app, [x1,y1])
    x_circle2, y_circle2 = create_circle_placemark(app, [x2,y2])

    # Calculation for intercept points
    r1 = 100
    r2 = 100
    R = math.sqrt((x2-x1)**2 + (y2-y1)**2)
    a = 1/2
    b = math.sqrt((2*((r1**2 + r2**2)/(R**2)))-1)

    intercept1 = [a * (x1+x2) - (a * (b * (y2-y1))),a * (y1+y2) + (a * (b * (x1-x2)))] # top intercept
    intercept2 = [a * (y1+y2) + (a * (b * (y2-y1))),a * (y1+y2) - (a * (b * (x2-x1)))] # bottom intercept

    # find the closest set of coordinates in the linestring compared to the calculations
    closest_circle1_coord_to_top_intercept = [get_closest_coord(app, intercept1[0], x_circle1), get_closest_coord(app, intercept1[1], y_circle1)]
    app.PrintPlain('closest coord on circle1 on to top intercept is: {}'.format(closest_circle1_coord_to_top_intercept))  
    closest_circle1_coord_to_bottom_intercept = [get_closest_coord(app, intercept2[0], x_circle1), get_closest_coord(app, intercept2[1], y_circle1)]
    app.PrintPlain('closest coord on circle1 on to bottom intercept is: {}'.format(closest_circle1_coord_to_bottom_intercept))

    closest_circle2_coord_to_top_intercept = [get_closest_coord(app, intercept1[0], x_circle2), get_closest_coord(app, intercept1[1], y_circle2)]
    app.PrintPlain('closest coord on circle2 on to top intercept is: {}'.format(closest_circle2_coord_to_top_intercept))
    closest_circle2_coord_to_bottom_intercept = [get_closest_coord(app, intercept2[0], x_circle2), get_closest_coord(app, intercept2[1], y_circle2)]
    app.PrintPlain('closest coord on circle2 on to bottom intercept is: {}'.format(closest_circle2_coord_to_bottom_intercept))


    circle1_x_top_intercept_index = x_circle1.index(closest_circle1_coord_to_top_intercept[0])  # upper bookend for x for circle1 x coordinate, used for iterating later
    app.PrintPlain('circle 1 x top intercept index: {}'.format(circle1_x_top_intercept_index))
    circle1_x_bottom_intercept_index = x_circle1.index(closest_circle1_coord_to_bottom_intercept[0])  # lower bookend for circle1 x coordinate
    app.PrintPlain('circle 1 x bottom intercept index: {}'.format(circle1_x_bottom_intercept_index))

    circle1_y_top_intercept_index = y_circle1.index(closest_circle1_coord_to_top_intercept[1])
    app.PrintPlain('circle 1 y top intercept index: {}'.format(circle1_y_top_intercept_index))
    circle1_y_bottom_intercept_index = y_circle1.index(closest_circle1_coord_to_bottom_intercept[1])
    app.PrintPlain('circle 1 y bottom intercept index: {}'.format(circle1_y_bottom_intercept_index))


    circle2_x_top_intercept_index = x_circle2.index(closest_circle2_coord_to_top_intercept[0])
    app.PrintPlain('circle 2 x top intercept index: {}'.format(circle2_x_top_intercept_index))
    circle2_x_bottom_intercept_index = x_circle2.index(closest_circle2_coord_to_bottom_intercept[0])
    app.PrintPlain('circle 2 x bottom intercept index: {}'.format(circle2_x_bottom_intercept_index))

    circle2_y_top_intercept_index = y_circle2.index(closest_circle2_coord_to_top_intercept[1])
    app.PrintPlain('circle 2 y top intercept index: {}'.format(circle2_y_top_intercept_index))
    circle2_y_bottom_intercept_index = y_circle2.index(closest_circle2_coord_to_bottom_intercept[1])
    app.PrintPlain('circle 2 y bottom intercept index: {}'.format(circle2_y_bottom_intercept_index))
    
    to_remove = []  # a list of coordinates that will be removed from the circle linestring

    for i in range(circle1_x_top_intercept_index, circle1_x_bottom_intercept_index):
        to_remove.append(x_circle1[i])
    x_circle1 = []
    for element in to_remove:
        x_circle1.append(element)
    to_remove = []

    for i in range(circle1_y_top_intercept_index, circle1_y_bottom_intercept_index):
        to_remove.append(y_circle1[i])
    y_circle1 = []
    for element in to_remove:
        y_circle1.append(element)
    to_remove = []

    for i in range(circle2_y_top_intercept_index-130, circle2_y_bottom_intercept_index): # x index is the first one it sees, not the intercept
        to_remove.append(x_circle2[i])
    for element in to_remove:
        x_circle2.remove(element)
    to_remove = []

    for i in range(circle2_y_top_intercept_index-130, circle2_y_bottom_intercept_index):
        to_remove.append(y_circle2[i])
    for element in to_remove:
        y_circle2.remove(element)
    to_remove = []
    '''
    for i in range(len(x_circle1)):  # slice out the parts of the circle which overlap
        if not(x_circle1[i] > closest_circle1_coord_to_bottom_intercept[0] and y_circle1[i] < closest_circle1_coord_to_top_intercept[1]):
            x_circle1_sliced.append(x_circle1[i])
            y_circle1_sliced.append(y_circle1[i])
    
    for i in range(len(x_circle2)):  # slice out the parts of the circle which overlap
        if x_circle2[i] < closest_circle1_coord_to_bottom_intercept[0] and y_circle2[i] > closest_circle1_coord_to_top_intercept[1]:
            x_circle2_sliced.append(x_circle2[i])
            y_circle2_sliced.append(y_circle2[i])
    '''


    for coord in x_circle1:
        coord = str(coord)
        test_file.write(coord + ',')
    test_file.write('\n')
    for coord in y_circle1:
        coord = str(coord)
        test_file.write(coord + ',')
    test_file.write('\n')
    for coord in x_circle2:
        coord = str(coord)
        test_file.write(coord + ',')
    test_file.write('\n')
    for coord in y_circle2:
        coord = str(coord)
        test_file.write(coord + ',')
    test_file.write('\n')

    app.PrintPlain('x_circle1: {}'.format(x_circle1))
    app.PrintPlain('y_circle1: {}'.format(y_circle1))
    app.PrintPlain('x_circle2: {}'.format(x_circle2))
    app.PrintPlain('y_circle2: {}'.format(y_circle2))

    output_file('circle.html')

    # Add plot
    p = figure(
        title = 'Example',
        x_axis_label = 'X axis', 
        y_axis_label = 'Y Axis'
    )
    #Render glyph
    p.line(x_circle1, y_circle1,legend='Line String Circle', line_width=2)
    p.line(x_circle2, y_circle2,legend='Line String Circle', line_width=2)
    
    # p.circle(x1,y1, legend='Circle 1', radius=100, fill_color=None, color='blue')
    # p.circle(x2,y2, legend='Circle 2', radius=100, fill_color=None, color='red')

    p.x(intercept1[0], intercept1[1])
    p.x(intercept2[0], intercept2[1])

    p.x(closest_circle1_coord_to_top_intercept[0], closest_circle1_coord_to_top_intercept[1], color='red')
    p.x(closest_circle1_coord_to_bottom_intercept[0], closest_circle1_coord_to_bottom_intercept[1], color='red')
    #Show results
    show(p)
    test_file.close()




if __name__ == '__main__':
  main()
