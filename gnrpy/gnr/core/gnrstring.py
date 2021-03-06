# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# module gnrstring : gnr string implementation
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import re
import cPickle
import zipfile
import StringIO
import logging
import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)

try:
    from string import Template
    
    class BagTemplate(Template):
        idpattern = '[_a-z\@][_a-z0-9\.\@]*'
        
    class NoneIsBlankMapWrapper(object):
        
        def __init__(self,data):
                self.data=data
                
        def __getitem__(self,k):
            value= self.data[k] 
            if value is None:
                value= ''
            return value
            
except:
    pass

try:
    try:
        import json
    except:
        import simplejson as json
    class JsonEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime.date):
                return obj.strftime('%m/%d/%Y')
            if isinstance(obj, Decimal):
                return str(obj)
            return json.JSONEncoder.default(self, obj)
            
    class JsonEncoderJS(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime.date):
                return "new Date(%i, %i, %i)" % (obj.year, obj.month - 1, obj.day)
            return json.JSONEncoder.default(self, obj)
except:
    pass

from gnr.core.gnrlocale import localize, parselocal

REGEX_WRDSPLIT = re.compile(r'\W+')
BASE_ENCODE = {'/2': '01',
               '/8': '012345678',
               '/16': '0123456789ABCDEF',
               '/36': '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
}

def getUntil(myString, chunk, returnOriginal=False):
    """Search in a string a chunk: if it is present, return all the characters before this chunk.
    If not, return an empty string (or the original one, if returnOriginal is ``True``).
    
    :param myString: the string to be checked
    :param chunk: substring that bounds the result string
    :param returnOriginal: if ``True``, return the entire string if the chunk is not present in the string.
                           Default value is ``False``.
    :returns: a string until a given chunk
    
    >>> getUntil('teststring', 'st')
    'te'
    >>> getUntil('teststring', 'te')
    ''
    >>> getUntil('teststring', 'co')
    ''
    >>> getUntil('teststring', 'co', returnOriginal=True)
    'teststring'
    """
    p = myString.find(chunk)
    if p > -1:
        return myString[0:p]
    else:
        if returnOriginal:
            return myString
        else:
            return ''
            
def getUntilLast(myString, chunk):
    """Return a string until last occurence of a given chunk
    
    :param myString: the string to be checked
    :param chunk: substring that bounds the result string
    :returns: a string until last occurence of a given chunk
    
    >>> getUntilLast('teststring', 'st')
    'test'
    >>> getUntilLast('teststring', 'te')
    ''
    >>> getUntilLast('teststring', 'co')
    ''
    """
    p = myString.rfind(chunk)
    if p > -1:
        return myString[0:p]
    else:
        return ''
        
def getFrom(myString, chunk):
    """Return a string after a given chunk
    
    :param myString: the string to be checked
    :param chunk: substring that bounds the result string
    :returns: a string after a given chunk
    
    >>> getFrom('teststring', 'st')
    'string'
    >>> getFrom('teststring', 'te')
    'ststring'
    >>> getFrom('teststring', 'co')
    ''
    """
    p = myString.find(chunk)
    if p > -1:
        return myString[p + len(chunk):]
    else:
        return ''
        
def getFromLast(myString, chunk):
    """Return a string after the last occurence of a given chunk.
    
    :param myString: the string to be checked
    :param chunk: substring that bounds the result string
    :returns: a string after the last occurence of a given chunk
    
    >>> getFromLast('teststring', 'st')
    'ring'
    >>> getFromLast('teststring', 'ng')
    ''
    >>> getFromLast('teststring', 'co')
    ''
    """
    p = myString.rfind(chunk)
    if p > -1:
        return myString[p + len(chunk):]
    else:
        return ''
            
def wordSplit(text):
    """Return a list that contains the words of the given text
        
    :param text: text to be splitted
    :returns: a list that contains the words of the given text
    
    >>> wordSplit('hello, my dear friend')
    ['hello', 'my', 'dear', 'friend']
    """
    return REGEX_WRDSPLIT.split(text)
    
def splitLast(myString, chunk):
    """Return a tuple of two strings, splitting the string at the last occurence of a given chunk.
    
    :param myString: string to be splitted
    :param chunk: substring that bounds the result string
    :returns: a tuple of two strings
    
    >>> splitLast('hello my dear friend', 'e')
    ('hello my dear fri', 'nd')
    """
    p = myString.rfind(chunk)
    if p > -1:
        return myString[0:p], myString[p + len(chunk):]
    else:
        return myString, ''
        
