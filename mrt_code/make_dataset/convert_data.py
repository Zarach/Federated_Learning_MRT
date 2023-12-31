import os 
import xml.etree.ElementTree as ET
# from tqdm import tqdm
import glob

ROOTDIR = '/dataset'

# classes = [mamma, melanoma, bronchial]
CLASS_NAME = 'Mamma'

script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
rel_path_xml = f"{ROOTDIR}/{CLASS_NAME}/annotations_xml/"
abs_file_path_xml = script_dir + rel_path_xml

rel_path = f"{ROOTDIR}/{CLASS_NAME}/annotations/"
abs_file_path = script_dir + rel_path

ANNOTATIONS_DIR = abs_file_path_xml
ANNOTATIONS_SAVE = abs_file_path

def main():
    # Get the annotations
    annotations = [os.path.join(ANNOTATIONS_DIR, x) for x in os.listdir(ANNOTATIONS_DIR) if x[-3:] == "xml"]
    annotations.sort()

    # Convert and save the annotations
    for ann in annotations:
        info_dict = extract_info_from_xml(ann)
        convert_to_yolov5(info_dict)
    annotations = [os.path.join(ANNOTATIONS_SAVE, x) for x in os.listdir(ANNOTATIONS_SAVE) if x[-3:] == "txt"]


# Function to get the data from XML Annotation
def extract_info_from_xml(xml_file):
    root = ET.parse(xml_file).getroot()
    
    # Initialise the info dict 
    info_dict = {}
    info_dict['bboxes'] = []

    # Parse the XML Tree
    for elem in root:
        # Get the file name 
        if elem.tag == "filename":
            info_dict['filename'] = elem.text
            
        # Get the image size
        elif elem.tag == "size":
            image_size = []
            for subelem in elem:
                image_size.append(int(subelem.text))
            
            info_dict['image_size'] = tuple(image_size)
        
        # Get details of the bounding box 
        elif elem.tag == "object":
            bbox = {}
            for subelem in elem:
                if subelem.tag == "name":
                    bbox["class"] = subelem.text
                    print(bbox['class'])
                    
                elif subelem.tag == "bndbox":
                    for subsubelem in subelem:
                        bbox[subsubelem.tag] = int(subsubelem.text)            
            info_dict['bboxes'].append(bbox)
    
    return info_dict


# Convert the info dict to the required yolo format and write it to disk
def convert_to_yolov5(info_dict):
    # Dictionary that maps class names to IDs
    class_name_to_id_mapping = {"Mamma": 0,
                            "Melanoma": 1,
                            "Bronchial": 2,
                            }

    print_buffer = []
    
    # For each bounding box
    for b in info_dict["bboxes"]:
        try:
            class_id = class_name_to_id_mapping[b["class"]]
        except KeyError:
            print("Invalid Class. Must be one from ", class_name_to_id_mapping.keys())
        
        # Transform the bbox co-ordinates as per the format required by YOLO v5
        b_center_x = (b["xmin"] + b["xmax"]) / 2 
        b_center_y = (b["ymin"] + b["ymax"]) / 2
        b_width    = (b["xmax"] - b["xmin"])
        b_height   = (b["ymax"] - b["ymin"])
        
        # Normalise the co-ordinates by the dimensions of the image
        image_w, image_h, image_c = info_dict["image_size"]  
        b_center_x /= image_w 
        b_center_y /= image_h 
        b_width    /= image_w 
        b_height   /= image_h 
        
        #Write the bbox details to the file 
        print_buffer.append("{} {:.3f} {:.3f} {:.3f} {:.3f}".format(class_id, b_center_x, b_center_y, b_width, b_height))

    # Name of the file which we have to save 
    save_file_name = os.path.join(ANNOTATIONS_SAVE, info_dict["filename"].replace("jpg", "txt"))
    print(save_file_name)
    
    # Save the annotation to disk
    print("\n".join(print_buffer), file= open(save_file_name, "w"))
        

if __name__ == "__main__":
    main()