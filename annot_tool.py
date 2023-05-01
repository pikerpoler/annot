# -*- coding: utf-8 -*-
import argparse
import os

import numpy as np
import pandas as pd
import copy
import cv2
#import numpy as np

draw = 0
mouseX = 0
mouseY = 0
color = (255, 255, 0)
thickness = 2



def open_window():
    cv2.namedWindow('GIP', cv2.WND_PROP_FULLSCREEN)
    # cv2.setWindowProperty('', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    # cv2.setWindowProperty('', cv2.SCREE)
    cv2.startWindowThread()



def close_window():
    cv2.destroyAllWindows()


class HIC_Annotator(object):
    def __init__(self, excel_file, root_dir):
        self.excel_file = excel_file
        self.root_dir = root_dir
        self.curr_im = None
        self.curr_brown_im = None
        self.display = None
        self.curr_im_path = None
        self.space_on = False
        self.curr_sheet = None
        self.curr_label = None

        self.curr_x1 = None
        self.curr_y1 = None
        self.curr_x2 = None
        self.curr_y2 = None
        self.exit = False
        self.draw_rect = True
        self.sheets = []
        self.curr_idx = None
        self.done = 0
        self.curr_sheet_idx = 0
        self.images = []
        self.labels = []
        self.x1 = []
        self.y1 = []
        self.x2 = []
        self.y2 = []
        self.data = {}
        color_dict = {
            #1: np.array([1, 0, 0]),
            #2: np.array([0.8, 0.1, 0.1]),
            #3: np.array([0.6, 0.2, 0.2]),
            1: np.array([1, 0, 0]),
            2: np.array([0, 1, 0]),
            3: np.array([0, 0, 1]),
            4: np.array([0.33, 0.33, 0.33]),
            5: np.array([0.2, 0.2, 0.6]),
            6: np.array([0.1, 0.1, 0.8]),
            7: np.array([0, 0, 1]),
            0: np.array([0, 0, 0])
        }
        self.color_dict = color_dict


    def mouse_click(self, event, x, y, flags, param):
        global mouseX, mouseY, draw, img
        if event == cv2.EVENT_LBUTTONDOWN:
            if draw == 0:
                mouseX, mouseY = x, y
            else:
                self.display = self.curr_im.copy()
                self.display = cv2.arrowedLine(self.display, (mouseX, mouseY), (x, y), color, thickness)
                cv2.imshow('', self.display)
                self.curr_x1 = mouseX
                self.curr_y1 = mouseY
                self.curr_x2 = x
                self.curr_y2 = y

                self.draw_rect = True
                print('x1=', x, 'y1=', y, 'x2= ', mouseX, 'y2= ', mouseY)
            draw = 1 - draw

    def draw_region(self, x1, y1, x2, y2):
        im = self.curr_im.copy()
        cv2.arrowedLine(self.display, (x1, y1), (x2, y2), color, thickness)
        return im
#        cv2.waitKey(5000)

    def color_edge(self, edge_width=15):
        im = self.curr_im.copy()
        if self.curr_label is not None:
            color = self.color_dict[self.curr_label]
            im[:edge_width, :] = color
            im[:, :edge_width, :] = color
            im[-edge_width:, :] = color
            im[:, -edge_width:, :] = color
        return im

    def get_initial_image(self):
        i = 0
        for label in self.labels:
            if not pd.isna(label):  # skip over filed labels
                i += 1
                continue
            return i
        return i

    def run(self, debug=False):
        print(self.excel_file)
        print(self.root_dir)
        open_window()

        xls = pd.ExcelFile(self.excel_file, engine='openpyxl')
        self.sheets = [s for s in xls.sheet_names if s != 'summary']
        xls.close()
        for sheet in self.sheets:
            df = pd.read_excel(self.excel_file, sheet_name=sheet)
            self.data[sheet] = df
        self.curr_sheet = -1
        first_sheet = True
        while self.curr_sheet < len(self.sheets):
            self.save_sheet()
            if self.curr_idx is None or self.curr_idx >= 0:
                self.curr_sheet += 1
                if self.curr_sheet == len(self.sheets):
                    break
                go_to_prev_sheet = False
            else:
                self.curr_sheet -= 1
                go_to_prev_sheet = True

            print(f'Analysing Image Folder: {self.sheets[self.curr_sheet]}')
            df = self.data[self.sheets[self.curr_sheet]]
            self.images = list(df['image path'])
            self.labels = list(df['label'])
            self.x1 = list(df['x1'])
            self.y1 = list(df['y1'])
            self.x2 = list(df['x2'])
            self.y2 = list(df['y2'])
            print(f'Total of {len(self.images)} images to annotate')

            if first_sheet:
                self.curr_idx = self.get_initial_image()
            else:
                self.curr_idx = 0 if go_to_prev_sheet is False else len(self.images) - 1
            while 0 <= self.curr_idx < len(self.images):
                first_sheet = False
                im, label, x1, y1, x2, y2 = self.images[self.curr_idx], self.labels[self.curr_idx], self.x1[self.curr_idx], self.y1[self.curr_idx], self.x2[self.curr_idx],self.y2[self.curr_idx]
                if self.exit:
                    break
                try:
