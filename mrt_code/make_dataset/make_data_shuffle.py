import glob
import os
import shutil
import random

random.seed(50)
# raw data directory
ROOTDIR = '../../raw_data/'

# classes = [mamma, melanoma, bronchial]
CLASS_NAME = 'Mamma'

script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
rel_path = f"{ROOTDIR}/{CLASS_NAME}/*"
abs_file_path = os.path.join(script_dir, rel_path)

# ids of patients with metastases
PATIENT_DIR = glob.glob(abs_file_path)



def main():


    images_all = []
    annotations_all = []
    image_number = 0

    for path in PATIENT_DIR:
        patient_id = path[-5:]
        print(patient_id)

        xml_list = glob.iglob(path + '/*.xml', recursive=True)

        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path_images = f"/dataset/{CLASS_NAME}/images/"
        abs_file_path_images = script_dir + rel_path_images#os.path.join(script_dir, rel_path_images)
        rel_path_xml = f"/dataset/{CLASS_NAME}/annotations_xml/"
        abs_file_path_xml = script_dir + rel_path_xml#os.path.join(script_dir, rel_path_images)

        save_dir_images = abs_file_path_images
        save_dir_annot = abs_file_path_xml

        for xml_filename in xml_list:
            img_filename = xml_filename[:-4] + '.jpg'
            x = img_filename.find(patient_id) + 6
            # print(img_filename[x:-4])
            output_jpg = CLASS_NAME + '_' + patient_id + '_' + img_filename[x:-4] + '.jpg'
            output_xml = CLASS_NAME + '_' + patient_id + '_' + img_filename[x:-4] + '.xml'
            # print(output_jpg)
            # print(output_xml)
            images_all.append((img_filename, output_jpg))
            annotations_all.append((xml_filename, output_xml))

    shuffle_list = list(zip(images_all, annotations_all))

    random.shuffle(shuffle_list)

    images_all, annotations_all = zip(*shuffle_list)

    for i in range (0, len(images_all)):
        img_name = str(image_number).zfill(4) + '_' + images_all[i][1]
        xml_name = str(image_number).zfill(4) + '_' + annotations_all[i][1]
        shutil.copy(images_all[i][0], save_dir_images+img_name)
        shutil.copy(annotations_all[i][0], save_dir_annot+xml_name)

        image_number = image_number + 1     

        print(image_number)




if __name__ == "__main__":
    main()