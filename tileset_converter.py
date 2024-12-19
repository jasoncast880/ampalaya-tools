from PIL import Image
import sys
#purpose is to convert a tileset into a c style buffer array.
#i want to build this to hold pointers to all the datas.

def to_rgb565(r,g,b):
    rgb565 = (((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3))
    
    lo_byte = (rgb565) & 0xFF
    hi_byte = (rgb565 >> 8) & 0xFF

    return hi_byte, lo_byte

def bmp_tileset_to_c_array(filepath,array_name,tile_len):
    try:
        img = Image.open(filepath)

        if img.mode != "RGB":
            img = img.convert("RGB")

        width, height = img.size
        pixels = list(img.getdata())  # Flattened list of (r, g, b)

        # Convert to RGB565 format
        rgb565_bytes = []
        for r, g, b in pixels:
            hi, lo = to_rgb565(r, g, b)
            rgb565_bytes.append(hi)
            rgb565_bytes.append(lo)

        # Image tile properties
        tile_len = 8  # Example tile length
        tiles_wide = width // tile_len
        tiles_tall = height // tile_len

        # Reorganize bytes into tiled format
        rgb565_bytes_reordered = []
        for tile_row in range(tiles_tall):
            temp_byte_arr = [[] for _ in range(tiles_wide)]  # Buffers for each tile in a row

            for row_in_tile in range(tile_len):  # Process pixel rows within a tile
                start = (tile_row * width * tile_len) + (row_in_tile * width)
                for tile_col in range(tiles_wide):
                    tile_start = start + (tile_col * tile_len * 2)
                    tile_pixels = rgb565_bytes[tile_start:tile_start + tile_len * 2]
                    temp_byte_arr[tile_col].extend(tile_pixels)

            for tile in temp_byte_arr:
                rgb565_bytes_reordered.extend(tile)

        # Format the reordered data into a C array
        c_array = "const uint8_t image_data[] = {\n"
        for i, byte in enumerate(rgb565_bytes_reordered):
            c_array += f"0x{byte:02X}, "
            if (i + 1) % 16 == 0:  # Add a newline every 16 bytes for readability
                c_array += "\n"
        c_array = c_array.rstrip(", \n") + "\n};"  # Remove trailing comma and add closing brace

        # Output the C array
        return(c_array)

    except Exception as e:
        print(f"Error: {e}")
        return None



def main():
    if len(sys.argv) < 4:
        print("Usage: python3 tileset_converter.py <bmp_filepath> <array_name> <tile_len>")
        return
    filepath = sys.argv[1]
    array_name = sys.argv[2]
    tile_len   = sys.argv[3]

    #generate a header, also write commented metadata at the top; pointers to all the datas
    #array will be a buffer, each x bytes is one tile
    c_style_array = bmp_tileset_to_c_array(filepath, array_name, tile_len)

    if c_style_array:
        header_file = f"{array_name}.h"
        with open(header_file, "w") as f:
            f.write(c_style_array)
        print(f"Generated C header file saved to {header_file}")
    else:
        print("Failure to create file")

if __name__ == "__main__":
    main()

