class Flag_Decoder():
    def __init__(self, flag_list) -> None:
        self.flag_list = flag_list
        self.encode_method_charset = {
            'base64': 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/',
            'hex': '0123456789ABCDEFabcdef',
            'ascii': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?',
            'url': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?',
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
            'base128': None
        }
    #TODO
