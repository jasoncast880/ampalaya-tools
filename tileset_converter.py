from PIL import Image
import sys

def to_rgb565(r, g, b):
    # Convert RGB to RGB565 (16-bit color)
    rgb565 = (((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3))
    
    lo_byte = (rgb565) & 0xFF
    hi_byte = (rgb565 >> 8) & 0xFF

    return hi_byte, lo_byte

def tileset_to_array(filepath, array_name, tile_len):
    try:
        # Ensure tile_len is an integer
        tile_len = int(tile_len)

        # Open the image and ensure it's in RGB format
        img = Image.open(filepath)
        if img.mode != "RGB":
            img = img.convert("RGB")

        bmp_width, bmp_height = img.size
        pixels = list(img.getdata())

        # Flip the image vertically
        flipped_pixels = []
        for y in range(bmp_height - 1, -1, -1):
            row_start = y * bmp_width
            row_end = row_start + bmp_width
            flipped_pixels.extend(pixels[row_start:row_end])
        
        # Convert pixels to RGB565 format (hi and lo byte)
        rgb565_bytes = []
        for r, g, b in flipped_pixels:
            hi, lo = to_rgb565(r, g, b)
            rgb565_bytes.append(hi)
            rgb565_bytes.append(lo)

        # Tile processing: rearrange the data into tiles
        tile_ready_bytes = []  # Final tile data

        tiles_wide = bmp_width // tile_len
        tiles_tall = bmp_height // tile_len
        num_tiles = tiles_wide * tiles_tall

        print(f"tiles wide: {tiles_wide}\n")
        print(f"tiles tall: {tiles_tall}\n")
        print(f"num tiles: {num_tiles}\n")

        bufPtr = 0              
        for i in range(tiles_tall): #for each given tile row
            bufPtr=i*tile_len*bmp_width*2 #reset the bufPtr to the bot left pix of the tile-row
            for j in range(tiles_wide): #within a given tile row
                for k in range(tile_len):  # Loop over each row within a single given tile
                    start = bufPtr + (j*tile_len*2);
                    end = start + (tile_len * 2)
                    tile_ready_bytes.extend(rgb565_bytes[start:end])
                    bufPtr += bmp_width * 2  # Move to the next tile row???
                bufPtr=i*tile_len*bmp_width*2 #reset the bufPtr to the bot left pix of the tile-row

        # Convert the tile data into a C-style array format
        c_style_array = f"static const uint8_t {array_name}[] = {{\n"
        for i in range(0, len(tile_ready_bytes), 16):
            line = ", ".join(f"0x{byte:02X}" for byte in tile_ready_bytes[i:i+16])
            c_style_array += f"   {line},\n"
        c_style_array += "};\n"  # Close the array

        return c_style_array

    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    # Check arguments
    if len(sys.argv) < 4:
        print("Usage: python3 tileset_converter.py <bmp_filepath> <array_name> <tile_len>")
        return
    filepath = sys.argv[1]
    array_name = sys.argv[2]
    tile_len = sys.argv[3]

    # Generate the C-style array and write it to a header file
    c_style_array = tileset_to_array(filepath, array_name, tile_len)

    if c_style_array:
        header_file = f"{array_name}.cpp"
        with open(header_file, "w") as f:
            f.write(c_style_array)
        print(f"Generated .cpp file saved to {header_file}")
    else:
        print("Failure to create file")

if __name__ == "__main__":
    main()

