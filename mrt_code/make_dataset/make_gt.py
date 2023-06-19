import glob
import shutil
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import matplotlib.pyplot as plt

# dataset directory
ROOTDIR = '/home/vsingh/Downloads/DFKI/neew/dataset'
# dataset after splits directory
SAVE_DIR = '/home/vsingh/Downloads/DFKI/neew/results/combined_gt/'
# classes = [mamma, melanoma, bronchial]
CLASS_NAME = 'bronchial'

ANNOTATIONS_DIR = glob.glob(f'{ROOTDIR}/{CLASS_NAME}/annotations')

def main():
    # Get the annotations
    annotations = [os.path.join(ANNOTATIONS_DIR[0], x) for x in os.listdir(ANNOTATIONS_DIR[0]) if x[-3:] == "txt"]
    annotations.sort()


    for annotation_file in annotations:
        #Get the corresponding image file
        image_file = annotation_file.replace("annotations", "images").replace("txt", "jpg")
        _, file_name = os.path.split(image_file)
        print(file_name)
        # #Load the image
        image = Image.open(image_file)
        save_img = file_name[:-4] + '_gt' + '.jpg'
        print(save_img)

        with open(annotation_file, "r") as file:
            annotation_list = file.read().split("\n")[:-1]
            annotation_list = [x.split(" ") for x in annotation_list]

            if len(annotation_list[0]) > 1:
                annotation_list = [[float(y) for y in x] for x in annotation_list]
                #Plot the Bounding Box
                plot_bounding_box(image, annotation_list, save_img)
            else:
                shutil.copy(image_file, SAVE_DIR + save_img)


def plot_bounding_box(image, annotation_list, img_name):
    class_name_to_id_mapping = {"mamma": 0,
                            "melanoma": 1,
                            "bronchial": 2,
                            }

    class_id_to_name_mapping = dict(zip(class_name_to_id_mapping.values(), class_name_to_id_mapping.keys()))
    annotations = np.array(annotation_list)
    w, h = image.size
    
    plotted_image = ImageDraw.Draw(image)

    transformed_annotations = np.copy(annotations)
    transformed_annotations[:,[1,3]] = annotations[:,[1,3]] * w
    transformed_annotations[:,[2,4]] = annotations[:,[2,4]] * h 
    
    transformed_annotations[:,1] = transformed_annotations[:,1] - (transformed_annotations[:,3] / 2)
    transformed_annotations[:,2] = transformed_annotations[:,2] - (transformed_annotations[:,4] / 2)
    transformed_annotations[:,3] = transformed_annotations[:,1] + transformed_annotations[:,3]
    transformed_annotations[:,4] = transformed_annotations[:,2] + transformed_annotations[:,4]
    
    for ann in transformed_annotations:
        obj_cls, x0, y0, x1, y1 = ann
        plotted_image.rectangle(((x0,y0), (x1,y1)), outline="orange", width=5)
        font  = ImageFont.truetype("Ubuntu-R.ttf" , 20)
        plotted_image.text((x0, y0 - 10), class_id_to_name_mapping[(int(obj_cls))], font=font)
    
    image = image.save(SAVE_DIR + img_name)


if __name__ == "__main__":
    main()