def getBetween(myString, startChunk, endChunk):
    """Return a string between two given chunks.
    
    :param myString: the string to be checked
    :param startChunk: substring that bounds the result string from left
    :param endChunk: substring that bounds the result string from right
    
    :returns: a string between two given chunks
    
    >>> getBetween('teststring', 'st','in')
    'str'
    >>> getBetween('teststring', 'st','te')
    ''
    >>> getBetween('teststring', 'te','te')
    ''
    """
    p1 = myString.find(startChunk)
    if p1 < 0:
        return ''
    else:
        p2 = myString.find(endChunk, p1 + len(startChunk))
        if p2 < 0:
            return ''
        else:
            return myString[p1 + len(startChunk):p2]
            
def like(s1, s2, wildcard='%'):
    """
    :param s1: first string
    :param s2: second string
    :wildcard: a special symbol that stands for one or more characters. Default value is ``%``
    
    >>> like('*dog*', 'adogert', '*')
    True
    >>> like('dog*', 'adogert', '*')
    False
    >>> like('*dog', '*adogert', '*')
    False
    """
    if s1.startswith('^'):
        s1 = s1[1:].upper()
        s2 = s2.upper()
    if s1 == wildcard or s1 == s2: return True
    elif not wildcard in s1: return False
    if s1.startswith(wildcard):
        if s1.endswith(wildcard): return bool(s1[1:-1] in s2)
        return bool(s2.endswith(s1[1:]))
    if s1.endswith(wildcard): return bool(s2.startswith(s1[:-1]))
    return False
    
def ilike(s1, s2, wildcard='%'):
    """Return the result of :meth:`like()` function ignoring upper-lowercase differencies
    
    :param s1: first string
    :param s2: second string
    :wildcard: a special symbol that stands for one or more characters. Default value is ``%``
    """
    return like(s1.upper(), s2.upper(), wildcard)
    
def filter(item, include=None, exclude=None, wildcard='%'):
    if include and isinstance(include, basestring):
        include = include.split(',')
    if exclude and isinstance(exclude, basestring):
        exclude = exclude.split(',')
    if exclude:
        for excl in exclude:
            if like(excl, item, wildcard):
                return False
    if include:
        for incl in include:
            if like(incl, item, wildcard):
                return True
        return False
    return True
    
def regexDelete(myString, pattern):
    """
    Returns a string obtained deleting from the given string any occurrency
    of the given pattern.
    
    :param myString: the string to be shortened
    :param pattern: pattern of chars that must be deleted from myString
    
    >>> regexDelete('When he turns the steering wheel', 'he')
    'Wn  turns t steering wel'
    """
    return re.sub(pattern, '', myString)
    
def templateReplace(myString, symbolDict=None, safeMode=False,noneIsBlank=True):
    """Allow to replace string's chunks.
    
    :param myString: template string
    :param symbolDict: dictionary that links symbol and values. Default value is ``None``.
    :param safeMode: flag that implies the use of :meth:`substitute()` and :meth:`or safe_substitute()` Python methods. Default value is ``False``.
    
    >>> templateReplace('$foo loves $bar but she loves $aux and not $foo', {'foo':'John','bar':'Sandra','aux':'Steve'})
    'John loves Sandra but she loves Steve and not John'"""
    
    if not '$' in myString or not symbolDict: return myString
    if hasattr(symbolDict, '_htraverse'):
        Tpl = BagTemplate
        if noneIsBlank:
            symbolDict=NoneIsBlankMapWrapper(symbolDict)
    else:
        Tpl = Template
    if safeMode:
        return Tpl(myString).safe_substitute(symbolDict)
    else:
        return Tpl(myString).substitute(symbolDict)
        
def asDict(myString, itemSep=',', argSep='=', symbols=None):
    """
    :param myString: a string that represent a list of key-value pairs.
    :param itemSep: the separator char between each key-value pair. Default value is ``,``
    :param argSep: the separator key and value. Default value is ``=``
    :param symbols: a dictionary that eventually contains value for templates in myString, Default value is ``False``
    
    >>> asDict('height=22, weight=73')
    {'weight': '73', 'height': '22'}
    
    >>> asDict('height=$myheight, weight=73', symbols={'myheight':55})
    {'weight': '73', 'height': '55'}
    """
    if not myString: return {}
    if myString.startswith('('): myString = myString[1:-1]
    result = {}
    itemList = split(myString, itemSep)
    for item in itemList:
        item = item.strip().strip(itemSep)
        key, value = split(item, argSep)
        
        key = key.encode()
        if value.startswith("'"): result[key] = value.strip("'")
        elif value.startswith('"'): result[key] = value.strip('"')
        if value.startswith('(')and value.endswith(')'): result[key] = value[1:-1]
        else:
            if '$' in value: value = templateReplace(value, symbols)
            result[key] = value
    return result
    
