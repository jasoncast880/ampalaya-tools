from PIL import Image
import sys

def rgb_to_bgr565(r, g, b):
    """
    Convert an RGB triplet to a 16-bit BGR565 value in big-endian order.
    """
    # Convert RGB to 16-bit BGR565
    bgr565 = ((b & 0xF8) << 8) | ((g & 0xFC) << 3) | (r >> 3)
    
    # Separate into two bytes (big-endian)
    high_byte = (bgr565 >> 8) & 0xFF
    low_byte = bgr565 & 0xFF
    
    return high_byte, low_byte

def bmp_to_c_array(file_path, array_name="image_data"):
    try:
        # Open the BMP image
        img = Image.open(file_path)
        
        # Ensure the image is in RGB mode
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Flip the image vertically (bottom to top)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

        # Get pixel data and image dimensions
        width, height = img.size
        pixels = list(img.getdata())
        
        # Convert pixels to BGR565 (big-endian)
        bgr565_bytes = []
        for r, g, b in pixels:
            high, low = rgb_to_bgr565(r, g, b)
            bgr565_bytes.append(high)
            bgr565_bytes.append(low)

        # Generate the C-style array as a string
        c_array = f"static const uint8_t {array_name}[] = {{\n"
        for i in range(0, len(bgr565_bytes), 16):  # 16 bytes per line for readability
            line = ", ".join(f"0x{byte:02X}" for byte in bgr565_bytes[i:i+16])
            c_array += f"    {line},\n"
        c_array += "};\n"
        
        # Add metadata about image dimensions
        c_array += f"\n// Image dimensions: {width}x{height}\n"
        return c_array

    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    if len(sys.argv) < 3:
        print("Usage: python bmp_to_c_array.py <bmp_file_path> <array_name>")
        return

    file_path = sys.argv[1]
    array_name = sys.argv[2]

    c_array = bmp_to_c_array(file_path, array_name)

    if c_array:
        header_file = f"{array_name}.h"
        with open(header_file, "w") as f:
            f.write(c_array)
        print(f"Generated C header file saved to {header_file}")
    else:
        print("Failed to convert BMP to C array.")

if __name__ == "__main__":
    main()