#                    self.curr_im_path = f'{self.root_dir}{im}'
                    self.curr_im_path = f'{im}'
                    # if we don't run on windows, we need to change the path
                    if not os.path.exists(self.curr_im_path):
                        self.curr_im_path = self.curr_im_path.replace('\\', '/')
                    self.curr_im_path = os.path.join(self.root_dir, self.curr_im_path)
#                    print(self.root_dir)
#                    print("======>", self.root_dir)
#                    print("------->", im)
                    self.curr_im = cv2.imread(self.curr_im_path) / 255
                    self.curr_brown_im = None if not self.space_on else self.color_brown()
                    if not pd.isna(label):  # set label of current image
                        self.curr_label = label
                        self.curr_im = self.color_edge()
                    else:
                        self.curr_label = None
                    self.display = self.curr_im.copy() if not self.space_on else self.curr_brown_im
                    to_break = False
                    while not to_break:
                        if self.draw_rect:
                            self.draw_region(self.curr_x1, self.curr_y1, self.curr_x2, self.curr_y2)

                        cv2.imshow('', self.display)
                        rv = cv2.waitKey(0)
                        if debug:
                            print(rv)
                        to_break = self.onkey(rv)

                    if self.exit:
                        self.goodbye_message()
                        break
                except Exception as e:
                    print(e)
                    self.curr_im = None
                    self.curr_im_path = None
                    self.curr_label = None
                    self.curr_idx += 1
                    continue
            self.save_sheet()
            if self.exit:
                break
        print('Done!')

    def goodbye_message(self):
        print('\n\n')
        if self.done <= 20:
            print(f'Tired today? you only annotated {self.done} new images...')
        elif self.done <= 50:
            print(f'Well Done! you annotated {self.done} new images.')
        else:
            print(f'Wow! you annotated {self.done} new images!')
        print('Saving results to file and exiting, please wait...')

    def save_sheet(self):

        if self.curr_sheet < 0:
            return
        with pd.ExcelWriter(self.excel_file, if_sheet_exists='replace', mode='a') as writer:
            for sheet in self.sheets:
                if sheet == self.sheets[self.curr_sheet]:
 #                   df = pd.DataFrame({'image path': self.images, 'label': self.labels})
                    df = pd.DataFrame({'image path': self.images, 'label': self.labels, 'x1': self.x1, 'y1': self.y1,'x2': self.x2,'y2': self.y2})
                    self.data[self.sheets[self.curr_sheet]] = df
                df = self.data[sheet]
                df.to_excel(writer, sheet_name=sheet, index=False)
            writer.save()

    def finish(self):
        close_window()
        self.curr_label = None
        self.exit = True

    def color_brown(self):
        self.curr_im = self.curr_im[..., ::-1]
        brown1 = np.array([0.41, 0.47, 0.6])
        brown2 = np.array([0.45, 0.4, 0.44])
        blue = np.array([0.39, 0.54, 0.8])

        # dist to brown:
        dist2brown1 = np.linalg.norm(self.curr_im.copy() - brown1, axis=-1, keepdims=True)
        dist2brown2 = np.linalg.norm(self.curr_im.copy() - brown2, axis=-1, keepdims=True)
        dist2brown = np.minimum(dist2brown1, dist2brown2)

        # dist blue brown:
        dist_blue_brown_1 = np.linalg.norm(brown1 - blue, axis=-1, keepdims=True)
        dist_blue_brown_2 = np.linalg.norm(brown2 - blue, axis=-1, keepdims=True)
        dist_blue_brown = np.minimum(dist_blue_brown_1, dist_blue_brown_2)

        eps = 0.03
        enhanced_im = np.concatenate([1 / (dist2brown + eps), np.ones_like(dist2brown) * (1 / (dist_blue_brown + eps)),
                                      eps * np.ones_like(dist2brown)], axis=2)
        enhanced_im = enhanced_im / enhanced_im.max()
        self.curr_im = self.curr_im[..., ::-1]
        return enhanced_im[..., ::-1]





    def onkey(self, event):
        """
        The main logic: performing the desired action according to the key pressed while analysing the current image
        :param event: The value return by cv2.waitKey() after pressing the keyboard:
        "escape" --> save results and exit
        "enter" --> save decision of current image and continue to next image
        "0" --> set label "NOT OK" for current image
        "1" --> set label "Roofing" for current image
        "2" --> set label "wire" for current image
        "3" --> set label "deep intubation" for current image
        "4" --> set label "Normal" for current image
         not supported functions {
                "space" --> color the image by brown color value intensity.
                ">" --> discard decision for the current image and move to next image
                "<" --> discard decision for the current image and move to previous image
                "Tab" --> move to the first image in current sheet that is not annotated yet. if all are annotated - move the next sheet.
                }
        :return: True if moving to next image or exiting, False if continue analysing the current image
        """

        # set the option for mouse click
        cv2.setMouseCallback('', self.mouse_click)
        #print(self.images[self.curr_idx])
        #s = self.images[self.curr_idx]
        #print(self.curr_sheet_idx)
        #print(s[s.find('img'):])
        #cv2.setWindowTitle('', s[s.find('img'):])
        #cv2.setWindowTitle('', " ")


        if event == 27:  # escape
            self.labels[self.curr_idx] = None
            self.finish()
            return True
        elif event == 13:  # enter
            if self.draw_rect:
                self.labels[self.curr_idx] = copy.copy(self.curr_label)
                self.labels[self.curr_idx + 1] = self.labels[self.curr_idx]
                print("------>", self.labels[self.curr_idx], self.labels[self.curr_idx - 1])
            else:
                self.labels[self.curr_idx] = copy.copy(self.curr_label)
                self.labels[self.curr_idx + 1] = self.labels[self.curr_idx]
                #self.labels[self.curr_idx] = None
                print("======>", self.labels[self.curr_idx], self.labels[self.curr_idx - 1])

            if self.draw_rect:
                self.x1[self.curr_idx] = copy.copy(self.curr_x1)
                self.y1[self.curr_idx] = copy.copy(self.curr_y1)
                self.x2[self.curr_idx] = copy.copy(self.curr_x2)
                self.y2[self.curr_idx] = copy.copy(self.curr_y2)

            else:
                self.x1[self.curr_idx] = None
                self.y1[self.curr_idx] = None
                self.x2[self.curr_idx] = None
                self.y2[self.curr_idx] = None
 #               self.draw_region(self.curr_x1, self.curr_y1, self.curr_x2, self.curr_y2)
            self.curr_idx += 1
            self.done += 1
            s = self.images[self.curr_idx]
            s1 = self.images[self.curr_idx - 1]
            #print(self.curr_sheet_idx)
            # Set the file name on the window's title bar
            cv2.setWindowTitle('', s1[s1.find('img'):] + " - was processed.     This image is  -    " + s[s.find('img'):])
            print("next image to be processed = ",s[s.find('img'):])
            if self.done % 100 == 0:
                print(f'done: {self.done} images so far. saving progress...')
                self.save_sheet()
            return True
        elif event == 49:  # 1
            self.curr_label = 1
            self.curr_im = self.color_edge()
            self.display = self.curr_im.copy()
            cv2.imshow('', self.display)
            #cv2.setWindowTitle('',"Roofing")
        elif event == 50:  # 2
            self.curr_label = 2
            self.curr_im = self.color_edge()
            self.display = self.curr_im.copy()
            cv2.imshow('', self.display)
        elif event == 51:  # 3
            self.curr_label = 3
            self.curr_im = self.color_edge()
            self.display = self.curr_im.copy()
            cv2.imshow('', self.display)
        elif event == 52:  # 4
            self.curr_label = 4
            self.curr_im = self.color_edge()
            self.display = self.curr_im.copy()
            cv2.imshow('', self.display)
        elif event == 53:  # 5
            self.curr_label = 5
            self.curr_im = self.color_edge()
            self.display = self.curr_im.copy()
            cv2.imshow('', self.display)
        elif event == 54:  # 6
            self.curr_label = 6
            self.curr_im = self.color_edge()
            self.display = self.curr_im.copy()
            cv2.imshow('', self.display)
        elif event == 55:  # 7
            self.curr_label = 7
            self.curr_im = self.color_edge()
            self.display = self.curr_im.copy()
            cv2.imshow('', self.display)
        elif event == 48:  # 0
            self.curr_label = 0
            self.curr_im = self.color_edge()
            self.display = self.curr_im.copy()
            cv2.imshow('', self.display)
        # elif event == 32:  # space
        #     self.space_on = not self.space_on
        #     if not self.space_on:
        #         self.display = self.curr_im.copy()
        #         cv2.imshow('', self.display)
        #     else:
        #         if self.curr_brown_im is None:
        #             self.curr_brown_im = self.color_brown()
        #         self.display = self.curr_brown_im
        #         cv2.imshow('', self.display)
        elif event == 46:  # >
            self.curr_label = None
            self.curr_idx += 1
            s = self.images[self.curr_idx]
            #print(self.curr_sheet_idx)
            #print(s[s.find('img'):])
            cv2.setWindowTitle('', s[s.find('img'):])

            return True
        elif event == 44:  # <
            self.curr_label = None
            self.curr_idx -= 1
            s = self.images[self.curr_idx]
            #print(self.curr_sheet_idx)
            #print(s[s.find('img'):])
            cv2.setWindowTitle('', s[s.find('img'):])

            if self.curr_sheet == 0:  # don't go back if this is the first sheet
                self.curr_idx = np.max([0, self.curr_idx])
            return True
        elif event == 9:  # Tab
            self.curr_label = None
            self.curr_idx = self.get_initial_image()
            return True
        elif event == 8:  # back
            self.curr_label = 0
            self.draw_rect = False
            print("back")
#            self.curr_idx = self.get_initial_image()
#            cv2.namedWindow("image")
#            self.draw_region(self.curr_x1, self.curr_y1, self.curr_x2, self.curr_y2)
#            cv2.setMouseCallback('', self.mouse_click)
#            cv2.imshow("image", self.display)
            return True
        else:
            pass
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--excel_file', type=str, required=True, help='full path to the excel file containing the '
                                                                      'list of images to annotate.\n The excel can '
                                                                      'contain multiple sheets, but each sheet should '
                                                                      'contain 2 columns with the headers "image path" '
                                                                      'and "label"')
    parser.add_argument('--root_images_dir',type=str, required=True, help='The path to the root images dir')
    args=parser.parse_args()
    print(args.excel_file)
    print(args.root_images_dir)
    annotator = HIC_Annotator(args.excel_file, args.root_images_dir)
    annotator.run(debug=False)


# WORKING CMD:
# annotation_tool.exe --excel_file "C:\Users\A Polonia\Desktop\GIL_PDL1\Antonio_Annotati
# ons_PDL1_02-008.xlsx" --root_images_dir "C:\Users\A Polonia\Desktop\GIL_PDL1\PDL1(SP142)-Springbio\\"
