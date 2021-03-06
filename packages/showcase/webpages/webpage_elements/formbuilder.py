# -*- coding: UTF-8 -*-

# formbuilder.py
# Created by Filippo Astolfi on 2010-09-20.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Formbuilder"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    def test_1_basic(self, pane):
        """Standard formbuilder"""
        pane.div("""Since we haven't changed any of the default attributes of the formbuilder,
                the fields are stacked on a single column, have a dimension of '7em' and
                have a space of 6 pixels between fields themselves.
                In test_3 we'll make some changes of formbuilder default attributes.""",
                 font_size='.9em', text_align='justify')
        fb = pane.formbuilder(datapath='test1')
        fb.textbox(value='^.name', lbl='Name')
        fb.textbox(value='^.surname', lbl='Surname')
        
    def test_2_structure(self, pane):
        """Formbuilder structure"""
        pane.div("""Every formbuilder column is splitted in two parts (left one and right one):
                the right part is the one where user can compile fields, while the left part
                is where "lbl" attribute appear. You can also see the effect of
                "border_spacing" css attribute, that is the space between fields.
                Last thing: to help you in discovering of the formbuilder hidden structure
                we used the "border" attribute (the outcome doesn't follow the standard of
                beauty, but the example is very instructive!).""",
                 font_size='.9em', text_align='justify')
        fb = pane.formbuilder(datapath='test2', border='5px', cols=2)
        fb.textbox(value='^.name', lbl='Name')
        fb.textbox(value='^.surname', lbl='Surname')
        fb.textbox(value='^.job', lbl='Profession')
        fb.numberTextbox(value='^.age', lbl='Age')
        fb.div('Favorite sport:')
        fb.div('Favorite browser:')
        fb.checkbox(value='^.football', label='Football')
        fb.radiobutton('Internet explorer', value='^.radio1', group='genre1')
        fb.checkbox(value='^.basketball', label='Basketball')
        fb.radiobutton('Mozilla Firefox', value='^.radio2', group='genre1')
        fb.checkbox(value='^.tennis', label='Tennis')
        fb.radiobutton('Google Chrome', value='^.radio3', group='genre1')
        
    def test_3_attributes(self, pane):
        """Formbuilder attributes"""
        pane.div("""When a formbuilder attribute begins with "lbl_" (like "lbl_width='10px'"),
                it means that EVERY "lbl" field attribute will be gain its properties.
                The same thing happens for each formbuilder attribute that begins with
                "fld_" (like "fld_width='10em'").""",
                 font_size='.9em', text_align='justify')
        pane.div("""To create a beautiful form, we suggest you to write "fld_width='100%'"
                and "width='100%'" as formbuilder attributes.""",
                 font_size='.9em', text_align='justify')
        pane.div(""" "cols" set the number of columns of the formbuilder. If you set cols=2
                and create 3 fields, they will be placed into two columns like this:""",
                 font_size='.9em', text_align='justify')
        pane.span("field_1 ", font_size='.9em', text_align='justify')
        pane.span("field_2", font_size='.9em', text_align='justify')
        pane.div("field_3", font_size='.9em', text_align='justify')
        pane.div("Setting \"cols=3\" would have led to this result, as we expected in an HTML table:",
                 font_size='.9em', text_align='justify')
        pane.span("field_1 field_2 field_3", font_size='.9em', text_align='justify')
        pane.div("""With "colspan" you can fullfil with a single field the space of two or more
                field (for an example check the textbox with 'lbl=Surname')""",
                 font_size='.9em', text_align='justify')
        pane.div("\"fld_width\" set the dimension of every field.",
                 font_size='.9em', text_align='justify')
                 
        fb = pane.formbuilder(datapath='test3', cols=2, fld_width='100%', width='100%', lbl_color='red')
        fb.textbox(value='^.name', lbl='Name')
        fb.textbox(value='^.surname', lbl='Surname')
        fb.numberTextbox(value='^.age', lbl="Age")
        fb.textbox(value='^.mail', lbl='Mail')
        fb.filteringSelect(value='^.sex', values='M:Male,F:Female', lbl='Sex')
        fb.textbox(value='^.job.profession', lbl='Job')
        fb.textbox(value='^.job.company_name', lbl='Company name')
        fb.textbox(value='^.job.fiscal_code', lbl='Fiscal code')
        
    def test_4_disabled(self, pane):
        """Disabled, hidden and visible"""
        bc = pane.borderContainer(datapath='test4')
        bc.data('^.visible',True)
        bc.div("""In this test you can see the effect of the three attributes
                  applied on the formbuilder:""",font_size='.9em', text_align='justify')
        bc.div("disabled: if True, user can't write in the form",font_size='.9em', text_align='justify')
        bc.div("hidden: if True, the formbuilder is hidden",font_size='.9em', text_align='justify')
        bc.div("visible: if False, user can't see the formbuilder and its form fields",
                font_size='.9em', text_align='justify')
        fb = bc.formbuilder()
        fb.checkbox(value='^.disabled', label='Disable form')
        fb.checkbox(value='^.hidden', label='Hidden form')
        fb.checkbox(value='^.visible', label='Visible form')
        
        fb = bc.formbuilder(cols=2,width='10em',disabled='^.disabled',hidden='^.hidden',visible='^.visible')
        fb.textbox(value='^.name', lbl='Name')
        fb.textbox(value='^.surname', lbl='Surname')
        fb.numberTextbox(value='^.age', lbl="Age", width='4em')
        fb.dateTextbox(value='^.birthdate', lbl='Birthdate')
        fb.filteringSelect(value='^.sex', values='M:Male,F:Female', lbl='Sex')
        fb.textbox(value='^.job.profession', lbl='Job')
        fb.textbox(value='^.job.company_name', lbl='Company name')
        
    # This is a bad test to correct the lblpos and lblalign functioning...
    def test_5_pos_align(self, pane):
        """lblpos and lblalign"""
        pane.div('lblpos = \'L\' ')
        bc = pane.borderContainer(datapath='test5')
        fb = bc.formbuilder(cols=2, lblpos='L')
        fb.textbox(value='^.top', lbl='left')
        fb.textbox(value='^.top2', lbl='left')
        fb.textbox(value='^.top3', lbl='left')
        fb.textbox(value='^.top4', lbl='left')
        
        pane.div('lblpos = \'T\' ')
        fb = bc.formbuilder(cols=2, lblpos='T')
        fb.textbox(value='^.top', lbl='top')
        fb.textbox(value='^.top2', lbl='top')
        fb.textbox(value='^.top3', lbl='top')
        fb.textbox(value='^.top4', lbl='top')
        
        pane.div('lblalign = \'left\' ')
        fb = bc.formbuilder(cols=2, lblpos='T', lblalign='left')
        fb.textbox(value='^.top', lbl='left')
        fb.textbox(value='^.top2', lbl='left')
        fb.textbox(value='^.top3', lbl='left')
        fb.textbox(value='^.top4', lbl='left')
        
        pane.div('lblalign = \'right\' ')
        fb = bc.formbuilder(cols=2, lblpos='T', lblalign='right')
        fb.textbox(value='^.top', lbl='right')
        fb.textbox(value='^.top2', lbl='right')
        fb.textbox(value='^.top3', lbl='right')
        fb.textbox(value='^.top4', lbl='right')
        