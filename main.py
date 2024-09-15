# -*- coding:utf-8 -*-
# @FileName  :main.py
# @Time      :2024/01/08 17:55:42
# @Author    :LamentXU
import time, binascii, utils, decoder

import os.path as op
from os import mkdir, chdir
from shutil import rmtree, copyfile
from rich import print
from rich.console import Console
# from rich.style import Style
from rich.table import Table
from json import load
from PIL import Image
from PIL.ExifTags import TAGS
VERSION = 'v0.1'
PATH = op.dirname(op.abspath(__file__))
console = Console()
def is_image(file_path):
    if not op.exists(file_path):
        return False
    _, extension = op.splitext(file_path)
    supported_extensions = ['.jpg', '.jpeg', '.png']
    if extension.lower() not in supported_extensions:
        return False
    return True

def get_image_content():
    with open(MAIN_image, 'rb') as f:
        image_content = f.read()

    return image_content
def get_image_info(MAIN_image, image_content):
    # 打开图片
    def get_image():
        global MAIN_image, image_content
        try:
            image = Image.open(MAIN_image)
            return image, MAIN_image
        except:
            status.stop()
            _print('Something wrong with {}, checking it'.format(MAIN_image), print_type='warning')
            status.update('checking image......')
            status.start()
            image_type, need_fix = utils.detect_image_format(MAIN_image)
            status.stop()
            if need_fix:
                _print('Header error, try to fix the header')
                status.update('fixing the header......')
                status.start()
                fixed = utils.fix_header(image_content, image_type)
                status.stop()
                with open('fixed_header_{}'.format(op.basename(MAIN_image)), 'wb') as f:
                    f.write(fixed)
                _print('Header fixed, saved in ./{}/fixed_header_{}, try to open the image again'.format(dir_name, op.basename(MAIN_image)), print_type='critical')
                image = Image.open('./fixed_header_{}'.format(op.basename(MAIN_image)))
                return image, './fixed_header_{}'.format(op.basename(MAIN_image))
            elif not image_type:
                _print('Unsupported image type', print_type='error')
                exit()
            _print('Image type: {}'.format(image_type))
            if image_type == 'PNG':
                status.update('Doing CRC32 brute force......')
                status.start()
                h, w = utils.CBC_boom(MAIN_image)
                if w and h:
                    status.stop()
                    _print('IHDR DETECTED, real width : {}, height : {}'.format(str(w), str(h)))
                    utils.modify_ihdr(MAIN_image, 'output.png', w, h)
                    _print('IHDR MODIFYIED, new image location : ./{}/output.png'.format(dir_name), print_type='critical')
                    _print('Check the new image, if still no flag, continue the script with the new image')
                is_continue()
                MAIN_image = 'output.png'
                with open(MAIN_image, 'rb') as f:
                    image_content = f.read() 
                image = Image.open(MAIN_image)
                return image, MAIN_image
    image, MAIN_image = get_image()
    metadata = {}
    metadata['format'] = image.format
    metadata['mode'] = image.mode
    metadata['size'] = '{}*{}'.format(image.size[0], image.size[1])
    exif_data = image.getexif()
    for tag_id, value in exif_data.items():
        tag_name = TAGS.get(tag_id, tag_id)
        if type(value) == int:
            value = str(value)
        elif type(value) == bytes:
            value = value.decode('utf-16') if value is not None else None
        
        metadata[tag_name] = value
    try:
        metadata.pop(59932)
    except:
        pass
    return metadata, image_content, image, MAIN_image
def is_continue():
    console.print("[b blue][i][PRESS CTRL+C TO CONTINUE IF YOU WANT][/i][/b blue]", end='\r')
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        _print('Now continue the script')
def _print(string, print_type='normal'):
    if print_type == 'normal':
        console.log("[b blue]INFO        {}.[/b blue]".format(string))
    elif print_type == 'flag':
        console.bell()
        console.log("[b green]FLAG        POSSIBLE FLAG [u][i]{}[/i][/u] FROM [i]{}[/i].[/b green]".format(string[0], string[1]), style='bold')
        is_continue()


    elif print_type == 'warning' or print_type == 'warn':
        console.log(
            "[b yellow]WARNING     {}.[/b yellow]".format(string))
    elif print_type == 'error':
        console.log("[b red]ERROR       {}.[/b red]".format(string))
    elif print_type == 'critical':
        console.log("[b cyan][reverse]CRITICAL[/]    {}.[/b cyan]".format(string), style='bold')
    else:
        raise NameError('Unknown print type {}.'.format(print_type))

