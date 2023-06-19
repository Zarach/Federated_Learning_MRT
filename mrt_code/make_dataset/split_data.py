import glob
import shutil
import os

script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in

# dataset directory
ROOTDIR = script_dir+'/dataset/'
# dataset after splits directory
SAVE_DIR = script_dir+'/mrt_dataset/'
# classes = [mamma, melanoma, bronchial]
CLASS_LIST = ['Mamma', 'Melanoma', 'Bronchial']
# number of group for split
GROUP = 0
# total number of splits
FOLDS = 10
# split index for classes
SPLIT = [65, 125, 245]


def main():
    make_remove_dir(SAVE_DIR)

    # loop over all the classes
    for i in range (0, len(CLASS_LIST)):
        train_annot, test_annot, val_annot, annot_list = ([] for i in range(4))

        class_name = CLASS_LIST[i]

        # get the images and annotations directory for the selected class
        annot_dir = f'{ROOTDIR}/{class_name}/annotations'
        image_dir = f'{ROOTDIR}/{class_name}/images'

        annot_filenames = glob.iglob(annot_dir + '/*.txt', recursive=True)

        # get the filenames as a list
        for annot_path in annot_filenames:
            _, tail = os.path.split(annot_path)
            annot_list.append(tail)
        
        # sort the filenames
        annot_list.sort()

        print(f'Total {class_name} images: {len(annot_list)}')
        
        # list to find out the split index
        split_idx = [num*SPLIT[i] for num in range (0, FOLDS)]
        split_idx.append(len(annot_list))
        print(split_idx)
        
        # get test and validation annotation filenames
        test_annot, val_annot = get_annot_tv(annot_list, split_idx)

        # get train annotaion filenames: not present in test and val
        for i in range(0, len(annot_list)):
            value = annot_list[i]
            if (value not in test_annot) and (value not in val_annot):
                train_annot.append(value)
        
        dataset = [train_annot, val_annot, test_annot]

        # loop over to fill train, test, and validation folders
        for i in range(0, len(dataset)):
            # choose directory
            if i == 0:
                copy_dir = 'train/'
            elif i == 1:
                copy_dir = 'val/'
            elif i == 2:
                copy_dir = 'test/'
            
            print(copy_dir)

            # build final dataset for training
            make_dataset(dataset, copy_dir, class_name, i)


# function to build dataset
def make_dataset(dataset, copy_dir, class_name, i):
    for annot_file in dataset[i]:
        img_file = annot_file[:-4] + '.jpg'
        save_dir_images = SAVE_DIR + copy_dir 
        save_dir_annot = SAVE_DIR + copy_dir

        if isEmpty(save_dir_images) and isEmpty(save_dir_annot):
            os.makedirs(save_dir_images + 'images')
            os.makedirs(save_dir_annot + 'labels')

        shutil.copy(ROOTDIR + class_name + '/images/' + img_file, save_dir_images + 'images/' + img_file)
        shutil.copy(ROOTDIR + class_name + '/annotations/' + annot_file, save_dir_annot +  'labels/' + annot_file)


# function to get test and validation filenames as a list
def get_annot_tv(list_annotations, split_index):
    if GROUP == 9:
        test_annot = list_annotations[split_index[GROUP]:]
        # print(len(test_annot), test_annot)
        val_annot = list_annotations[split_index[0]:split_index[1]]

    else:
        test_annot = list_annotations[split_index[GROUP]:split_index[GROUP + 1]]
        # print(len(test_annot), test_annot)
        val_annot = list_annotations[split_index[GROUP + 1]:split_index[GROUP + 2]]
    
    return test_annot, val_annot


# function to make and remove necessary directories
def make_remove_dir(path):
    if isEmpty(SAVE_DIR):
        os.makedirs(SAVE_DIR + 'train')
        os.makedirs(SAVE_DIR + 'test')
        os.makedirs(SAVE_DIR + 'val')
    else:
        shutil.rmtree(SAVE_DIR + 'train', ignore_errors=True)
        shutil.rmtree(SAVE_DIR + 'test', ignore_errors=True)
        shutil.rmtree(SAVE_DIR + 'val', ignore_errors=True)
        os.makedirs(SAVE_DIR + 'train')
        os.makedirs(SAVE_DIR + 'test')
        os.makedirs(SAVE_DIR + 'val')


# function to Check if the path specified
def isEmpty(path):
    if os.path.exists(path) and os.path.isdir(path):
        # Checking if the directory is empty or not
        if not os.listdir(path):
            return True
        else:
            return False
    else:
        return False































if __name__ == '__main__':
    main()
