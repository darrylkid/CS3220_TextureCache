from PIL import Image
import numpy as np
import math
import globals

from numpy.core.records import array


def get_texel_array_from_image(file_location):
    im=Image.open(file_location).convert('RGBA')
    pix_val = np.array(im)
    # pix_val=np.array(im.getdata())
    # print(im.size[0])
    # print(pix_val.size)
    # image2 = Image.fromarray(data[0][0]) # might help with piecing image back together
    # image2.show()
    return (pix_val, im.size[0], im.size[1]) # (pixels, width, height)

def convert_texel_array_to_6D(texels, width, height):
    max_w_or_h = max(width, height) # takes the maximum between width and height to determine # of superblocks
    min_w_or_h = min(width, height)
    num_super_blocks = math.ceil((max_w_or_h*max_w_or_h) / globals.super_block_size)
    super_block_width_in_blocks = math.ceil(math.sqrt(globals.super_block_size/globals.block_size))
    num_super_blocks_in_row = math.ceil(math.sqrt(num_super_blocks))
    #print(num_super_blocks_in_row)
    
    block = np.empty((4, 4), dtype=list)
    superblock = np.empty((super_block_width_in_blocks, super_block_width_in_blocks), dtype=list)
    superblocks = np.empty((num_super_blocks_in_row, num_super_blocks_in_row), dtype=list)
    
    blockoffsetx = 0
    blockoffsety = 0
    superblockoffsetx = 0
    superblockoffsety = 0
    counter = 0
    # Populate an array of superblocks 
    for a in range(num_super_blocks_in_row):
        for b in range(num_super_blocks_in_row):
            # Populate each 16x16 superblock with blocks
            for x in range (super_block_width_in_blocks):
                for y in range(super_block_width_in_blocks):
                    # Populate each 4x4 block with texels
                    for i in range(4): 
                        for j in range(4):
                            if ((i + blockoffsetx + superblockoffsetx >= min_w_or_h) or (j + blockoffsety + superblockoffsety >= min_w_or_h)):
                                block[i][j] = np.array([0,0,0,0])
                            else:
                                block[i][j] = np.array(texels[i + blockoffsetx + superblockoffsetx][j + blockoffsety + superblockoffsety])
                    superblock[x][y] = np.array(block)
                    block = np.empty((4, 4), dtype=list)
                    blockoffsety += 4
                blockoffsetx += 4
                blockoffsety = 0
                superblocks[a][b] = np.array(superblock)
            superblockoffsety += globals.super_block_wh
        superblockoffsetx += globals.super_block_wh
        superblockoffsety = 0
    
    return np.array(superblocks)
    
    
# TESTING -----------------------------------------------

data = get_texel_array_from_image(globals.file_location)
superblocks = convert_texel_array_to_6D(data[0], data[1], data[2])
a_file = open("log.txt", "w")

for row in superblocks:
    np.savetxt(a_file, row, fmt='%s')

a_file.close()



