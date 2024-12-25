from PIL import Image
import sys

def to_rgb565(r,g,b):
    rgb565 = (((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3))
    
    lo_byte = (rgb565) & 0xFF
    hi_byte = (rgb565 >> 8) & 0xFF

    return hi_byte, lo_byte

def tileset_to_array(filepath,array_name,tile_len):
    try:
        img = Image.open(filepath)
        if img.mode != "RGB":
            img = img.convert("RGB")

        bmp_width, bmp_height = img.size
        pixels = list(img.getdata())

        #flip the img??
        flipped_pixels = []
        for y in range(bmp_height -1, -1, -1):
            row_start = y*bmp_width
            row_end = row_start+bmp_width
            flipped_pixels.extend(pixels[row_start:row_end])
        
        rgb565_bytes = []
        for r, g, b in flipped_pixels:
            hi, lo = to_rgb565(r, g, b)
            rgb565_bytes.append(hi)
            rgb565_bytes.append(lo)

        #tile converting section starts here
        #for this section i'm going to reorder 565

        tile_ready_bytes = [] #append, copy on the thing

        tilerow_buf_size = 16*tile_len # 16-bits/pix * tile's length. 
        tiles_wide = bmp_width//tile_len
        tiles_tall = bmp_height//tile_len
        num_tiles = tiles_wide*tiles_tall

        bufPtr = 0
        for i in range(num_tiles):
            for j in range(tile_len):
                tile_ready_bytes.append(rgb565_bytes[bufPtr:bufPtr+tilerow_buf_size])
                bufPtr+=bmp_width
            bufPtr=Nat(i*tile_len) #after tile, offset to the next pix

        c_style_array = f"static const uint8_t {array_name}[] = {{\n"
        for i in range(0, len(tile_ready_bytes), 16):
            line = ", ".join(f"0x{byte:02X}" for byte in tile_ready_bytes[i:i+16])
            c_style_array += f"   {line},\n"
        c_style_array += "};\n" #close array

        return c_style_array

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
    c_style_array = tileset_to_array(filepath, array_name, tile_len)

    if c_style_array:
        header_file = f"{array_name}.h"
        with open(header_file, "w") as f:
            f.write(c_style_array)
        print(f"Generated C header file saved to {header_file}")
    else:
        print("Failure to create file")

if __name__ == "__main__":
    main()

