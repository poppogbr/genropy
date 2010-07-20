#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

import datetime
from gnr.core.gnrbag import Bag, DirectoryResolver

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        fb = root.formbuilder(datapath='form')
        fb.button(label='Upload',
                    action='genro.dlg.upload("Upload something","importMethod","aux.resultPath")')
        fb.simpleTextarea(value='^aux.resultPath',width='30em',height='40em')
        
    def rpc_importMethod(self,**kwargs):
        """What I do with my file on server"""
        try:
            f = kwargs['fileHandle'].file
            text = f.read()
            result = """Content-Type: text/html
                <html>
                    <head>
                    </head>
                    <body>
                        <textarea>%s</textarea>
                    </body>
                </html>
                """ % text
        except Exception, e:
            result = """Content-Type: text/html
                <html>
                    <head>
                    </head>
                    <body>
                        <textarea>It doesn't work</textarea>
                    </body>
                </html>
            """
        return result