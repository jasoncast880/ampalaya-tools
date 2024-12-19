import numpy as np
from PIL import Imag
import sys
#purpose is to convert a tileset into a c style buffer array.
#i want to build this to hold pointers to all the datas.

def to_rgb565(r,g,b):
    rgb565 = (((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3))
    
    lo_byte = (rgb565) & 0xFF
    hi_byte = (rgb565 >> 8) & 0xFF

    return hi_byte, lo_byte

# this is distinct from the bmp_converter script because it will take each
# square and make it into its own buffer string;
# metadata to seperate the textures appropriately.
def bmp_tileset_to_c_array(filepath, array_name,tile_len, tiles_wide, tiles_tall): 
    try:
        img = Image.open(filepath)

        if img.mode != "RGB":
            img = img.convert("RGB")

        width, height = img.size
        pixels = list(img.getdata())

        #process the flipped pixels byte by byte 
        #big endian???
        rgb565_bytes = []
        for r,g,b in pixels:
            hi, lo = to_rgb565(r,g,b)
            rgb565_bytes.append(hi)
            rgb565_bytes.append(lo)
        

        #rgb565bytes reps the buf arr. (2by / pix)    
        for rows in tiles_tall:

        temp_byte_arr = [[0 for _ in range(tile_len^2)] for _ in range(tiles_wide)] #temp byte arr for each row of tiles cluster.
        #process the rows of pixels individually. put the tiles into temp buffers to concat afterwards
            for row_of_pixels in tile_len: 
                #reps the row of pixels. every <tile_len> pixels store in the next buffer.
                for tiles in tiles_wide:
                    for pix in tile_len:


                    
                     
#concat the array to include the tiles we processed in the last row

"""
        #flip image vertically; THIS IS HARDWARE-DEPENDENT i think
        flipped_pixels = []
        for y in range(height -1, -1, -1): #iterate rows from bot to top
            row_start = y*width
            row_end = row_start+width
            flipped_pixels.extend(pixels[row_start:row_end])
"""

        c_style_arr = ['']
        return c_style_arr

    except Exception as e:
        print(f"Error:{e}")
        return None


def main():
    if len(sys.argv) < 6:
        print("Usage: python3 tileset_converter.py <bmp_filepath> <array_name> <tile_len> <tiles_wide> <tiles_tall>")
        return
    filepath = sys.argv[1]
    array_name = sys.argv[2]
    tile_len   = sys.argv[3]
    tiles_wide = sys.argv[4]
    tiles_tall = sys.argv[5]

    #generate a header, also write commented metadata at the top; pointers to all the datas
    #array will be a buffer, each x bytes is one tile
    c_style_array = bmp_tileset_to_c_array(filepath, array_name, tile_len, tiles_wide, tiles_tall)

    if c_style_array:
        header_file = f"{array_name}.h"
        with open(header_file, "w") as f:
            f.write(c_style_array)
        print(f"Generated C header file saved to {header_file}")
    else:
        print("Failure to create file")

if __name__ == "__main__":
    main()

