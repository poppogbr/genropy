# -*- coding: UTF-8 -*-

# textbox.py
# Created by Niso on 2010-09-17.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Textbox"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    """
    =========
     textbox
    =========

    .. currentmodule:: form

    .. class:: textbox -  Genropy textbox

    	A simple textbox.

    	+-----------------------+---------------------------------------------------------+-------------+
    	|   Attribute           |          Description                                    |   Default   |
    	+=======================+=========================================================+=============+
    	| ``default``           | Add a default text                                      |  ``None``   |
    	+-----------------------+---------------------------------------------------------+-------------+
    	| ``font_size``         | CSS attribute                                           |  ``1em``    |
    	+-----------------------+---------------------------------------------------------+-------------+
    	| ``text_align``        | CSS attribute                                           |  ``left``   |
    	+-----------------------+---------------------------------------------------------+-------------+

    		Example::

    			pane.textbox(value='^box')
				
        """
        
    #   - Other forms, attributes and items:
    #       In this section we report forms/attributes that have been used in this example
    #       despite they didn't strictly belonging to boxes.
    #       We also suggest you the file (if it has been created!) where you can find
    #       some documentation about them.
    #
    #       ## name ##          --> ## file ##
    #       cols                --> formbuilder.py
    #       datapath            --> datapath.py
    #       formbuilder         --> formbuilder.py
    #       nodeId              --> form.py
    #       validate_len        --> form.py
    #       validate_onAccept   --> form.py
    #       validate_onReject   --> form.py
    #       value               --> datapath.py
    
    def test_1_textbox(self,pane):
        """Textbox"""
        fb = pane.formbuilder(datapath='test1',cols=2)
        fb.textbox(value='^.textBox',default='ciao')
        fb.div("A simple textbox.",font_size='.9em',text_align='justify')
        fb.textbox(value='^.textBox_2',nodeId='name',
                   validate_len='4:',
                   validate_onReject='alert(value+" is too short (minimum 4 characters)")',
                   validate_onAccept='alert("Correct lenght of "+value)')
        fb.div(""" A textbox with "validate" attributes. Here you have to write a text
                   with 4 or more characters.""",
                   font_size='.9em',text_align='justify')
        