def check_for_flag(string):
    try:
        if type(string) == bytes:
            string = string.decode('utf-8', errors='ignore')
        for flag_format in FLAG:
            start_index = string.find(flag_format)
            if start_index == -1:
                continue
            else:
                end_index = string.find("}", start_index)
                if end_index == -1 and '{' in flag_format:
                    _print("Flag found, but somehow there is no '}' in flag, printout the whole string", print_type='warning')
                    flag_string = string[start_index:]
                    if len(flag_string) >= 50:
                        flag_string = flag_string[:50] + '...'
                    _print("Flag: {}".format(flag_string))
                    is_continue()
                    status.start()
                    return False
                elif '{' not in flag_format:
                    _print('Flag found, not no "{}" in flag format, print out all the string where flag was found')
                    flag_value = string
                else:
                    flag_value = string[start_index:end_index+1]
                if flag_format == 'ctf{' or flag_format == 'CTF{':
                    _print('It seems like you are using the default flag format, please set your own flag format in the file(ex: "EICTF{", "0CTF{")', print_type='warning')
                    _print('The flag format might be XXCTF{ (ex: EICTF{) not CTF{, remeber to set the correct flag format', print_type='warning')
                    _print('In case of using the default flag format, you can choose to print out the whole string where flag was found')
                    _ = input('Do you want to print out the whole string where flag was found?(y/n): ')
                    if _ == 'Y' or _ == 'y' or _ == 'yes' or _ == 'YES' or not _:
                        _print("Flag: {}".format(string))
                return flag_value
    except Exception as e:
        return False
    return False
