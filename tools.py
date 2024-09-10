import zlib
import struct
import zipfile
import struct
from pyzbar import pyzbar
from PIL import Image
def decode_QRcode(PIL_image):
    result = pyzbar.decode(PIL_image)
    if not result:
        return False
    else:
        return result[0].data
def find_embedded_files(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()

    offset = 0
    results = []

    while True:
        # Search for JPEG files
        start_jpeg = data.find(b'\xff\xd8', offset)
        if start_jpeg == -1:
            break
        
        end_jpeg = data.find(b'\xff\xd9', start_jpeg)
        if end_jpeg == -1:
            break
        
        size_jpeg = end_jpeg - start_jpeg + 2
        results.append(('JPEG', start_jpeg, size_jpeg))
        offset = end_jpeg + 2

    # Check for PNG files
    png_header = b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a' # PNG signature
    offset = 0
    while True:
        start_png = data.find(png_header, offset)
        if start_png == -1:
            break

        # Get the size of the PNG file
        size_offset = start_png + 8
        size = 0
        chunk_type = b'IHDR'
        while chunk_type != b'IEND':
            chunk_size = int.from_bytes(data[size_offset:size_offset+4], byteorder='big')
            chunk_type = data[size_offset+4:size_offset+8]
            size += chunk_size + 12  # Add 12 bytes for chunk type, length and CRC
            size_offset += chunk_size + 12
        
        results.append(('PNG', start_png, size))
        offset = start_png + size

    # Check for GIF files
    gif_header = b'\x47\x49\x46\x38' # GIF signature
    offset = 0
    while True:
        start_gif = data.find(gif_header, offset)
        if start_gif == -1:
            break
        
        size_offset = start_gif + 6
        size = int.from_bytes(data[size_offset:size_offset+3], byteorder='little')
        results.append(('GIF', start_gif, size + 10))
        offset = start_gif + size + 10

    # Check for ZIP files
    with open(file_path, 'rb') as f:
        try:
            zip_file = zipfile.ZipFile(f)
            for file_info in zip_file.infolist():
                start_zip = file_info.header_offset
                results.append(('ZIP', start_zip, file_info.compress_size+file_info.header_offset))
        except:
            pass

    # Check for PDF files
    pdf_header = b'%PDF-'
    offset = 0
    while True:
        start_pdf = data.find(pdf_header, offset)
        if start_pdf == -1:
            break

        end_pdf = data.find(b'%%EOF', start_pdf)
        if end_pdf == -1:
            break

        size_pdf = end_pdf - start_pdf + 5
        results.append(('PDF', start_pdf, size_pdf))
        offset = end_pdf + 5

    # Check for TIFF files
    tiff_header = b'II\x2A\x00' # Little-endian TIFF signature
    offset = 0
    while True:
        start_tiff = data.find(tiff_header, offset)
        if start_tiff == -1:
            break
        
        size_offset = start_tiff + 4
        size_tiff = int.from_bytes(data[size_offset:size_offset+4], byteorder='little')
        results.append(('TIFF', start_tiff, size_tiff))
        offset = start_tiff + size_tiff + 8

    # Check for MP3 files
    mp3_header = b'\xff\xe2'
    offset = 0
    while True:
        start_mp3 = data.find(mp3_header, offset)
        if start_mp3 == -1:
            break

        size_offset = start_mp3 + 4
        size = int.from_bytes(data[size_offset:size_offset+4], byteorder='big')
        results.append(('MP3', start_mp3, size))
        offset = start_mp3 + size + 4

    # Check for WAV files
    wav_header = b'RIFF'
    offset = 0
    while True:
        start_wav = data.find(wav_header, offset)
        if start_wav == -1:
            break
        
        size_offset = start_wav + 4
        size = int.from_bytes(data[size_offset:size_offset+4], byteorder='little') + 8
        results.append(('WAV', start_wav, size))
        offset = start_wav + size

    # Check for MP4 files
    mp4_header = b'\x00\x00\x00\x18\x66\x74\x79\x70' # MP4 signature
    offset = 0
    while True:
        start_mp4 = data.find(mp4_header, offset)
        if start_mp4 == -1:
            break
        
        size_offset = start_mp4 + 4
        size = int.from_bytes(data[size_offset:size_offset+4], byteorder='big')
        results.append(('MP4', start_mp4, size))
        offset = start_mp4 + size

    # Check for AVI files
    avi_header = b'RIFF'
    offset = 0
    while True:
        start_avi = data.find(avi_header, offset)
        if start_avi == -1:
            break
        
        size_offset = start_avi + 4
        size = int.from_bytes(data[size_offset:size_offset+4], byteorder='little') + 8
        results.append(('AVI', start_avi, size))
        offset = start_avi + size

    return results
def extract_lsb(image_path):
    # Open image and get pixel data
    im = Image.open(image_path)
    pixels = im.load()
    width, height = im.size

    # Extract LSBs from each color channel
    message_bits = ""
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y][0], pixels[x, y][1], pixels[x, y][2]
            message_bits += bin(r)[-1] + bin(g)[-1] + bin(b)[-1]

    # Convert message to bytes
    message_bytes = bytearray()
    for i in range(0, len(message_bits), 8):
        byte = message_bits[i:i+8]
        message_bytes.append(int(byte, 2))

    return message_bytes
