#!/usr/bin/python
#/****************************************************************************
# Detect objects based on color segmentation
# Copyright (c) 2020-2020, Kenni Nilsson <kenil16@student.sdu.dk>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the copyright holder nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#****************************************************************************/
'''
This file contains a Python class to segment objects based on color segmentation.

2020-02-24 Kenni added class and functions 
'''

import cv2
import numpy as np
import matplotlib.pyplot as plt

from skimage.feature import peak_local_max
from skimage.morphology import watershed
from scipy import ndimage 
import imutils

class obj_seg:

    def __init__(self,test_img,color_space):
        self.test_images = [] #Test images used in color segmentation 
        self.image_mask = None #Remaining objects after color segmentation 
        self.target_image = None #Image for which to make color segmentation 
        self.mean = [] #Mean for all channels 
        self.std = [] #Standard deviation fro all channels 
        self.color_space = None #The choosing color space
        self.labels = None # 
        self.number_of_objects = None
        self.objects_position = []

        #Find mean and standard diviation from test image in all channels 
        self.find_mean_std_from_test_img(test_img,color_space)


    def find_mean_std_from_test_img(self,test_img,color_space):
        
        #Load test images 
        for item in test_img:
            if (color_space == 'lab'):
                lab_img = cv2.imread(item)
                lab_img = cv2.cvtColor(lab_img, cv2.COLOR_BGR2LAB) 
                self.test_images.append(lab_img)
            else:
                self.test_images.append(cv2.imread(item))
                
        #Find mean and std for all channels 
        for item in self.test_images:
            mean, std = cv2.meanStdDev(item)
            if (len(self.mean) == 1):
                self.mean = self.mean + mean
                self.std = self.std + std
            else: 
                self.mean.append(mean)
                self.std.append(std)
                
        #Get the average value from all test images 
        if (len(test_img) > 1):
            self.mean = self.mean/(len(test_img))
            self.std = self.std/(len(test_img))
            
    def color_segmentation(self,img,color_space,resize_factor,std_gain):

        #Load test images
        self.target_image = img #cv2.imread(img)
        self.color_space = color_space
        if (color_space == 'lab'):
            self.target_image  = cv2.cvtColor(self.target_image, cv2.COLOR_BGR2LAB)
        
        #Resize images
        dim = self.target_image.shape
        self.target_image = cv2.resize(self.target_image,(int(dim[1]/resize_factor),int(dim[0]/resize_factor)))

        #Find objects based on mean and std
        lower_bound = np.array([self.mean[0]-self.std[0]*std_gain])
        upper_bound = np.array([self.mean[0]+self.std[0]*std_gain])
        self.image_mask = cv2.inRange(self.target_image,lower_bound,upper_bound)

        #Define kernel size for noise removel
        kernel = cv2.getStructuringElement(shape=cv2.MORPH_ELLIPSE,ksize=(9,9))
        
        #Use morphology (Just erosion (remove pixels from ojects) and dilation (add pixels to obejct)) to remove noise 
        self.image_mask = cv2.morphologyEx(self.image_mask,cv2.MORPH_OPEN,kernel)

        #cv2.imwrite('../output/' + figure_name + '.png',self.image_mask)

    def split_overlapping_objects(self):

        #Now compute the euclidian distance to the closest zero (background pixels) for each foreground pixel (Think of brush fire algorithm)
        D = ndimage.distance_transform_edt(self.image_mask)
        
        #Determine the local maximum in the map (Find midpoint of shapes)
        local_max = peak_local_max(D,indices=False,min_distance=5,labels=self.image_mask)
        
        #Give pixel value to clostest local max
        markers = ndimage.label(local_max,structure=np.ones((3,3)))[0]
        
        #Use watershed to distinguish objects from from another 
        self.labels = watershed(-D,markers,mask=self.image_mask)
        
        self.number_of_objects = len(np.unique(self.labels))-1
        #print("[INFO] {} unique segments found".format(len(np.unique(self.labels))-1))
        #print('Split overlapping objects succeded..')

        return  self.number_of_objects 

    def distinct_objects_position(self): 

        self.objects_position = []

        if self.color_space == 'lab':
            image = cv2.cvtColor(self.target_image,cv2.COLOR_Lab2BGR)
            img_gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        else:
            image = self.target_image
            img_gray = cv2.cvtColor(self.target_image,cv2.COLOR_BGR2GRAY)

        for label in np.unique(self.labels):
            #If the label is zero, it is the background and ignores it
            if (label == 0):
                continue
            #Otherwise label the region and draw it on the mask
            mask = np.zeros(img_gray.shape, dtype="uint8")
            mask[self.labels == label] = 255
            #Detect contours in the mask and grab the largest one
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            c = max(cnts, key=cv2.contourArea)
            ((x, y), r) = cv2.minEnclosingCircle(c)

            pos = []
            pos.append(int(x))
            pos.append(int(y))
            pos.append(r)
            self.objects_position.append(pos)

        return self.objects_position
            
    def encircle_distinct_objects(self,fig_name): 
        
        if self.color_space == 'lab':
            image = cv2.cvtColor(self.target_image,cv2.COLOR_Lab2BGR)
            img_gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        else:
            image = self.target_image
            img_gray = cv2.cvtColor(self.target_image,cv2.COLOR_BGR2GRAY)
            
        for label in np.unique(self.labels):
	    #If the label is zero, it is the background and ignores it
            if (label == 0):
                continue
	    #Otherwise label the region and draw it on the mask
            mask = np.zeros(img_gray.shape, dtype="uint8")
            mask[self.labels == label] = 255
	    #Detect contours in the mask and grab the largest one
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            c = max(cnts, key=cv2.contourArea)
	    #Draw a circle enclosing the object
            ((x, y), r) = cv2.minEnclosingCircle(c)
            cv2. circle(image, (int(x), int(y)), int(r), (0, 255, 0), 1)
        
        cv2.imwrite(fig_name, image)
        print('Objecst succesfulle encircled..')
        

if __name__ == "__main__":

    #Make object from object segmentation class 
    instance = obj_seg()

    #Specify path to images 
    test_images = ['../input/test_image_pumpkin1.png', '../input/test_image_pumpkin2.png','../input/test_image_pumpkin3.png','../input/test_image_pumpkin4.png'] 
    target_image = ['../input/DJI_0237.JPG']
    
    #Segment target image based on mean and std from test images 
    instance.color_segmentation(target_image,test_images,'lab','../output/lab_segmentation',2,6)
    instance.split_overlapping_objects()
    instance.encircle_distinct_objects('../output/contours_mask.png')
    instance.avg_objects_per_area(13.2,8.8,5472,3078,54.2)