menu = rf'''                                               
 .    . ..          ...         ....  .. .     .            ...     
 .                           .@@@@@@@@@@@@@$. .                     
 .    . ..          ...          . .     .-@@@@@#..        . ;      
 .    . ..          ...        - #@@@@@@@@@@@@@@@         .o~^      
 .  .......     .. .....   ..*@@@@@@#@        ....     ..nooo ..    
 .  ....;*....  .. ...... .-88.   .  .      ......  .. oooooo...    
 .  ....**;*;;**;*.....  #@@@@@@@-..        ...... . ~ooooooo...    
 .    . ^*;*****;;*;;;;*~* ...    ..          ..   oooo*o~oon..     
 .      .;**********;;;;;;******;*.. . .      ..+~oon#@@@&oo^       
 .       ;********;;*--+^;;**;**;;;*****^*....~ooooo@#@@@aoo        
 .      .;*****;*@@@@@@@@@@@@+*;**;;*********ooooo^#@~~@@oo~        
 .       ;*****;@@@@@@@@;n#@@@@@+;**********;oooo~@@oov@zooo        
 .      .;;*****@@@@@@@;****#@@@@@-;*********~ooo@@@oo@@ooon        
 .       ;;*****;**;;!@*****;@@@@@@!********;oooo@@~o@@oooo+        
 .       ;;*********;;;;*;**-@@@@@@#********;ooo*ooo@@;oooo.        
 .       ^*************^i@@@@@@@@@@u*********oooooo^@@ooooo         
 .        **********;;*@@@@@@@@@@v*;*********oooooo@@@oooo~.        
 .      . ************^@@@@@@6;*;;*********;;oooooo@!ooooon         
 .    . ..******;;*;;;;@@@@@@;*;;;;;*******;oooooooooooooo. ...     
 .    ....;*****;;*;;;*;;^@#@;;;;;;;*******;ooooooon@;oov   ...     
 .  ......**;;**;;*;;;*;***;***;;;;;;;;*;;;;oooooo;@@oo-  ......    
 .  ......;*;;**;;*;;;*8$@@@***;;;;;;;;*;;;;oooooou&o~ .........    
 .    . ....-*;**;*;;;;@@@@@@;*;;;;;*******;ooooooo~..      ...     
 .  .......   ..  ^***;;^#@@#**;;;;;;;;*;;**oooooo-       ......    
 .                      ;*;****************;ooooo.                  
 .  .......     .. .....  . ..;;;;;;;;;*;;*;ooo           ......    
 .                               . ^;*;;****oz                      
 .                                       **~          



███╗   ███╗██╗██████╗  ██████╗   ██████╗  ██████╗ ██╗  ██╗
████╗ ████║██║╚════██╗██╔════╝   ██╔══██╗██╔═████╗╚██╗██╔╝
██╔████╔██║██║ █████╔╝██║        ██████╔╝██║██╔██║ ╚███╔╝ 
██║╚██╔╝██║██║ ╚═══██╗██║        ██╔══██╗████╔╝██║ ██╔██╗ 
██║ ╚═╝ ██║██║██████╔╝╚██████╗   ██████╔╝╚██████╔╝██╔╝ ██╗
╚═╝     ╚═╝╚═╝╚═════╝  ╚═════╝   ╚═════╝  ╚═════╝ ╚═╝  ╚═╝
        
----------------------[AUTHOR] LamentXU----------------------
------------------------[Version] {VERSION}------------------------

/flag: I like cats (*/ω＼*), meow meow meow.
'''
if __name__ == '__main__':
    try:
        try:
            with open('Flags.json') as f:
                FLAG = load(f)['FLAG']
        except Exception as e:
            _print('Fail to load Flags.json, print out the error : {}'.format(e), print_type='error')
            _print('You can set your own flag dict or download it from https://github.com/LamentXU123/Mi3cB0x/blob/main/Flags.json', print_type='warning')
            _ = console.input('Download https://github.com/LamentXU123/Mi3cB0x/blob/main/Flags.json to fix the problem?(y/n): >>> ')
            if _ == 'Y' or _ == 'y' or _ == 'yes' or _ == 'YES' or not _:
                import urllib.request
                try:
                    url = "https://raw.githubusercontent.com/LamentXU123/Mi3cB0x/master/Flags.json" 
                    save_path = op.join(PATH, 'Flags.json')  
                    urllib.request.urlretrieve(url, save_path)
                except:
                    console.print_exception()
                    _print('Download failed, please check your network', print_type='warning')
                    quit()
            else:
                quit()
        print(f'[b cyan]{menu}[/b cyan]')
        if FLAG == ['flag{', 'key{', 'ctf{', 'CTF{', 'FLAG{', 'ctf{', 'FLAG-{', 'FLAG_', 'CTF-{', 'CTF_', 'KEY{', 'KEY-{', 'KEY_', 'crypto{', 'pwn{', 'web{', 'rev{', 'misc{', 'stego{', 'forensics{', 'reversing{', 'exploitation{', 'network{', 'coding{', 'hacking{']:
            _print('Flags.json is the default flag format list, please set your own flag format in the file(ex: "EICTF{", "0CTF{")', print_type='warning')
        global status, MAIN_image
        MAIN_image = console.input('Please input the image location: >>> ')
        if not is_image(MAIN_image):
            _print('Image does not exist or not have a supported extensions', print_type='error')
            quit()
        else:
            dir_name = op.basename(MAIN_image)+'_extracted_'+str(int(time.time()))
            if op.exists(dir_name):
                _print('folder {}'.format(dir_name) + 'already exists', print_type='error')
                _ = console.input('Do you want to overwrite it?(y/n): >>> ')
                if _ == 'Y' or _ == 'y' or _ == 'yes' or _ == 'YES' or not _:
                    rmtree(dir_name)
                else:
                    quit()
            mkdir(dir_name)
            copyfile(MAIN_image, op.join(dir_name, op.basename(MAIN_image)))
            chdir(dir_name)
            with console.status('Reading image') as status:
                image_content = get_image_content()
                status.update('Checking the image info......')
                image_info, image_content, img_in_PIL, MAIN_image = get_image_info(MAIN_image, image_content)
                table = Table(show_header=True, header_style="bold magenta", title='image info')
                table.add_column("key", style="dim")
                table.add_column("value")
                output = []
                for key, value in image_info.items():
                    table.add_row(key, value)
                status.stop()
                console.print(table)
                for key, value in image_info.items():
                    flag_found = False
                    is_flag = check_for_flag(value)
                    if is_flag:
                        flag_found = True
                        _print([key, is_flag], print_type='flag')
                if not flag_found:
                    _print('No flag found in image info')
                status.start()
                status.update('Checking if the image is a QR code......')
                res = utils.decode_QRcode(img_in_PIL)
                status.stop()
                if res:
                    flag_value= check_for_flag(res)
                    if flag_value:
                        _print([flag_value, 'QR code'], print_type='flag')
                    else:
                        _print('QR code detected, but no flag, QR code message: {}'.format(res), print_type='warning')
                else:
                    _print('No QR code detected')
                status.start()
                status.update('Reading image hex, converting it into ascii......')
                hex_str = binascii.hexlify(image_content).decode('utf-8')
                ascii_str = ''.join(chr(byte) if 31 < byte < 127 else '.' for byte in image_content)
                flag_value = check_for_flag(ascii_str)
                status.stop()
                if flag_value:
                    _print([flag_value, 'Image hex -> ascii string'], print_type='flag')
                else:
                    _print('Image hex read, converted it into chars by ascii, no flag found')
                status.update('Checking lsb stegano......') 
                lsb_ste = utils.extract_lsb(MAIN_image)
                _print('LSB bytes saved in file: /{}/lsb_bytes'.format(dir_name), print_type='critical')
                with open('lsb_bytes', 'wb') as f:
                    f.write(lsb_ste)
                flag = check_for_flag(lsb_ste.decode('utf-8', errors='ignore'))
                if flag:
                    _print([flag, 'LSB Stegano'], print_type='flag')
                else:    
                    _print('LSB bytes extracted, but no flag found')
                status.update('Finding possible embedded files......')
                status.start()
                mkdir('possibly_extracted')
                result = utils.find_embedded_files(MAIN_image)
                status.stop()
                table = Table(show_header=True, header_style="bold magenta", title='embedded file info')
                table.add_column('File')
                table.add_column('File type')
                table.add_column('Start offset')
                table.add_column('Size')
                i = 0
                for res in result:
                    table.add_row('./{}/possibly_extracted/File'.format(dir_name)+str(i), res[0], str(res[1])+'B', str(res[2])+'B')
                    i += 1
                console.print(table)
                if len(result) > 1:
                    _print('possible embedded file(s) found, print out the result')
                    status.update('Extracting file......')
                    status.start()
                    i = 0
                    for res in result:
                        filename, size = utils.extract_embedded_files(MAIN_image, res, i)
                        _print("Extracted {} ({} bytes)".format(filename, size), print_type='critical')
                        i += 1
                else:
                    _print('No embedded file found')
    except SystemExit:
        pass
    except:
        console.print_exception()
    else:
        _print('Finished, please check the output files in ./{} folder'.format(dir_name))
    finally:
        chdir(PATH)