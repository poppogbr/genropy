.. _genro_database_rowcaption:

==========
Rowcaption
==========

    * :ref:`database_definition`
    * :ref:`database_description_examples`: :ref:`rowcaption_model_table`, :ref:`rowcaption_webpage`

.. _database_definition:

Definition
==========

    *rowcaption* is the textual representation of a record, and it is used with all the form widgets that draw their value from a database :ref:`model_table`, that are :ref:`genro_field`, :ref:`genro_dbselect` and :ref:`genro_dbcombobox`.

.. _database_description_examples:

Description and examples
========================

    *rowcaption* can be defined in two places:

        * directly into the database table: check :ref:`rowcaption_model_table`
        * in the query-field (``field``, ``dbselect`` or ``dbcombobox``) placed into the webpage: check :ref:`rowcaption_webpage`

.. _rowcaption_model_table:

rowcaption in the database table
================================

    Let's see an example::

        class Table(object):
            def config_db(self, pkg):
                tbl = pkg.table('person',pkey='id',rowcaption='$name',
                                 name_long='!!people',name_plural='!!People')

    The syntax is ``$`` followed by the name of a column, like::

        rowcaption='$name'

    You can add more than one column in the rowcaption, like::

        rowcaption='$name,$nationality'

    The graphical result is the list of attributes separated by a "-", like::

        Alfred Hitchcock - UK

    or::

        rowcaption='$name,$nationality:%s: %s' # where the %s: %s are placeholders providing an
                                               # alternate way to format the rowcaption with fields
                                               # and addition characters.

    Obviously, you can also use the "@" syntax (check in :ref:`model_table` page for further details).

.. _rowcaption_webpage:

rowcaption in the query-field
=============================

    Let's see an example on putting the *rowcaption* attribute directly in the webpage::

        class Table(object):
            def config_db(self, pkg):
                tbl = pkg.table('person',pkey='id',
                                 name_long='!!people',name_plural='!!People')

    In this case, we define the table without using the *rowcaption* attribute. We have to put it into the webpage, like::

        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb=pane.formbuilder(datapath='test1',cols=2)
                fb.field(dbtable='showcase.person',rowcaption='$name',
                         value='^.person_id',lbl='Star')
