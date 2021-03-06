#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

# menu.py
# Created by Giovanni Porcari on 2007-03-24.
# Copyright (c) 2007 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage

    def test_1_basic(self, pane):
        """A basic menu example"""
        ddb=pane.dropdownbutton('Menu')    # Same meaning: ddb=root.dropdownbutton(label='Menu')
        dmenu=ddb.menu()
        dmenu.menuline('Open...',action="alert('Opening...')")
        dmenu.menuline('Close',action="alert('Closing...')")
        dmenu.menuline('-')
        submenu=dmenu.menuline('I have submenues').menu() # With this line you create a submenu
        submenu.menuline('To do this',action="alert('Doing this...')")
        submenu.menuline('Or to do that',action="alert('Doing that...')")
        dmenu.menuline('-')
        dmenu.menuline('Quit',action="alert('Quitting...')")

    def test_2_bag(self, pane):
        """Menu with Bag"""
        pane.data('values.states', self.tableData_states())
        pane.data('values.sex', self.tableData_sex(), id='#k', caption='#v')
        pane.data('records', self.myRecords())
        fb = pane.formbuilder(cols='4', datapath='records', cellspacing='10', background_color='silver', margin='30px')
        for r in range(4):
            self.makeRow(fb, r)

        self.pageCtrlMenu(pane.menu('pagemenu'))
        self.pageShiftMenu(pane.menu('shiftmenu', modifiers='shift'))

        self.dropDownContent(fb.dropdownbutton('Open me'))
        self.connectionDialog(fb.dropdownbutton('Connection mode'))
        self.savingDialog(pane, 'savedlg')
        fb.button('Save as...', action='genro.savedlg.show()')

        dlg = pane.dialog(title='Saving all', datapath='saving', gnrId='savedlg').formbuilder(cols='2',
                                                                                              border_spacing='8px')
        dlg.textbox(lbl='Filename', value='^.filename')
        dlg.checkbox('Make a copy', value='^.docopy')
        dlg.button('Ok', action='genro.savedlg.hide()')

    def tableData_states(self):
        mytable = Bag()
        mytable.setItem('r1', None, id='CA', caption='California')
        mytable.setItem('r2', None, id='IL', caption='Illinois')
        mytable.setItem('r3', None, id='NY', caption='New York')
        mytable.setItem('r4', None, id='TX', caption='Texas')
        mytable.setItem('r5', None, id='AL', caption='Alabama')
        return mytable

    def savingDialog(self, pane, gnrId):
        dlg = pane.dialog(title='Saving all', datapath='saving', gnrId=gnrId).formbuilder(cols='2', cellspacing='8')
        dlg.textbox(lbl='Filename', value='^.filename')
        dlg.checkbox('Make a copy', value='^.docopy')
        dlg.button('Ok', action='genro.%s.hide()' % gnrId)

    def connectionDialog(self, dlg):
        tt = dlg.tooltipDialog(datapath='connection').formbuilder(cols='2', cellspacing='8', background_color='yellow')
        tt.textbox(lbl='Url', lbl_color='red', value='^.url')
        tt.textbox(lbl='User', value='^.user')
        tt.numberTextBox(lbl='Min time', value='^.maxtime')
        tt.numberTextBox(lbl='Min time', value='^.mintime')

    def dropDownContent(self, x):
        x = x.menu(action="function(x){alert('Selected:'+x.label)}")
        x.menuline('Do This')
        x.menuline('Do That', action="alert('Doing That')")
        p = x.menuline('Print to').menu()
        p.menuline('Printer')
        p.menuline('Fax')
        p.menuline('-')
        p.menuline('File')
        x.menuline('-')
        x.menuline('Do nothing')

    def pageCtrlMenu(self, m):
        m.menuline('Open...', gnrIcon='Save', action="alert('Opening now...')")
        m.menuline('Close...', action="alert('Closing now')")
        m.menuline('-')
        mz = m.menuline('Print to').menu()
        mz.menuline('Laser first floor', gnrIcon='Paste', background_color='green',
                    action="alert('Printing on the laser')")
        mz.menuline('Ink Jet', color='red', gnrIcon='Cut', action="alert('Wasting ink...')")

    def pageShiftMenu(self, m):
        m.menuline('gggg', gnrIcon='Save', action="alert('ggggggg')")
        m.menuline('hhhhh', action="alert('hhhhhhhhh')")

    def ageMenu(self, m):
        m.menuline('Over 18', specialattr='24', action="function(item){alert(item.specialattr)}")
        m.menuline('Over 30')
        m.menuline('-')
        mz = m.menuline('Older').menu()
        mz.menuline('Over 50', action="alert('Senior uh ?')")
        mz.menuline('Over 100', disabled=True)

    def makeRow(self, fb, r):
        name = fb.textBox(lbl='Name', value='^.r%i.name' % r)
        #age=fb.numberTextBox(lbl='Age', value='.r%i.age' % r)
        age = fb.numberSpinner(lbl='Age', value='^.r%i.age' % r)
        menu = age.menu(action="function(item){alert(item.label)}")
        self.ageMenu(menu)

        sex = fb.filteringSelect(lbl='Sex', value='^.r%i.sex' % r, storepath='values.sex')
        state = fb.filteringSelect(lbl='State', value='^.r%i.state' % r, storepath='values.states')

    def myRecords(self):
        data = Bag()
        data['r0.name'] = 'John'
        data['r0.age'] = 26
        data['r0.sex'] = 'M'
        data['r0.state'] = 'TX'
        data['r1.name'] = 'Mary'
        data['r1.age'] = 31
        data['r1.sex'] = 'F'
        data['r1.state'] = 'CA'
        return data

    def tableData_sex(self):
        mytable = Bag()
        mytable.setItem('M', 'Male')
        mytable.setItem('F', 'Female')
        return mytable