def stringDict(myDict, itemSep=',', argSep='='):
    """return a string that represents a list of list of key-value pairs taken from a dictionary.
    
    :param myDict: dictionary to be transformed in a string
    :param itemSep: the separator char between each key-value pair. Default value is ``,``
    :param argSep: the separator key and value. Default value is ``=``
    
    >>> stringDict({'height':22,'width':33})
     'width=33,height=22'
    """
    return itemSep.join([argSep.join((str(k), str(v))) for k, v in myDict.items()])
    
def updateString(source, s, sep=','):
    """Append a new element to a string that represents a set of elements separated by a separation char.
    
    :param source: initial string
    :param s: string to be added
    :param sep: separator string. Default value is ``,``
    
    >>> updateString('I drink cola', 'beer')
    'I drink cola,beer'
    
    >>> gs.updateString('I drink cola', 'beer', ' and ')
    'I drink cola and beer'
    """
    if not source: return s
    splitted = split(source, sep)
    if s in splitted: return source
    return sep.join(splitted + [s])
    
def updateStringList(s1, s2, sep=','):
    """add???
    
    :param s1: add???
    :param s2: add???
    :param sep: separator string. Default value is ``,``
    :returns: add???
    """
    #what??
    l1 = set(splitAndStrip(s1))
    l2 = set(splitAndStrip(s2))
    s = set()
    
def makeSet(*args, **kwargs):
    """add???
    """
    result = set()
    for myString in args:
        result.update(splitAndStrip(myString, sep=kwargs.get('sep', ',')))
    if not kwargs.get('keepEmpty', False):
        result.discard('')
    return result
    
def splitAndStrip(myString, sep=',', n=-1, fixed=0):
    """Split a string in a list of n+1 items, striping white spaces.
        
    :param myString: the string to be splitted
    :param sep: separation character. Default value is ``,``
    :param n: how many split operations must be done on myString. Default value is ``-1``
    :param fixed: use ``fixed`` if the resulting list must have a fixed length. Default value is ``0``
    
    >>> splitAndStrip('cola, beer, milk')
    ['cola', 'beer', 'milk']
    >>> splitAndStrip('cola, beer, milk', n=2)
    ['cola', 'beer, milk']
    """
    myString = myString.strip().strip(sep)
    r = myString.split(sep, n)
    result = [x.strip() for x in r]
    delta = abs(fixed) - len(result)
    if not fixed or delta == 0:
        return result
    if delta > 0:
        dlist = [''] * delta
        if fixed > 0:
            return result + dlist
        else:
            return dlist + result
    else:
        return result[0:abs(fixed)]
            
def countOf(myString, srcString):
    """add???
        
    :param myString: add???
    :param srcString: add???
    :returns: add???
    """
    return (len(myString) - len(myString.replace(srcString, ''))) / len(srcString)
    
def split(path, sep='.'):
    """Return a list splitting a path string at any occurrency of separation character.
    
    :param path: the path string to be splitted
    :param sep: separation character. Default value is ``.``
    
    >>> split('first.second.third')
    ['first', 'second', 'third']
    """
    
    if not path: return ['']
    extendedsep = sep[1:]
    sep = sep[0]
    result = []
    start = 0
    end = len(path)
    myre = re.compile("([^\%s\'\"\(\[\)\]]*)(?:(?P<enditem>\%s|$)|(\')|(\")|(\()|(\[)|(\))|(\]))" % (sep, sep))
    wch = []
    nextPos = start
    while start < end:
        startpos = start
        foundsep = False
        while not foundsep or wch:
            res = myre.match(path, nextPos)
            gr = res.groups()
            nextPos = res.end()
            if gr[1] == "": #End of string
                if wch: raise  ValueError("wrong level: missing :" + wch.pop())
                foundsep = True
                blockLen = res.end()
                
            elif not wch and gr[1] != None:
                foundsep = True
                blockLen = res.end() - 1
                if extendedsep and res.group('enditem') == sep:
                    if path[nextPos:].startswith(extendedsep):
                        nextPos = nextPos + len(extendedsep)
                    else:
                        foundsep = False
            else:
                char = gr[2] or gr[3] or gr[4] or gr[5] or gr[6] or gr[7]
                if char:
                    if char in """\'\"""": nextPos = path.index(char, nextPos) + 1
                    elif char == '(': wch.append(')')
                    elif char == '[': wch.append(']')
                    elif char in '])':
                        if char == wch[-1]: wch.pop()
                        else: raise ValueError("wrong level: missing :" + wch.pop())
                        
        result.append(path[startpos:blockLen])
        start = nextPos
    return result
    
