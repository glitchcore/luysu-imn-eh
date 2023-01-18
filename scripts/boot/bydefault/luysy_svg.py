import xml.etree.ElementTree as ET
import svg.path

def to_point(c, size):
    return (c.real / size[0], c.imag / size[1])

def parse_svg(filename):
    # parse the SVG file
    tree = ET.parse(filename)
    root = tree.getroot()

    size = (float(root.attrib['width']), float(root.attrib['height']))

    # get the first path tag
    path_tag = root.find('.//{http://www.w3.org/2000/svg}path')

    # get the d attribute from the path tag
    path_d = path_tag.attrib['d']

    # parse the d attribute using svg.path
    path = svg.path.parse_path(path_d)

    points = [to_point(segment.start, size) for segment in path]
    return points

# 'web/svg/chr-savushkina-hackspace.svg'
# web/svg/chr-test.svg
print(parse_svg("web/svg/chr-savushkina-hackspace.svg"))
