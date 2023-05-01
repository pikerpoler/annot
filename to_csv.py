#import os
import argparse
import pandas as pd
import glob
import os
from timeit import default_timer as timer


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv_file', type=str, required=True, help='full path to the csv file containing the '
                                                                      'list of images to annotate.')
    parser.add_argument('--root_dir', type=str, required=True, help='The path to the root images dir')
    args=parser.parse_args()
    print(args.root_dir)
    print(args.csv_file)
    path = args.root_dir
    images_list = []

    # Use a nested loop to iterate through all sub folders and files
    for foldername in os.listdir(path):
        folderpath = os.path.join(path, foldername)
        if os.path.isdir(folderpath):
            for filepath in glob.glob(os.path.join(folderpath, "*.bmp")):
                images_list.append((foldername, os.path.basename(filepath)))

    folder_list = [x[0] for x in images_list]
    file_list = [x[1] for x in images_list]
    image_nums = [int(x[1].split('.')[1]) for x in images_list]
    labels = [None] * len(images_list)
    x1 = [None] * len(images_list)
    y1 = [None] * len(images_list)
    x2 = [None] * len(images_list)
    y2 = [None] * len(images_list)
    df = pd.DataFrame({'sub folder': folder_list, 'image num': image_nums, 'label': labels, 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2})
    df = df.sort_values(by=['sub folder', 'image num'], ignore_index=True)
    print(df)
    df.to_csv(args.csv_file)
