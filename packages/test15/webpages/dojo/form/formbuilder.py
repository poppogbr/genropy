# -*- coding: UTF-8 -*-
# 
"""Formbuilder"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    dojo_theme = 'tundra'

    def test_1_basic(self, pane):
        """Basic formbuilder"""
        fb = pane.formbuilder(cols=2, border_spacing='3px', width='100%', fld_width='30px')
        fb.textbox(value='^.aaa', lbl='aaa', width='100%')
        fb.textbox(value='^.bb', lbl='bb')
        fb.textbox(value='^.cc', lbl='cc', width='100%', colspan=2)

    def test_1_field(self, pane):
        """Field formbuilder"""
        fb = pane.formbuilder(cols=2, border_spacing='3px', dbtable='polimed.medico',
                              fld_width='100%', width='100%')
        fb.field('@anagrafica_id.cognome', _class='pippo', lbl_class='ttt')
        fb.field('@anagrafica_id.nome')
        fb.field('@anagrafica_id.indirizzo', width='100%', colspan=2)
        fb.field('@anagrafica_id.azienda')
        fb.field('@anagrafica_id.azienda', tag='radiobutton')