#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        bc = root.borderContainer()
        top = bc.contentPane(region='top',height='3ex',background_color='green')
        left = bc.contentPane(region='left',width='5em',background_color='orange',splitter=True)
        center= bc.tabContainer(region='center',background_color='silver')
        tab1 = center.contentPane(title='tab1')
        tab2 = center.accordionContainer(title='Accordion')
        acc1 = tab2.accordionPane(title='acc1')
        acc2 = tab2.accordionPane(title='acc2')