def smartjoin(mylist, on):
    """Join the given list with the separator substring on and escape each occurrency of on within mylist
        
    :param mylist: the list to be joined
    :param on: separator substring
    
    >>> smartjoin(['Hello, dog', 'you', 'are', 'yellow'], ',')
    'Hello\\, dog,you,are,yellow'
    """
    escape = "\\" + on
    return on.join([x.replace(on, escape) for x in mylist])
    
def smartsplit(path, on):
    """Split the string ``path`` with the separator substring ``on`` ignoring the escaped separator chars
    
    :param path: the path to be splitted
    :param on: separator substring
    """
    
    escape = "\\" + on
    if escape in path:
        path = path.replace(escape, chr(1))
        pathList = path.split(on)
        pathList = [x.replace(chr(1), escape) for x in pathList]
    else:
        pathList = path.split(on)
    return pathList
    
def concat(s1, s2, sep='.'):
    """join two strings. If the first string is ``None``, return the second string.
        
    :param s1: the first string
    :param s2: the second string
    :param sep: separation character. Default value is ``.``
    :returns: the two strings joined
    """
    if s1:
        return '%s%s%s' % (s1, sep, s2)
    else:
        return s2
        
def dotEsc(txt):
    """Return a text with all dot char escaped
    
    :param txt: the text
    :returns: the text with all dot char escaped
    """
    return txt.replace('.', '\\.')
    
#encoding and conversion functions
    
def encode(number, base='/16', nChars=None):
    """Return a string that contains the given number in the specified base
       
       :param number: number to encode
       :param base: base of encoding. Default value is ``/16``
       :param nChar: number of characters of the result. Default value is ``None``
       :returns: encoded number as string
    """
    import math
    
    if base in BASE_ENCODE: base = BASE_ENCODE[base]
    b = len(base)
    result = []
    while (number >= 1):
        result.insert(0, base[int(math.fmod(number, b))])
        number = math.floor(number / b)
        
    if (len(result) > nChars): result = []
    elif (len(result) < nChars):
        for x in range(nChars - len(result)):
            result.insert(0, base[0])
    return ''.join(result)
    
def fromIsoDate(datestring):
    """add???
        
    :param datestring: add???
    :returns: add???
    """
    if datestring and datestring != '0000-00-00':
        return datetime.date(*[int(el) for el in wordSplit(datestring)])
        
def fromText(mystring, obj, locale=None):
    """add???
    
    :param mystring: add???
    :param obj: add???
    :param locale: add???. Default value is ``None``
    :returns: add???
    """
    #what?
    return parselocal(mystring, obj, locale=locale)
    
def toText(obj, locale=None, format=None, mask=None, encoding=None, currency=None):
    """Return a unicode string representing an object of any class.
       
       If there are ``locale`` or ``format`` parameters Babel is used to format the value 
       according to the given localization or format.
       
       :param obj: the object to be transformed in a string
       :param locale: add???. Default value is ``None``
       :param format: add???. Default value is ``None``
       :param mask: add???. Default value is ``None``
       :param encoding: The multibyte character encoding you choose. Default value is ``None``
       :param currency: add???. Default value is ``None``
       :returns: a unicode string representing an object of any class
       """
    if isinstance(obj, list) or isinstance(obj, tuple):
        return ','.join([toText(v) for v in obj])
        #what?
    if obj is None: return u''
    if not (locale or format):
        result = unicode(obj)
    else:
        result = localize(obj, locale=locale, format=format, currency=currency)
        
    if mask:
        result = mask % result
    return result
        
def guessLen(dtype, locale=None, format=None, mask=None, encoding=None):
    """
    :param dtype: add???.
    :param locale: add???. Default value is ``None``
    :param format: add???. Default value is ``None``
    :param mask: add???. Default value is ``None``
    :param encoding: The multibyte character encoding you choose. Default value is ``None``
    :returns: add???
    """
    typeSamples = {'B': 'true', 'D': datetime.date(2005, 10, 10), 'H': datetime.time(4, 5),
                   'DH': datetime.datetime.now(),
                   'I': 1234, 'L': 48205294, 'R': 34567.67, 'serial': 123445566}
    result = 10
    if dtype in typeSamples.keys():
        result = len(toText(typeSamples[dtype], format=format, mask=mask))
    return result
    
