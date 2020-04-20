#!/usr/bin/env python
#*****************************************************************************
# Big data processing
# Copyright (c) 2013-2020, Kenni Nilsson <kenil16@student.sdu.dk>
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
#*****************************************************************************
"""
Class with methods for big data processing
2020-03-13 Kenni First version
"""
import os
import sys

sys.path.append(os.getcwd())

import numpy as np
from rasterio.windows import Window
import rasterio
import matplotlib.pyplot as plt
#from rasterio.plot import show
import cv2
from object_segmentation import*

class data_processing:


    def __init__(self):
        self.img_width = int
        self.img_height = int
        self.block_size_width = int
        self.block_size_height = int
        self.overlap = int
        self.list_of_objects = []
        self.list_of_blocks = []
        self.objects_without_duplicates = []
        self.objects_duplicates = []

    def calculate_amount_of_blocks(self, src_img, block_size_width, block_size_height, overlap, partitions):
        
        with rasterio.open(src_img) as src:

            #Find dimentions of image
            self.img_height = src.height
            self.img_width = src.width
            self.block_size_height = block_size_height
            self.block_size_width = block_size_width
            self.overlap = overlap
            print("Image width: " + str(self.img_width))
            print("Image height: " + str(self.img_height))

            #Define current position of block
            block_x_upper = block_size_width
            block_x_lower = 0
            block_y_upper = block_size_height
            block_y_lower = 0
            reset_x_upper = False
            reset_y_upper = False

            while True:

                #Now place all blocks on a list
                block = []
                block.append(block_x_lower)
                block.append(block_x_upper)
                block.append(block_y_lower)
                block.append(block_y_upper)
                self.list_of_blocks.append(block)

                #See if whole image has been seperated in blocks
                if (reset_x_upper == True and reset_y_upper == True):
                    break

                #Update the y location of the block
                if(reset_x_upper == True):

                    block_x_lower = 0
                    block_x_upper = 0

                    if ( (block_y_upper+block_size_height) < (self.img_height) ):
                        block_y_lower = block_y_upper - overlap
                        block_y_upper = block_y_upper + block_size_height - overlap
                    else:
                        block_y_lower = block_y_upper - overlap
                        block_y_upper = block_y_upper + (self.img_height - block_y_upper)
                        reset_y_upper = True

                    reset_x_upper = False

                #Update the x location of the block
                if block_x_upper == 0:
                    block_x_upper = block_size_width
                else:
                    if ( (block_x_upper+block_size_width) < (self.img_width)):
                        block_x_lower = block_x_upper - overlap
                        block_x_upper = block_x_upper + block_size_height - overlap
                    else:
                        block_x_lower = block_x_upper - overlap
                        block_x_upper = block_x_upper + (self.img_width-block_x_upper)
                        reset_x_upper = True


    def create_partitions(self,partitions):
        
        #Make partitions in txt files based of blocks
        if (partitions > 0):
            
            #Define how many blocks one partiiton must hold
            blocks_in_partition = int(len(self.list_of_blocks)/partitions)
            
            #Define node number and counter 
            node = 1
            counter = 1
            write = 'w'
            
            #Write blocks to files to be used in parellel processing if partition is more than 1
            for item in self.list_of_blocks:
                if (counter == blocks_in_partition) and (node != partitions):
                    node = node + 1
                    counter = 0
                    write = 'w'
                else:
                    file_name = '../partitions/' + "node" + str(node) + '.txt'
                    f = open (file_name, write)
                    f.write(str(item[0]) + " " + str(item[1]) + " " + str(item[2]) + " " +str(item[3]) +  "\n")
                    f.close()
                    write = 'a'
                counter = counter + 1
            
        return len(self.list_of_blocks)

    def partition_blocks(self,interval):

        list_of_blocks = []
        for i in range(interval[0],interval[1]):
            list_of_blocks.append(self.list_of_blocks[i])
        self.list_of_blocks = list_of_blocks
            
    def read_blocks_from_file(self,file_name):

        #Read blocks from file 
        f = open (file_name, "r")

        for line in f:
            line = line.replace ('\n',' ')
            item = line.split(' ')

            data = []
            data.append(int(item[0]))
            data.append(int(item[1]))
            data.append(int(item[2]))
            data.append(int(item[3]))
            self.list_of_blocks.append(data)

        f.close()
        print("Number of blocks is: " + str(len(self.list_of_blocks)))

    def process_blocks(self,src_img,test_images,color_space,resize_factor,std_gain):

        objects = 0
        self.instance = obj_seg(test_images,color_space)

        with rasterio.open(src_img) as src:
            
            for block in self.list_of_blocks:

                #Read only as RGB
                img = np.stack([src.read(4-i, window=Window.from_slices((block[2],block[3]),(block[0],block[1]))) for i in range(1,4)], axis=-1)

                #Reduce the amount of brightness in the image 
                img = cv2.addWeighted(img,1,np.zeros(img.shape,img.dtype),0,-90)

                #Segment target image based on mean and std from test images
                self.instance.color_segmentation(img,color_space,resize_factor,std_gain)
                objects += self.instance.split_overlapping_objects()

        return objects 


if __name__ == "__main__":

    instance = data_processing()

    #Get amount of blocks
    #instance.calculate_amount_of_blocks("input/orthomosaic1.tif",500,500,50,4)
    instance.read_blocks_from_file("output/node1.txt")
    
    print(len(instance.list_of_blocks))
    #instance.partition_blocks([0,742])

    #Specify path to test images 
    test_images = ['input/test_image_pumpkin3.png', 'input/test_image_pumpkin4.png'] 
    print(instance.process_blocks("input/orthomosaic1.tif",test_images,"lab",1,4.5))
    
    #instance.read_objects_from_file('../output/objects/location_of_objects.txt')


