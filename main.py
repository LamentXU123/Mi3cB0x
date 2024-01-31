# -*- coding:utf-8 -*-
# @FileName  :main.py
# @Time      :2024/01/08 17:55:42
# @Author    :LamentXU
import time, os, binascii, tools, stegano

from sys import exit
from rich import print
from rich.console import Console
# from rich.style import Style
from rich.table import Table
from json import load
from PIL import Image
from PIL.ExifTags import TAGS
from os.path import dirname, abspath
VERSION = 'v0.1'
console = Console()
PATH = dirname(abspath(__file__))
def is_image(file_path):
    if not os.path.exists(file_path):
        return False
    _, extension = os.path.splitext(file_path)
    supported_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    if extension.lower() not in supported_extensions:
        return False
    return True

def get_image_content():
    with open(MAIN_image, 'rb') as f:
        image_content = f.read()

    return image_content
def get_image_info(MAIN_image, image_content):
    # 打开图片
    try:
        image = Image.open(MAIN_image)
    except:
        status.stop()
        _print('Something wrong with {}, checking it'.format(MAIN_image), print_type='warning')
        status.update('checking image......')
        status.start()
        image_type = tools.detect_image_format(MAIN_image)
        status.stop()
        if not image_type:
            print('Header error, try to fix the header', print_type='warning')
            status.update('fixing the header......')
            status.start()
            #TODO
        _print('Image type : {}'.format(image_type))

        if image_type == 'PNG':
            status.update('Doing CRC32 brute force......')
            status.start()
            h, w = tools.CBC_boom(MAIN_image)
            if w and h:
                status.stop()
                _print('IHDR DETECTED, real width : {}, height : {}'.format(str(w), str(h)))
                tools.modify_ihdr(MAIN_image, 'output.png', w, h)
                _print('IHDR MODIFYIED, new image location : {}\\output.png'.format(PATH), print_type='good')
                _print('Look the new image, if still no flag, continue the script with the new image')
            is_continue()
            MAIN_image = 'output.png'
            with open(MAIN_image, 'rb') as f:
                image_content = f.read() 
            image = Image.open(MAIN_image)
    metadata = {}
    # 获取图片属性
    metadata['format'] = image.format
    metadata['mode'] = image.mode
    metadata['size'] = '{}*{}'.format(image.size[0], image.size[1])
    # 获取图像的所有 EXIF 信息
    exif_data = image.getexif()
    # 遍历 EXIF 数据字典
    for tag_id, value in exif_data.items():
        # 获取标签名称
        tag_name = TAGS.get(tag_id, tag_id)
        
        # 将标签和值存储在字典中
        if type(value) == int:
            value = str(value)
        elif type(value) == bytes:
            value = value.decode('utf-16') if value is not None else None
        
        metadata[tag_name] = value
    try:
        metadata.pop(59932)
    except:
        pass
    return metadata, image_content, image
def is_continue():
    console.print("[b blue][i][PRESS CTRL+C TO CONTINUE IF YOU WANT][/i][/b blue]", end='\r')
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        _print('Now continue the script')
def _print(string, print_type='normal'):
    if print_type == 'normal':
        console.log("[b cyan][b blod]INFO[/b blod]        {}[/b cyan]".format(string))
    elif print_type == 'flag':
        console.bell()
        console.log("[b green][b blod]FLAG        POSSIBLE FLAG [u][i]{}[/i][/u] FROM [i]{}[/i][/b blod][/b green]".format(string[0], string[1]))
        is_continue()


    elif print_type == 'warning' or print_type == 'warn':
        console.log(
            "[b yellow][b blod]WARNING[/b blod]     {}[/b yellow]".format(string))
    elif print_type == 'error':
        console.log("[b red][b blod]ERROR[/b blod]       {}[/b red]".format(string))
    elif print_type == 'good':
        console.log("[b green][b blod]GOOD        {}[/b green][/b blod]".format(string))
    else:
        raise NameError('Unknown print type {}'.format(print_type))

def check_for_flag(string):
    
    try:
        for flag_format in FLAG:
            start_index = string.find(flag_format)
            if start_index == -1:
                continue
            else:
                end_index = string.find("}", start_index)
                if end_index == -1:
                    status.stop()
                    _print("Flag found, but somehow there is no '}' in flag, printout the whole string", print_type='warning')
                    flag_string = string[start_index:]
                    if len(flag_string) >= 50:
                        flag_string = flag_string[:50] + '...'
                    _print("Flag: {}".format(flag_string))
                    is_continue()
                    status.start()
                    return False
                else:
                    # 输出 flag 值
                    flag_value = string[start_index:end_index+1]
                    return flag_value
    except:
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
        
----------------------[AUTHOR] Lament XU----------------------
------------------------[Version] {VERSION}------------------------

'''
if __name__ == '__main__':
    try:
        with open('Flags.json') as f:
            FLAG = load(f)['FLAG']
    except Exception as e:
        _print('Fail to load Flags.json, set your own flag dict or download it from github') #TODO
    try:
        print(f'[b cyan]{menu}[/b cyan]')
        global status, MAIN_image
        MAIN_image = console.input('Please input the image location: >>> ')
        if not is_image(MAIN_image):
            _print('Image does not exist or not have a supported extensions', print_type='error')
            exit()
        else:
            with console.status('Reading image') as status:
                image_content = get_image_content()
                status.update('Checking the image info......')
                image_info, image_content, img_in_PIL = get_image_info(MAIN_image, image_content)
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
                status.update('Reading image hex, converting it into ascii......')
                hex_str = binascii.hexlify(image_content).decode('utf-8')
                ascii_str = ''.join(chr(byte) if 31 < byte < 127 else '.' for byte in image_content)
                flag_value = check_for_flag(ascii_str)
                status.stop()
                if flag_value:
                    _print([flag_value, 'Image hex -> ascii string'], print_type='flag')
                else:
                    _print('Image hex read, converted it into ascii, no flag found')
                status.update('Checking lsb stegano......') 
                try:
                    lsb_ste = stegano.lsb.reveal(img_in_PIL)
                    if lsb_ste:
                        _print('LSB STEGANO FOUND, message({})'.format(lsb_ste))
                        flag = check_for_flag(lsb_ste)
                        if flag:
                            _print([flag, 'LSB Stegano'], print_type='flag')
                        else:
                            _print('LSB found, but no flag, please check it')
                            is_continue()
                    else:
                        _print('No lsb setgano found')
                except:
                    _print('No lsb setgano found')
                status.update('Now finding embedded files......')
                status.start()
                result = tools.find_embedded_files(MAIN_image)
                status.stop()
                table = Table(show_header=True, header_style="bold magenta", title='embedded file info')
                table.add_column('File')
                table.add_column('File type')
                table.add_column('Start offset')
                table.add_column('Size')
                i = 0
                for res in result:
                    table.add_row('File'+str(i), res[0], str(res[1])+'B', str(res[2])+'B')
                    i += 1
                console.print(table)
                if len(result) > 1:
                    _print('EMBEDDED FILE FOUND, print out the result', 'good')
                    status.update('Extracting file......')
                    status.start()
                    i = 0
                    for res in result:
                        filename, size = tools.extract_embedded_files(MAIN_image, res, i)
                        _print("Extracted {} ({} bytes)".format(filename, size))
                        i += 1
                else:
                    _print('No embedded file found')
    except:
        console.print_exception()
    finally:
        _print('Exit')