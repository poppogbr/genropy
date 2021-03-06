.. _genro_datastore:

===========
 datastore
===========

    * :ref:`datastore_description`
    * :ref:`datastore_syntax`
    * :ref:`datastore_access`
    * :ref:`datastore_debugger`

.. _datastore_description:

Description
===========
    
    The datastore is a Genro :ref:`genro_bag_intro` used to keep track of data.
    
    Through various python commands, you can attach the javascript code to the events of the components interface or events generated by the datastore.

.. _datastore_syntax:

Datastore syntax
================
    
    The path followed by the syntax in the datastore:
    
    * ``path`` --> absolute path in datastore
    * ``.path`` --> relative path in datastore
    * ``#ID`` --> path relative to the ID
    
    The path indicates the access path to data to every element of the datastore (it is implemented by reading the Bag interface, and thus includes many things: for example, you can also specify the CSS classes of an HTML element linking them to an element of the datastore), using the prefixes:

    * "^" (circumflex accent): ``^access.to.resolver``, setting an observer at this node. The component will be informed of changes to the datastore
    * equal: ``=accessed.from.resolver``, reads the datastore content.
    
    For more information on absolute and relative paths, check the :ref:`genro_datapath` documentation page.

.. _datastore_access:

Access to the datastore from javascript
=======================================

    The possible operations on the datastore include some macros, that are:
    
    * :ref:`genro_set`
    * :ref:`genro_put`
    * :ref:`genro_get`
    * :ref:`genro_fire`
    
    They can be specified in the javascript events associated with an interface, and the framework deals gnrjs to the expansion of these macros. Check the :ref:`genro_macro` page for further details.

.. _datastore_debugger:

The datastore graphical interface
=================================

..The Genro Team is going to change the GI developer tools: until it won't be stable, there is no interest to document this part

    You can access to its graphic interface from any Genro webpage by clicking ``ctrl+shift+D`` [#]_:
    
        .. image:: ../images/datastore.png

**Footnotes**

.. [#] For Mac and Windows users. For Linux users, you have to push ... ???