#bmp_to_TilesetArr.py

from PIL import Image
import sys

#define the indexed colors here

"""
INDEXED COLOR LEGEND : INDEX,CLR,RGB ; will change later
0-BLK-(0,0,0)
1-WHT-(255,255,255)
2-YLO-(255,249,130)
3-ORNG-(255,140,92)
4-GRN-(99,255,186)
5-DARK BLU-(0,8,113)

255- !!!ALPHA PIXEL!!! - SPRITE OBJECT ONLY
"""

def to_indexed_value(r, g, b):
    value = 69 

    if((r==0)&(g==0)&(b==0)): #BLK
        value = 0
    elif((r==255)&(g==255)&(b==255)): #WHT
        value = 1
    elif((r==255)&(g==249)&(b==130)): #YLO
        value = 2
    elif((r==255)&(g==140)&(b==92)): #ORNG
        value = 3
    elif((r==99)&(g==255)&(b==186)): #GRN
        value = 4
    elif((r==0)&(g==8)&(b==113)): #DARK BLU
        value = 5
    elif((r==255)&(g==0)&(b==113)): #PURP pure ALPHA (filter this out)
        value = 255

    return value

def tileset_to_array(filepath, array_name, tile_len):
    try:
        # Ensure tile_len is an integer
        tile_len = int(tile_len)

        # Open the image and ensure it's in RGB format
        img = Image.open(filepath)
        if img.mode != "RGB":
            img = img.convert("RGB") # 3x8(pix-bytes) of true color

        bmp_width, bmp_height = img.size
        pixels = list(img.getdata())

        # Flip the image vertically
        flipped_pixels = []
        for y in range(bmp_height - 1, -1, -1):
            row_start = y * bmp_width
            row_end = row_start + bmp_width
            flipped_pixels.extend(pixels[row_start:row_end])
        
        #convert to indexed colors, let the HAL handle the rgb conversion

        # Convert pixels to indexed-color format
        indexed_array = []
        for r, g, b in flipped_pixels:
            indexed_value = to_indexed_value(r, g, b)
            indexed_array.append(indexed_value)

        # Tile processing: rearrange the data into tiles
        tile_ready_arr = []  # Final tile data

        tiles_wide = bmp_width // tile_len
        tiles_tall = bmp_height // tile_len
        num_tiles = tiles_wide * tiles_tall

        print(f"tiles wide: {tiles_wide}\n")
        print(f"tiles tall: {tiles_tall}\n")
        print(f"num tiles: {num_tiles}\n")

        bufPtr = 0              
        for i in range(tiles_tall): #for each given tile row
            bufPtr=(i*tile_len)*bmp_width #reset bufPtr to the bottom left pxiel of the tile-row (this line for edge case scenarios)
            for j in range(tiles_wide): #within a given tile row
                for k in range(tile_len):  # Loop over (and append) each row within a single given tile to the tile_ready_arr
                    start = bufPtr+(tile_len*j);
                    end = start+tile_len;

                    tile_ready_arr.extend(indexed_array[start:end])
                    bufPtr += bmp_width
                bufPtr=(i*tile_len)*bmp_width #reset bufPtr to the bottom left pxiel of the tile-row

        # Convert the tile data into a C-style array format
        c_style_array = f"const uint8_t {array_name}[] = {{\n"
        for i in range(0, len(tile_ready_arr), tile_len):
            line = ", ".join(f"{int_val}" for int_val in tile_ready_arr[i:i+tile_len])
            c_style_array += f"   {line},\n"
        c_style_array += "};\n"  # Close the array

        return c_style_array

    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    # Check arguments
    if len(sys.argv) < 4:
        print("Usage: python3 bmp_to_TilesetArr.py <bmp_filepath> <array_name> <tile_len>")
        return
    filepath = sys.argv[1]
    array_name = sys.argv[2]
    tile_len = sys.argv[3]

    # Generate the C-style array and write it to a header file
    c_style_array = tileset_to_array(filepath, array_name, tile_len)

    if c_style_array:
        asset_file = f"{array_name}.cpp"
        with open(asset_file, "w") as f:
            f.write(c_style_array)
        print(f"Generated .cpp file saved to {asset_file}")
    else:
        print("Failure to create file")

if __name__ == "__main__":
    main()

