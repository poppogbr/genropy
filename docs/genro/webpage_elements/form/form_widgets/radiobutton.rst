.. _genro_radiobutton:

===========
radiobutton
===========

    .. note:: The Genro radiobutton has been taken from Dojo without adding any modifies. In this page you will find some interesting features that we want to point up. For more information, check the Dojo's radiobutton documentation.
    
    * :ref:`radiobutton_def`
    * :ref:`radiobutton_description`
    * :ref:`radiobutton_attributes`
    * :ref:`radiobutton_examples`: :ref:`radiobutton_examples_simple`
    
.. _radiobutton_def:

Definition
==========

    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.radiobutton

.. _radiobutton_description:

Description
===========

    Radiobuttons are used when you want to let the user select one - and just one - option from a set of choices.
    
    If more options are to be allowed at the same time you should use :ref:`genro_checkbox`\es instead.

.. _radiobutton_attributes:

Attributes
==========
    
    **radiobutton attributes**:
    
    * *group*: Allow to create a radiobutton group. For more information, check the :ref:`radiobutton_examples_simple` below.
    
    **Common attributes**:
    
    * *disabled*: if True, allow to disable this widget. Default value is ``False``.
      For more information, check the :ref:`genro_disabled` documentation page
    * *hidden*: if True, allow to hide this widget. Default value is ``False``.
      For more information, check the :ref:`genro_hidden` documentation page
    * *label*: Set the radiobutton label
    * *value*: specify the path of the widget's value. For more information, check
      the :ref:`genro_datapath` documentation page
    * *visible*: if False, hide the widget (but keep a place in the :ref:`genro_datastore` for it).
      For more information, check the :ref:`genro_visible` documentation page
    
.. _radiobutton_examples:

Example
=======

.. _radiobutton_examples_simple:

simple example
--------------

    Let's see a simple example::
        
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb=root.contentPane(title='Buttons',datapath='test1').formbuilder(cols=4,border_spacing='10px')
                
                fb.div("""We show you here a simple radio buttons set; (add to your radiobuttons
                          the "group" attribute).""",font_size='.9em',text_align='justify')
                fb.radiobutton(value='^.radio.jazz',group='genre1',label='Jazz')
                fb.radiobutton(value='^.radio.rock',group='genre1',label='Rock')
                fb.radiobutton(value='^.radio.blues',group='genre1',label='Blues')
                
                fb.div("""Here we show you an other radio buttons set.""",
                          font_size='.9em',text_align='justify')
                fb.div('Sex')
                fb.radiobutton(value='^.sex.male',group='genre2',label='M')
                fb.radiobutton(value='^.sex.female',group='genre2',label='F')
