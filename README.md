# 6D Blocking Python Implementation

## Milestone 2 Progress

### Varshita

- Implemented functionality of converting an image into texels with RGBA values.
- Converted a linear array of texels into a 6D blocking structure
- Wrote the functions `get_texel_array_from_image()` and `convert_texel_array_to_6D()` within `Image_to_6D.py` file to accomplish the above two tasks.

### Darryl

## Code Documentation

## `Image_to_6D.py`

### `get_texel_array_from_image()`

#### **Description**:

This function takes in a file path location to a desired image and utilizes the Pillow python library to convert it into texels with RGBA values. It is then converted into a numpy array containing a linear list of [R, G, B, A] values.

#### **Input**:

- `file_location`: The path to an image

#### **Output**:

A tuple containing a linear array of pixels in RGBA format and the height and width of the image in pixels.

### `convert_texel_array_to_6D()`

#### **Description**:

This function converts a linear array of texels into the 6D blocking representation by creating a 6D array structure holding superblocks, blocks, and texels. The size of a superblock and block are 16 x 16 are 4 x 4 texels respectively. For images that are smaller than the superblock or block size, all of the surrounding block values are padded with zeros.

#### **Input**:

- `texels`: A linear array of texels containing [R, G, B, A] values
- `width`: The width of an image
- `height`: The height of an image

#### **Output**:

A 6D array containing superblocks, blocks, and texels.
