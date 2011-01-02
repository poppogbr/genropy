# -*- coding: UTF-8 -*-

# bordercontainer.py
# Created by Francesco Porcari on 2010-08-16.
# Copyright (c) 2010 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    dojo_theme = 'claro'

    def windowTitle(self):
        return ''

    def test_bordercontainer_mixedlayout(self, pane):
        bc = pane.borderContainer(height='300px')
        bc.contentPane(region='top', height='20px', background='red', splitter=True)
        tc = bc.tabContainer(region='left', width='400px')
        tc.contentPane(title='aa')
        tc.contentPane(title='bb')
        ac = bc.accordionContainer(region='right', width='400px')
        bc2 = ac.borderContainer(title='aa', background='black')
        bc2.contentPane(region='bottom', height='30px', background='silver')
        bc2.contentPane(region='center', background='lime')
        ac.contentPane(title='bb')
        bc.contentPane(region='center', background='yellow')

class ToFix(object):
    """
    we have to add regions in genroway
    """

class FixedToCheck(object):
    """
    """

class Fixed(object):
    """docstring for Fixed"""
        