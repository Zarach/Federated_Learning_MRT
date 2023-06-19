import xml.etree.ElementTree as ET
import glob
import os


ROOTDIR = '/dataset'

# classes = [mamma, melanoma, bronchial]
CLASS_NAME = 'Mamma'

script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
rel_path = f"{ROOTDIR}/{CLASS_NAME}/annotations_xml"
abs_file_path = script_dir + rel_path

ANNOTATIONS_DIR = abs_file_path

def main():

    xml_list = glob.iglob(ANNOTATIONS_DIR + '/*.xml', recursive=True)
    for xml_filename in xml_list:
        _, tail = os.path.split(xml_filename)
        tail = tail[:-4] + '.jpg'
        file_path = f'{script_dir}/dataset/images/' + tail
        xmlTree = ET.parse(xml_filename)

        rootElement = xmlTree.getroot()
        rootElement.find('filename').text = str(tail)
        rootElement.find('path').text = str(file_path)

        for element in rootElement.findall("object"):
            element.find('name').text = CLASS_NAME

        xmlTree.write(xml_filename,encoding='UTF-8',xml_declaration=True)    

if __name__ == "__main__":
    main()