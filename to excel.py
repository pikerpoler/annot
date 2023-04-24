#import os
import argparse
import pandas as pd
import glob


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--excel_file', type=str, required=True, help='full path to the excel file containing the '
                                                                      'list of images to annotate.\n The excel can '
                                                                      'contain multiple sheets, but each sheet should '
                                                                      'contain 2 columns with the headers "image path" '
                                                                      'and "label"')
    parser.add_argument('--root_dir',type=str, required=True, help='The path to the root images dir')
    args=parser.parse_args()
    print(args.root_dir)
    print(args.excel_file)

    images_list = glob.glob(args.root_dir + '*\\' + '*.bmp', recursive=True)
    labels = [None] * len(images_list)
    x1 = [None] * len(images_list)
    y1 = [None] * len(images_list)
    x2 = [None] * len(images_list)
    y2 = [None] * len(images_list)

    df = pd.DataFrame({'image path': images_list, 'label': labels, 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2})
    print(df)
    df.to_excel(args.excel_file)
