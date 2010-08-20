#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        #   horizontalSlider - DEFAULT parameters:
        #       minimum=0, maximum=100, intermediateChanges=False
        
        fb=root.formbuilder(cols=3,datapath='math')
        fb.horizontalSlider(value='^.number',width='250px',maximum=50,
                            intermediateChanges=True,discreteValues=51,lbl='!!Integer number')
        fb.numberTextBox(value='^.number',width='10em')
        fb.br()
        fb.horizontalSlider(value='^.f_number',width='250px',minimum=10,
                            default=25,intermediateChanges=True,lbl='!!Float number')
        fb.numberTextBox(value='^.f_number',width='10em',places='^.decimals')
        fb.numberSpinner(value='^.decimals',width='4em',min=0,max=15,lbl='decimals')