from PIL import Image
import sys

# My pixel to arr elements formatter
def to_rgb565(r, g, b):
    rgb565 = (((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3))
    # RRRRRGGG GGGBBBBB
    # Separate the bytes
    lo_byte = (rgb565) & 0xFF
    hi_byte = (rgb565 >> 8) & 0xFF

    return hi_byte, lo_byte

def bmp_to_c_array(filepath, array_name="image_data"):
    try:
        img = Image.open(filepath)

        if img.mode != "RGB":
            img = img.convert("RGB")

        # Get pixel data, image dimensions
        width, height = img.size
        pixels = list(img.getdata())

        # Flip the image vertically
        flipped_pixels = []
        for y in range(height - 1, -1, -1):  # Iterate rows from bottom to top
            row_start = y * width
            row_end = row_start + width
            flipped_pixels.extend(pixels[row_start:row_end])

        rgb565_bytes = []
        for r, g, b in flipped_pixels:  # Process flipped_pixels
            hi, lo = to_rgb565(r, g, b)
            rgb565_bytes.append(hi)
            rgb565_bytes.append(lo)  

        # Format to C-style array
        c_style_array = f"static const uint8_t {array_name}[] = {{\n"
        for i in range(0, len(rgb565_bytes), 16):
            line = ", ".join(f"0x{byte:02X}" for byte in rgb565_bytes[i:i+16])
            c_style_array += f"   {line},\n"
        c_style_array += "};\n"  # Close the array properly

        return c_style_array

    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 bmp_converter.py <bmp_filepath> <array_name>")
        return
    filepath = sys.argv[1]
    array_name = sys.argv[2]

    c_style_array = bmp_to_c_array(filepath, array_name)

    if c_style_array:
        header_file = f"{array_name}.cpp"
        with open(header_file, "w") as f:
            f.write(c_style_array)
        print(f"Generated .cpp file saved to {header_file}")
    else:
        print("Failure")

if __name__ == "__main__":
    main()

