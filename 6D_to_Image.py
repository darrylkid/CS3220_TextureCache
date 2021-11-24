from PIL import Image, ImageDraw
import numpy as np
from math import log
import math
import globals
import Image_to_6D as i26

from numpy.core.records import array


def linear(superblocks) -> list:
    ''' Returns a 1D linear array given a numpy 6D data structure'''
    linear_list = []
    i = 0

    ''' 
        Algorithm Explanation: 
        There are three layers of hierarchy: superblock, block and texel.

        For each hierarchy, first access the row and access the specific 
        unit from the row. Once the unit is accessed, within that unit are
        more granular units of the next hierachy. This continues until
        the smallest unit, the texel has been reached. Each texel is added
        to the linear list.
    '''
    superblock_rows = len(superblocks) 

    for superblock_row_index in range(superblock_rows):
        superblock_row = superblocks[superblock_row_index]
        num_superblocks_in_row = len(superblock_row) 

        for superblock_index in range(num_superblocks_in_row):
            superblock_unit = superblock_row[superblock_index]
            block_rows = len(superblock_unit)

            for block_row_index in range(block_rows):
                block_row = superblock_unit[block_row_index]
                num_blocks_in_row = len(block_row)

                for block_index in range(num_blocks_in_row):
                    block_unit = block_row[block_index]
                    texel_rows = len(block_unit)

                    for texel_row_index in range(texel_rows):
                        texel_row = block_unit[texel_row_index]
                        num_texels_in_row = len(texel_row)

                        for texel_index in range(num_texels_in_row):
                            texel_unit = texel_row[texel_index]

                            # Add texel to linear list.
                            linear_list.append(texel_unit.tolist())
                            i += 1
    
    return linear_list

def address(t_x, t_y, image_w, base_address = 0) -> int:
    '''
        Returns the address for the 6D linear data structure given
        the texture coordinate.

        Coordinate System:

        (0, 0) -----------------> +x
              |
              |
              |
              |
              |
              |
              |
              v
            +y

        @param t_x texel x component
        @param t_y texel y component
        @param image_w width of the image in texels
    '''

    radix = 2 # for the log function we will later use

    block_w = globals.block_wh
    block_h = globals.block_wh
    block_area = block_w * block_h

    # The log version of these variables will be
    # used to shift by output-of-log amount. This
    # is a more efficient than multiplying, which takes
    # multiple cycles.
    l_block_width = int(log(block_w, radix))
    l_block_height = int(log(block_h, radix))
    l_block_area = int(log(block_area, radix))

    block_x = t_x >> l_block_width
    block_y = t_y >> l_block_height
    l_block_row_area = int(log(image_w * block_h, radix))
    block_address = base_address \
                  + (block_y << l_block_row_area) \
                  + (block_x << l_block_area)

    # The bitwise AND acts as a more efficient modulo operation
    t_x_relative_to_block = t_x & (block_w - 1) 
    t_y_relative_to_block = t_y & (block_h -1)
    texel_address = block_address \
                  + (t_y_relative_to_block << l_block_width) \
                  + t_x_relative_to_block

    return texel_address

def linear1D(linear6D, image_w, image_l):
    '''
    Converts a 6D block representation stored in a linear array
    into a 1D block representation stored in a linear array.
    '''
    linear1D_list = []
    i = 0

    num_superblocks_x = math.ceil(image_w / globals.super_block_wh)
    num_superblocks_y = math.ceil(image_l / globals.super_block_wh)
    num_blocks_x = int(globals.super_block_wh / globals.block_wh)
    num_blocks_y = num_blocks_x
    num_texels_x = globals.block_wh
    num_texels_y = num_texels_x

    for superblock_row_index in range(num_superblocks_y):
        for superblock_col_index in range(num_superblocks_x):
            superblock_address = image_w * globals.super_block_wh * superblock_row_index \
                                    + globals.super_block_wh * superblock_col_index

            for block_row_index in range(num_blocks_y):
                for block_col_index in range(num_blocks_x):
                    block_address = image_w * globals.block_wh * block_row_index \
                                       + globals.block_wh * block_col_index

                    for texel_row_index in range(num_texels_x):
                        for texel_col_index in range(num_texels_y):
                            texel_address = superblock_address + block_address \
                                            + image_w * texel_row_index \
                                            + texel_col_index

                            linear1D_list.append(linear6D[texel_address])
                            i += 1
                            
    return linear1D_list       

def convert_1D_to_image(linear1D, image_file_name, image_w, image_l):
    '''
        Saves a png image given a 6D block representation stored in
        a linear array.

        linear6D : 6D blocks stored in a linear array of type list
                   not a numpy array
        image_file_name : image_name name of the file to save of type string
                          e.g. convert_to_image(X, 'soccer', X) -> soccer.png
        image_w : image width in texels of type int
        image_l : image length in texels of type int

    '''

    output_img = Image.new(mode = 'RGBA', size = (image_w, image_l))
    image_2D = []
    
    for image_row_index in range(image_l):
        image_row = []
        for image_col_index in range(image_w):
            address = image_w * image_row_index + image_col_index
            texel = linear1D[address]
            image_row.append(texel)
            output_img.putpixel((image_col_index, image_row_index), tuple(texel))
        image_2D.append(image_row)

    output_img.save("./" + image_file_name + ".png", bitmap_format = 'png')


def convert_to_image(linear6D, image_file_name, image_w, image_l):
    '''
        Saves a png image given a 6D block representation stored in
        a linear array.

        linear6D : 6D blocks stored in a linear array of type list
                   not a numpy array
        image_file_name : image_name name of the file to save of type string
                          e.g. convert_to_image(X, 'soccer', X) -> soccer.png
        image_w : image width in texels of type int
        image_l : image length in texels of type int

    '''
    linear1D_list = linear1D(linear6D, image_w, image_l)
    output_img = Image.new(mode = 'RGBA', size = (image_w, image_l))
    image_2D = []
    
    for image_row_index in range(image_l):
        image_row = []
        for image_col_index in range(image_w):
            address = image_w * image_row_index + image_col_index
            texel = linear1D_list[address]
            image_row.append(texel)
            output_img.putpixel((image_col_index, image_row_index), tuple(texel))
        image_2D.append(image_row)

    output_img.save("./" + image_file_name + ".png", bitmap_format = 'png')

    


''' ---------------- Testing ------------------------- '''
# Check the original unprocessed rgbw image. Notice how each row is a unique color.
# A 6D transformation should output an image such that the colors alternate every
# 4 texels inside the row. The output image is rendered 
# in the order of a linear 6D blocking array.
# 
# Each cache line access is now a square section of the image
# instead of a scan line. 

im=Image.open(globals.file_location).convert('RGBA')
image_w_in_texels = im.width
image_l_in_texels = im.height

data = i26.get_texel_array_from_image(globals.file_location)
superblocks = i26.convert_texel_array_to_6D(data[0], data[1], data[2])

linear6D = linear(superblocks)

def test_6D_access():
    texel = linear6D[address(4, 2, image_w_in_texels)]
    return texel

def test_6D_to_1D_conversion():
    linear1D_list = linear1D(linear6D, image_w_in_texels, image_l_in_texels)
    return linear1D_list

def test_image_conversion():
    convert_to_image(linear6D, "./" + globals.file_name + "_out"
                        , image_w_in_texels, image_l_in_texels)

def test_Image_to_6D():
    convert_1D_to_image(linear(superblocks), "./" + globals.file_name + "_out"
                        , image_w_in_texels, image_l_in_texels)
    return

#test_6D_access()
#test_6D_to_1D_conversion()
test_image_conversion()
#test_Image_to_6D()


