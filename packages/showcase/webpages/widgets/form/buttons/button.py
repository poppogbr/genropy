# -*- coding: UTF-8 -*-

# button.py
# Created by Niso on 2010-09-01.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Button"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    """
    =========
     Buttons
    =========
    
    .. currentmodule:: widgets

    .. class:: Buttons -  Genropy buttons
    
    **Definition**: same definition of Dojo buttons (version 1.4). To show it, click here_.
    
    .. _here: http://docs.dojocampus.org/dijit/form/Button

    	This is not a real class, but only one way to combine the methods of the struct that implements interface **buttons**

    .. method:: button(label[, fire=datapath][, action=javascript][, hidden=boolean or resolver])

    	Button is a Dojo widget used as a representation of a normal button. You can act with it through "action" attribute, a js that is executed on mouse click.

    	Example::

    		pane.button('Button',action="alert('Hello!')")

    	You can also use "FIRE" attribute within "action" attribute (action="FIRE 'javascript command'").

    	Here is an example::

    		pane.dataController('''alert(msg);''', msg='^msg')
    		pane.button('Click me!',action="FIRE msg='Click!';")

    	An alternative sintax is::

    		pane.button('Click me!', fire_Click = 'msg')

        In Genro there are four macros used as a shortcut that you can use in place of a Javascript command.

    	Here is the list: FIRE, GET, SET, PUT.
    """
        
        #   - Other forms and attributes:
        #       In this section we report forms/attributes that have been used in this example
        #       despite they didn't strictly belonging to button.
        #       We also suggest you the file (if it has been created!) where you can find
        #       some documentation about them.
        #
        #       ## name ##      --> ## file ##
        #       datapath        --> datapath.py
        #       formbuilder     --> formbuilder.py
        #       menu            --> menu.py
        #       menuline        --> menu.py
        #       numberTextbox   --> textbox.py
        #       textbox         --> textbox.py
        #       value           --> datapath.py
        
    def test_1_action(self,pane):
        """Action attribute"""
        fb = pane.formbuilder(cols=2)
        fb.button('Button',action="alert('Hello!')",tooltip='click me!')
        fb.div(""" This button is used to create an alert message through "action" attribute.
                 """,font_size='.9em',text_align='justify')
        
    def test_2_fire(self,pane):
        """FIRE attribute"""
        pane.div("""There are three way to use FIRE:""",
                font_size='.9em',text_align='justify')
        pane.dataController('''alert(msg);''', msg='^msg')
        fb = pane.formbuilder(cols=2) # in this test formbuilder is only used to have a better layout
        fb.button('Click me!',action="FIRE msg='Click';")
        fb.div(""" "action="FIRE msg='Click';" [shows an alert message reporting "Click"] """,font_size='.9em')
        fb.button('Click me!',fire_Click = 'msg')
        fb.div(""" "fire_Click = 'msg'" [same result of the previous one]""",font_size='.9em')
        fb.button('Click me!',fire='msg')
        fb.div(""" "fire='msg'" [shows an alert message reporting "true"] """,font_size='.9em')
        
    def test_3_graphical_attributes(self,pane):
        """Graphical attributes"""
        pane.div(""" You can also change appearance of your button, with Dojo and CSS button attributes.""",
                font_size='.9em',text_align='justify')
        pane.data('icon','icnBaseOk')
        pane.data('fontType','Courier')
        pane.data('widthButton','10em')
        pane.data('fontSize','22px')
        pane.data('color','green')
        pane.button('Click me',iconClass='^icon',width='^widthButton',color='^color',
                    font_size='^fontSize',font_family='^fontType',action="alert('Clicked!')")
                    
                    