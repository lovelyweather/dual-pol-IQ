import sys
sys.path.append("../../")
import numpy as np
import struct
import bz2
import gzip

def _structure_size(structure):
    """
    计算structure的字节大小
    eg: struct.calcsize('<iHHb');
    out: 9. int(4)+unsigned short(2*2)+signed char(1) = 9
    """
    return struct.calcsize('<' + ''.join([i[1] for i in structure]))

def _unpack_from_buf(buf, pos, structure):
    '''unpack a structure from buf, the starting position is pos'''
    size = _structure_size(structure)
    return _unpack_structure(buf[pos:pos + size], structure), size

def _unpack_structure(string, structure):
    '''unpack a structure from a string'''
    fmt = '<' + ''.join([i[1] for i in structure])
    lst = struct.unpack(fmt, string)
    #struct.unpack(format, buffer): 根据格式字符串 format 从缓冲区 buffer 解包（假定是由 pack(format, ...) 打包）。 
    return dict(zip([i[0] for i in structure], lst))

def IQ_unpack(data):
    data_=np.empty_like(data,dtype='float32')
    
    for i,v in enumerate(data):
        E=v>>12 #按位右移 >> 第11位符号位在最前面
        S=(v&0x0FFF)>>11
        M=v&0x07FF
        SM=v&0x0FFF
        
        if E!=0:
            M1=np.array(M,dtype='int32')
            if S:
                M1|=0x800
            else:
                M1|=0xfffff000
                
            E=np.array(E,dtype='float32')
            data_[i]=M1*2**(E-25)
        else:
            data_[i]=SM*2**(-24)
    
    return data_[0::2],data_[1::2]

def _prepare_for_read(filename):
    """
    解压
    Return a file like object read for reading.
    Open a file for reading in binary mode with transparent decompression of
    Gzip and BZip2 files.  The resulting file-like object should be closed.
    Parameters
    ----------
    filename : str or file-like object
        Filename or file-like object which will be opened.  File-like objects
        will not be examined for compressed data.
    Returns
    -------
    file_like : file-like object
        File like object from which data can be read.
    """
    # if a file-like object was provided, return
    if hasattr(filename, 'read'):  # file-like object
        return filename
    # look for compressed data by examining the first few bytes
    fh = open(filename, 'rb')
    magic = fh.read(1)
    fh.close()
    if magic.startswith(b'\x1f\x8b'):
        f = gzip.GzipFile(filename, 'rb')
    elif magic.startswith(b'BZh'):
        f = bz2.BZ2File(filename, 'rb')
    else:
        f = open(filename, 'rb') #r:read; b: binary
    return f