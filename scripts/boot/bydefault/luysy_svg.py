import xml.etree.ElementTree as ET
import svg.path
import glob

def to_point(c, size):
    return (c.real / size[0], c.imag / size[1])

def parse_svg(filename):
    # parse the SVG file
    tree = ET.parse(filename)
    root = tree.getroot()

    size = (float(root.attrib['width'].replace("m", "")), float(root.attrib['height'].replace("m", "")))

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
# print(parse_svg("web/svg/chr-savushkina-hackspace.svg"))

def get_files():
    folder_path = 'svg'
    svg_files = glob.glob(folder_path + '/*.svg')

    data = []

    for file in svg_files:
        file_name = file.split("/")[-1]
        parts = file_name.split("-", 1)
        # print(parts)
        data.append((parts[0], parse_svg(folder_path + '/' + file_name), file_name))

    return data

if __name__ == '__main__':
    print(get_files()[0])