def boolean(obj):
    """add???
    
    :param obj: The given object
    :returns: add???
    """
    if obj and isinstance(obj, basestring):
        if obj.lower() in ['n', 'no', 'f', 'false', '0']:
            obj = False
    return bool(obj)
    
def pickleObject(obj, zipfilename=None):
    """Return the Pickle string for the given object.
        
    :param obj: The given object
    :param zipfilename: add???. Default value is ``None``
    :returns: the Pickle string for the given object
    """
    objstr = cPickle.dumps(obj)
    if zipfilename:
        objstr = zipString(objstr, zipfilename)
    return objstr
    
def unpickleObject(objstr, zipfilename=None):
    """Load an object from a pickle string.
        
    :param objstr: The given object string
    :param zipfilename: add???. Default value is ``None``
    :returns: the object loaded from the pickle string
    """
    if zipfilename:
        objstr = unzipString(objstr, zipfilename)
    return cPickle.loads(objstr)
    
def zipString(mystring, filename):
    """Return a zip compressed version of mystring
        
    :param mystring: The given string
    :param filename: add???
    :returns: a zip compressed version of ``mystring``
    """
    zipresult = StringIO.StringIO()
    zip = zipfile.ZipFile(zipresult, mode='w', compression=zipfile.ZIP_DEFLATED)
    zip.writestr(filename, mystring)
    zip.close()
    mystring = zipresult.getvalue()
    zipresult.close()
    return mystring
    
def unzipString(mystring, filename):
    """Extract a zip compressed string
        
    :param mystring: the compressed string to decompress
    :param filename: add???
    :returns: the decompressed string 
    """
    zipresult = StringIO.StringIO(mystring)
    zip = zipfile.ZipFile(zipresult, mode='r', compression=zipfile.ZIP_DEFLATED)
    result = zip.read(filename)
    zip.close()
    zipresult.close()
    return result
    
def toJson(obj):
    """add???
        
    :param obj: add???
    :returns: add???
    """
    #non so come testare
    return json.dumps(obj, cls=JsonEncoder)
    
def toJsonJS(obj):
    """add???
        
    :param obj: add???
    :returns: add???
    """
    return json.dumps(obj, cls=JsonEncoderJS)
    
def toSecureJsonJS(obj, key=None):
    """add???
        
    :param obj: add???
    :param key: add???. Default value is ``None``
    :returns: add???
    """
    result = json.dumps(obj, cls=JsonEncoderJS)
    if key:
        n = 0
        nmax = len(key)
        umax = len(result)
        t = nmax * umax
        for k in result:
            if n >= nmax:
                n = 0
            t = (t + (t + (ord(k) * ord(key[n]))) % umax)
            n = n + 1
        return '@%s_%s' % (str(t % 10000).zfill(4), result)
    else:
        return result
        
def slugify(value):
    """add???
        
    :param value: add???
    :returns: add???
    """
    import unicodedata
    
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)
    
def fromJson(obj):
    """add???
        
    :param obj: add???
    :returns: add???
    """
    #non so come testare
    return json.loads(obj)
    
def anyWordIn(wordlist, mystring):
    """Return a list of all the elements included both in ``wordlist`` and in ``mystring``
        
    :param wordlist: the list of words to be searched in ``mystring``
    :param mystring: the string on which there will be executed the search
    :returns: a list of all the elements included both in ``wordlist`` and in ``mystring``
    """
    return [k for k in wordlist if k in mystring]
    
def jsquote(str_or_unicode):
    """add???
        
    :param str_or_unicode: the string to be quoted
    :returns: add???
     
    >>> print jsquote('pippo')
    'pippo'
    >>> print jsquote(u'pippo')
    'pippo'
    """
    if isinstance(str_or_unicode, str):
        return repr(str_or_unicode)
    elif isinstance(str_or_unicode, unicode):
        return repr(str_or_unicode.encode('utf-8'))
        
if __name__ == '__main__':
    incl = '%.py,%.css'
    excl = '_%,.%'
    lst = ['pippo.py', 'piero.txt', '_gino.py', '.ugo.css', 'mario.css', 'sergio.py']
    result = [x for x in lst if filter(x, include=incl, exclude=excl)]
    print toJson([1, 2, 4])
    print result
   