import re
class Flag_Decoder():
    def __init__(self, flag_list, work_dir) -> None:
        self.flag_list = flag_list
        self.work_dir = work_dir
        self.encode_method_charset = {
            'base64': 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/',
            'hex': '0123456789ABCDEFabcdef',
            'ascii': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?',            
            'url': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789%',
            'decimal': '0123456789',
            'octal': '01234567',
            'binary': '01',
            'base16': '0123456789ABCDEF',
            'base32': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
            'base58': '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz',
            'base85': '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~',
            'base62': 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789',
            'base91': 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!"#$%&()*+,./:;<=>?@[]^_`{|}~',
            'base92': 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!"#$%&()*+,./:~;<=>?@[]^_`{|}-',
        }
        self.format_dict = {
        'JPEG (jpg)': 'FFD8FF',
        'PNG (png)': '89504E47',
        'GIF (gif)': '47494638',
        'ZIP Archive (zip)': '504B0304',
        'TIFF (tif)': '49492A00',
        'Windows Bitmap (bmp)': '424D',
        'CAD (dwg)': '41433130',
        'Adobe Photoshop (psd)': '38425053',
        'Rich Text Format (rtf)': '7B5C727466',
        'XML (xml)': '3C3F786D6C',
        'HTML (html)': '68746D6C3E',
        'Email (eml)': '44656C69766572792D646174653A',
        'Outlook Express (dbx)': 'CFAD12FEC5FD746F',
        'Outlook (pst)': '2142444E',
        'MS Word/Excel (xls/doc)': 'D0CF11E0',
        'MS Access (mdb)': '5374616E64617264204A',
        'WordPerfect (wpd)': 'FF575043',
        'Adobe Acrobat (pdf)': '255044462D312E',
        'Quicken (qdf)': 'AC9EBD8F',
        'Windows Password (pwl)': 'E3828596',
        'RAR Archive (rar)': '52617221',
        'Wave (wav)': '57415645',
        'AVI (avi)': '41564920',
        'Real Audio (ram)': '2E7261FD',
        'Real Media (rm)': '2E524D46',
        'MPEG (mpg)': '000001BA',
        'MPEG (mpg)': '000001B3',
        'Quicktime (mov)': '6D6F6F76',
        'Windows Media (asf)': '3026B2758E66CF11',
        'MIDI (mid)': '4D546864'
        }
    def solve_flag_by_bytes(self, flag, data_from):
        if type(flag) == str:
            flag = flag.encode('utf-8')
        flag_hex = flag.hex().upper()
        for i in self.format_dict:
            if flag_hex.startswith(self.format_dict[i]):
                matches = re.findall(r'\((.*?)\)', i)[0]
                with open('./{}_extracted.{}'.format(data_from, matches[0]), 'wb') as f:
                    f.write(flag)
                return '{} File found in {} with header {}, saved in /{}/{}_extracted.{}'.format(i,matches ,self.format_dict[i], self.work_dir,data_from, matches)
        return False      
    