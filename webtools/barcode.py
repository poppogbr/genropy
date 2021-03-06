#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

# --------------------------- BaseWebtool subclass ---------------------------


from gnr.web.gnrbaseclasses import BaseWebtool
#from code39 import Code39Encoder
from huBarcode.code128 import Code128Encoder
from huBarcode.datamatrix import DataMatrixEncoder
from huBarcode.qrcode import QRCodeEncoder
from huBarcode.ean13 import EAN13Encoder
import tempfile
import mimetypes

encoders = {
    #'code39' : Code39Encoder,
    'code128': Code128Encoder,
    'datamatrix': DataMatrixEncoder,
    'qrcode': QRCodeEncoder,
    'ean13': EAN13Encoder

}
class Barcode(BaseWebtool):
    #content_type = 'image/png'
    #headers = [('header_name','header_value')]


    def __call__(self, text=None, mode='code128', height=None, width=None, suffix='.png', **kwargs):
        encoder = encoders.get(mode)
        if not encoder:
            return
        barcode = encoder(text)
        temp = tempfile.NamedTemporaryFile(suffix=suffix)
        barcode.save(temp.name)
        self.content_type = mimetypes.guess_type(temp.name)[0]
        return temp.read()
        