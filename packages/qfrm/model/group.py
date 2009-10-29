#!/usr/bin/env python
# encoding: utf-8

# group table is used to group form_items into sections on the form
# in the section is defined an outer formBuilder.  The group goes into one of the outer form cells at
# an x y co-ordinate of the outer formBuilderbut may use colspan or row span for the group placement
# The group will be placed the first level of an inner form consisting of two rows and one column
# the top row is where the label for the group is displayed.  This of course can be empty.

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('group',  pkey='id', name_long='!!Group', rowcaption='label')
        self.sysFields(tbl,id=False)
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('section_id',size='22', group='_').relation('section.id',
                                                                 many_name='Group',
                                                                 one_name='Section',
                                                                 mode='foreignkey',
                                                                 onDelete='delete',
                                                                 one_group='')
        tbl.column('code', size=':10',name_long='!!Code')
        tbl.column('label', 'T', name_long='!!Short Name')
        tbl.column('x_position', 'I',name_long='!!X position')
        tbl.column('y_position', 'I',name_long='!!Y Position')
        tbl.column('colspan', 'I',name_long='!!Colspan')
        tbl.column('rowspan', 'I',name_long='!!Rowspan')

