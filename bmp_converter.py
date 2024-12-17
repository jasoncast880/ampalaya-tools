from PIL import Image
import sys

#my pixel to arr elements formatter
def to_rgb565(r,g,b):
    rgb565 = (((r&0xf8) << 8)  | ((g&0xfc)<<3) | (b>>3))
    #RRRRRGGG GGGBBBBB
    #seperate the bytes
    lo_byte = (rgb565)&0xFF
    hi_byte = (rgb565>>8)&0xFF

    return hi_byte, lo_byte
    

def bmp_to_c_array(filepath, array_name="image_data"):
    try:
        img = Image.open(filepath)

        if img.mode != "RGB":
            img = img.convert("RGB")

        #get pixel data, image dims
        width, height = img.size
        pixels = list(img.getdata())

        #convert the pixels to little endian
        rgb565_bytes = []
        for r,g,b in pixels:
            hi,lo = to_rgb565(r,g,b)
            rgb565_bytes.append(lo) #little endian ordering critical
            rgb565_bytes.append(hi)

        #format to c style array
        c_style_array = f"static const uint8_t {array_name}[] = {{\n"
        for i in range(0,len(rgb565_bytes),16):
            line = ", ".join(f"0x{byte:02X}"
            for byte in rgb565_bytes[i:i+16])
            c_style_array+=f"   {line},\n"

    except Exception as e:
        print(f"Error: {e}")
        return None

def main():                                                        
    if len(sys.argv) <3:
        print("Usage: python3 bmp_converter.py <bmp_filepath> <array_name>")
        return
    filepath = sys.argv[1]
    array_name = sys.argv[2]

    c_style_array = bmp_to_c_array(filepath, array_name)

    if c_style_array:
        header_file = f"{array_name}.h"
        with open(header_file, "w") as f:
            f.write(c_style_array)
        print(f"generated c header file saved to {header_file}")
    else:
        print("Failure")

if __name__ == "__main__":
    main()


