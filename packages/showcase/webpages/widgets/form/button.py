# -*- coding: UTF-8 -*-

# formbuilder.py
# Created by Niso on 2010-09-01.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Button"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerBase"
    # dojo_theme='claro'
    
    """ "Button" is a Dojo widget used as a representation of a normal button.
        You can act with it through "action" attribute, that allow you to use Javascript.
        - sintax: action="Here put Javascript code"
        
        You can also use "FIRE" attribute within "action" attribute; the difference is ... ???
        - sintax: action="FIRE 'javascript command'".
            Here is an example:
                pane.dataController('''alert(msg);''', msg='^msg')
                pane.button('Click me!',action="FIRE msg='Click!';")
            An alternative sintax is:
                pane.button('Click me!', fire_Click = 'msg')
                
        In Genro there are four macros used as a shortcut that you can use in the place of
        a Javascript command.
        Here is the list: FIRE, GET, SET, PUT. For more example see macro.py"""
        
        #   - Other forms and attributes:
        #       In this section we report forms/attributes that have been used in this example
        #       despite they didn't strictly belonging to button.
        #       We also suggest you the file (if it has been created!) where you can find
        #       some documentation about them.
        #
        #       ## name ##      --> ## file ##
        #       checkbox        --> togglebutton.py
        #       formbuilder     --> formbuilder.py
        #       FIRE            --> macro.py
        #       menu            --> menu.py
        #       menuline        --> menu.py
        #       numberTextbox   --> textbox.py
        #       textbox         --> textbox.py
        #       value           --> datapath.py
        
    def test_1_action(self,pane):
        """Action attribute"""
        pane.div(""" This button is used to create an alert message through "action" attribute.
                """,
                font_size='.9em',text_align='justify')
        pane.button('Button',action="alert('Hello!')",tooltip='click me!')
                    
    def test_2_fire(self,pane):
        """FIRE attribute"""
        pane.div("""There are three way to use FIRE:""",
                font_size='.9em',text_align='justify')
        pane.dataController('''alert(msg);''', msg='^msg')
        fb = pane.formbuilder(cols=2) # in this test formbuilder is only used to have a better layout
        fb.button('Click me!',action="FIRE msg='Click';")
        fb.div(""" "action="FIRE msg='Click';" by showing an alert message reporting "Click" """,font_size='.9em')
        fb.button('Click me!',fire_Click = 'msg')
        fb.div(""" "fire_Click = 'msg'" the result is the same of the previous one.""",font_size='.9em')
        fb.button('Click me!',fire='msg')
        fb.div(""" "fire='msg'" by showing an alert message reporting "true" """,font_size='.9em')
        
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
                    
    def test_4_checkbox(self,pane):
        """Checkbox button"""
        pane.div(""" Here we show you an example of checkbox button.""",
                font_size='.9em',text_align='justify')
        labels = 'First,Second,Third'
        labels=labels.split(',')
        pane=pane.formbuilder()
        for label in labels:
            pane.checkbox(value='^cb_%s'%label, label=label)
            
    def test_5_dropdownbutton(self,pane):
        """Dropdown button"""
        pane.div(""" Here we show you an example of dropdown button, using also "action" attribute
                (for further details, check "menu.py").""",
                font_size='.9em',text_align='justify')
        ddb=pane.dropdownbutton('Menù')
        dmenu=ddb.menu()
        dmenu.menuline('Open...', action="FIRE msg='Opening!';")
        dmenu.menuline('Close', action="FIRE msg='Closing!';")
        dmenu.menuline('-')
        submenu=dmenu.menuline('I have submenues').menu()
        submenu.menuline('To do this', action="alert('Doing this...')")
        submenu.menuline('Or to do that', action="alert('Doing that...')")
        dmenu.menuline('-')
        dmenu.menuline('Quit',action="alert('Quitting...')")
                    