def extract_embedded_files(file_path, embedded_files, file_num):
    with open(file_path, 'rb') as f:
        data = f.read()
        file_type, start_offset, size = embedded_files[0], embedded_files[1], embedded_files[2]
        # if file_type == 'ZIP':
        #     size = 100
        file_data = data[start_offset:start_offset+size]
        file_name = "./possibly_extracted/File{}_{}_embedded_file.{}".format(file_num, file_type.lower(),file_type.lower())
        with open(file_name, 'wb') as f:
            f.write(file_data)

        return file_name, size
#TODO

def modify_ihdr(input_path, output_path, new_width, new_height):
    with open(input_path, 'rb') as f:
        # 读取PNG文件头部信息
        header_data = f.read(8)

        # 解析IHDR块
        ihdr_data = f.read(25)

        # 修改宽度和高度
        new_ihdr_data = (
            ihdr_data[:4] + 
            bytes.fromhex('49484452') +
            struct.pack('>I', new_width) +
            struct.pack('>I', new_height) +
            ihdr_data[16:]
        )

        # 写入新的PNG文件
        with open(output_path, 'wb') as output_file:
            # 写入PNG文件头部信息
            output_file.write(header_data)

            # 写入新的IHDR块
            output_file.write(new_ihdr_data)
            # 写入剩余数据
            chunk_type = f.read(4)
            while chunk_type:
                chunk_length = struct.unpack('>I', f.read(4))[0]
                chunk_data = f.read(chunk_length + 4)
                output_file.write(chunk_type)
                output_file.write(struct.pack('>I', chunk_length))
                output_file.write(chunk_data)
                chunk_type = f.read(4)
def CBC_boom(filename):
    with open(filename, 'rb') as f:
        all_b = f.read()
        crc32key = int(all_b[29:33].hex(),16)
        ihdr = all_b[12:29]
        data = bytearray(ihdr)
        n = 4095
        for w in range(n): 
            width = bytearray(struct.pack('>i', w))
            for h in range(n):
                height = bytearray(struct.pack('>i', h))
                for x in range(4):
                    data[x+4] = width[x]
                    data[x+8] = height[x]
                crc32result = zlib.crc32(data)
                if crc32result == crc32key:
                    return int.from_bytes(height, byteorder='big'), int.from_bytes(width, byteorder='big')
    return False, False
def detect_image_format(image_path):
    with open(image_path, 'rb') as f:
        file_header = f.read(8)
        
        if file_header.startswith(b'\xff\xd8'):
            return "JPEG"
        elif file_header.startswith(b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'):
            return "PNG"
        elif file_header.startswith(b'\x47\x49\x46\x38\x39\x61') or file_header.startswith(b'\x47\x49\x46\x38\x37\x61'):
            return "GIF"
        elif file_header.startswith(b'BM'):
            return "BMP"
        elif file_header.startswith(b'II*') or file_header.startswith(b'MM*'):
            return "TIFF"
        elif file_header.startswith(b'RIFF'):
            return "WebP"
        elif file_header.startswith(b'\x00\x00\x01\x00'):
            return "ICO"
        elif file_header.startswith(b'8BPS'):
            return "PSD"
        elif file_header.startswith(b'<svg'):
            return "SVG"
        else:
            return False
