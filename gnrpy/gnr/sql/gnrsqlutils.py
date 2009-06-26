#!/usr/bin/env python
# encoding: utf-8
"""
gnrsqlutils.py

Created by Saverio Porcari on 2007-09-20.
Copyright (c) 2007 __MyCompanyName__. All rights reserved.
"""

from gnr.core import gnrlist
from gnr.core.gnrbag import Bag
from gnr.sql.gnrsql_exceptions import GnrNonExistingDbException

class ModelExtractor(object):
    def __init__(self, dbroot):
        self.dbroot = dbroot
        
    def extractModelSrc(self, root):
        self.buildSchemata(root)
        self.buildRelations(root)
        return root
        
    def buildSchemata(self, root):
        elements = self.dbroot.adapter.listElements('schemata')
        for pkg_name in elements:
            pkg = root.package(pkg_name, sqlschema=pkg_name, sqlprefix='')
            self.buildTables(pkg, pkg_name)
            
    def buildTables(self, pkg, pkg_name):
        elements=self.dbroot.adapter.listElements('tables', schema=pkg_name)
        for tbl_name in elements:
            tbl = pkg.table(tbl_name)
            self.buildColumns(tbl, pkg_name, tbl_name)
            self.buildIndexes(tbl, pkg_name, tbl_name)
            
    def buildColumns(self, tbl, pkg_name, tbl_name):
        columns = list(self.dbroot.adapter.getColInfo(schema=pkg_name, table=tbl_name))
        gnrlist.sortByItem(columns, 'position')

        for col_dict in columns:
            col_dict.pop('position')
            colname = col_dict.pop('name')
            length = col_dict.pop('length', 0)
            dtype = col_dict['dtype']
            if dtype=='A':
                col_dict['size'] = '0:%s' % length
            elif dtype=='C':    
                col_dict['dtype'] = 'A'
                col_dict['size'] = length
            col =  tbl.column(colname, **dict([(k,v) for k,v in col_dict.items() if not k.startswith('_')]))
        pkey = self.dbroot.adapter.getPkey(schema=pkg_name, table=tbl_name)
        if len(pkey) == 1:
            tbl.parentNode.setAttr(pkey=pkey[0])
        elif len(pkey)>1:
            pass #multiple pkey
        else:
            pass #there's no pkey
        pass
    
    def buildIndexes(self, tbl, pkg_name, tbl_name):
        for ind in self.dbroot.adapter.getIndexesForTable(schema=pkg_name, table=tbl_name):
            if not ind['primary']:
                tbl.index(ind['columns'], name=ind['name'], unique=ind['unique'])
                
    def buildRelations(self, root):
        relations = self.dbroot.adapter.relations()
        for (many_rel_name, many_schema, many_table, many_cols, one_rel_name, one_schema, one_table, one_cols) in relations:
            #one_rel_name = self.relName(ref, tbl)
            many_field = many_cols[0]
            one_field = one_cols[0]
            
            fld = root['packages.%s.tables.%s.columns.%s' % (many_schema, many_table, many_field)]
            fld.relation('%s.%s.%s' % (one_schema, one_table, one_field))
            
    def buildViews(self):
        elements=self.dbroot.adapter.listElements('views', schema=self.schema)
        children = Bag(self.children) 
        for element in elements:
            if not element in children:
                children.setItem(element, None, tag='view')                
        return SqlTableList(parent=self.structparent, name=self.name, attrs=self.attrs, children=children)

class SqlModelChecker(object):
    """
    This class has to keep a database aligned with its logical structure in the GnrSqlDb.
    If there is any change in the modelobj, database is automatically updated.
    """
    def __init__(self, db):
        self.db = db
        
    def checkDb(self):
        """
        prepares self.actual_tables, self.actual_schemata, self.actual_views and calls _checkPackage for each package.
        Returns a list of instructions for the database building.
        """
        create_db = False
        self.changes = []
        self.bagChanges = Bag()
        try:
            self.actual_schemata = self.db.adapter.listElements('schemata')
        except GnrNonExistingDbException, exc:
            self.actual_schemata = []
            self.actual_tables = {}
            self.actual_views = {}
            self.actual_relations = {}
            self.changes.append(self.db.adapter.createDbSql(exc.dbname, 'UNICODE'))
            create_db = True
        if not create_db:
            self.actual_tables = dict([(k, self.db.adapter.listElements('tables', schema=k)) for k in self.actual_schemata])
            self.actual_views = dict([(k, self.db.adapter.listElements('views', schema=k)) for k in self.actual_schemata])
            actual_relations = self.db.adapter.relations()
            self.actual_relations = {}
            for r in actual_relations:
                self.actual_relations.setdefault('%s.%s' % (r[1], r[2]), []).append(r)
        
        for pkg in self.db.packages.values():
            #print '----------checking %s----------'%pkg.name
            self._checkPackage(pkg)
        self._checkAllRelations()
        return [x for x in self.changes if x]
    
    def _checkPackage(self, pkg):
        """
        Check if the current package is contained by a not defined schema and then calls
        checkTable for each table and checkView for each view.
        Returns a list containing sql statements"""
        self._checkSqlSchema(pkg)
        if pkg.tables:
            for tbl in pkg.tables.values():
                #print '----------checking table %s----------'%tbl.name
                self._checkSqlSchema(tbl)
                if tbl.sqlname in self.actual_tables.get(tbl.sqlschema, []):
                    tablechanges = self._checkTable(tbl)
                else:
                    tablechanges = self._buildTable(tbl)#Create sql commands to BUILD the missing table
                self.bagChanges.setItem('%s.%s' % (tbl.pkg.name, tbl.name), None, changes='\n'.join([ch for ch in tablechanges if ch]))
                
        #views = node.value['views']
        #if views:
            #for viewnode in views:
                #tbl_schema = self._checkSqlSchema(sql, node, pkg_schema)
                #if self.sqlName(viewnode) in self.actual_views.get(tbl_schema, []):
                    #sql.extend(self._checkView(viewnode, tbl_schema))
                #else:
                    #sql.extend(self._buildView(viewnode, tbl_schema))
    
    def _checkSqlSchema(self, obj):
        """
        If the package/table/view is defined in a new schema that's not in the actual_schemata
        the new schema is created and its name is appended to self.actual_schemata.
        Returns the schema name.
        """
        sqlschema = obj.sqlschema
        if sqlschema and not (sqlschema in self.actual_schemata) and not (sqlschema == self.db.main_schema):
            change = self.db.adapter.createSchemaSql(sqlschema)
            self.changes.append(change)
            self.bagChanges.setItem(obj.name, None, changes=change)
            self.actual_schemata.append(sqlschema)
            
    def _checkTable(self, tbl):
        """
        It checks if any column has been changed and then it builds
        the sql statements for adding/deleting/editing table's columns calling _buildColumn.
        """
        tablechanges = []
        if tbl.columns:
            dbcolumns = dict([(c['name'], c) for c in self.db.adapter.getColInfo(schema=tbl.sqlschema, table=tbl.sqlname)])
            for col in tbl.columns.values():
                if col.sqlname in dbcolumns:
                    #it there's the column it should check if has been edited.
                    pass
                    #sql.extend(self.checkColumn(colnode, dbcolumns[self.sqlName(colnode)]))
                else:
                    change = self._buildColumn(col)
                    self.changes.append(change)
                    tablechanges.append(change)
                    self.bagChanges.setItem('%s.%s.columns.%s' % (tbl.pkg.name, tbl.name, col.name), None, changes=change)
                    
        if tbl.indexes:
            dbindexes = dict([(c['name'], c) for c in self.db.adapter.getIndexesForTable(schema=tbl.sqlschema,table=tbl.sqlname)])
            for idx in tbl.indexes.values():
                if idx.sqlname in dbindexes:
                    pass
                else:
                    icols = idx.getAttr('columns')
                    icols = ','.join([tbl.column(col.strip()).sqlname for col in icols.split(',')])
                    unique = idx.getAttr('unique')
                    change = self._buildIndex(tbl.sqlname, idx.sqlname, icols, sqlschema=tbl.sqlschema, unique=unique, pkey=tbl.pkey)
                    self.changes.append(change)
                    tablechanges.append(change)
                    self.bagChanges.setItem('%s.%s.indexes.%s' % (tbl.pkg.name, tbl.name, idx.sqlname), None, changes=change)
        return tablechanges

    def _checkAllRelations(self):
        for pkg in self.db.packages.values():
            for tbl in pkg.tables.values():
                self._checkTblRelations(tbl)
                
    def _checkTblRelations(self, tbl):
        if tbl.relations:
            tbl_actual_rels = self.actual_relations.get(tbl.sqlfullname, [])[:] #get all db foreignkey of the current table
            relations = [rel[0] for rel in tbl.relations.digest('#a.joiner') if rel]
            for rel in relations:
                if rel.get('foreignkey'): # link has foreignkey constraint
                    o_pkg_sql, o_tbl_sql, o_fld_sql, m_pkg_sql, m_tbl_sql, m_fld_sql = self._relationToSqlNames(rel)
                    on_up = self._onStatementToSql(rel.get('onUpdate_sql')) or 'NO ACTION'
                    on_del = self._onStatementToSql(rel.get('onDelete_sql')) or 'NO ACTION'
                    init_deferred = self._deferredToSql(rel.get('deferred'))
                    existing = False
                    tobuild = True
                    
                    for actual_rel in tbl_actual_rels:
                        if actual_rel[3][0] == m_fld_sql: #if db foreignkey is on current col
                            linkto_sql = '%s.%s' % (actual_rel[5], actual_rel[6])
                            if linkto_sql== '%s.%s' % (o_pkg_sql, o_tbl_sql): #if db foreignkey link on current many table
                                if actual_rel[7][0] == o_fld_sql:#if db foreignkey link on current many field
                                    existing=True
                                    tobuild=False
                                    tbl_actual_rels.pop(tbl_actual_rels.index(actual_rel))
                                    if actual_rel[8] != on_up:
                                        tobuild=True
                                        break
                                    if actual_rel[9] != on_del:
                                        tobuild=True
                                        break
                                    if (actual_rel[10]=='YES' and not rel.get('deferred')) or (actual_rel[10]=='NO' and  rel.get('deferred')):
                                        tobuild=True
                                        break
                                        
                    if tobuild:
                        if existing:
                            change = self._dropForeignKey(m_pkg_sql, m_tbl_sql, m_fld_sql)
                            self.changes.append(change)
                            self.bagChanges.setItem('%s.%s.relations.%s' % (tbl.pkg.name, tbl.name, 'fk_%s_%s' % (m_tbl_sql, m_fld_sql)), None, changes=change)
                            prevchanges = self.bagChanges.getAttr('%s.%s' % (tbl.pkg.name, tbl.name), 'changes')
                            self.bagChanges.setAttr('%s.%s' % (tbl.pkg.name, tbl.name), None, changes='%s\n%s' % (prevchanges, change))
                        change = self._buildForeignKey(o_pkg_sql, o_tbl_sql, o_fld_sql, m_pkg_sql, m_tbl_sql, m_fld_sql, on_up, on_del, init_deferred)
                        self.changes.append(change)
                        self.bagChanges.setItem('%s.%s.relations.%s' % (tbl.pkg.name, tbl.name, 'fk_%s_%s' % (m_tbl_sql, m_fld_sql)), None, changes=change)
                        prevchanges = self.bagChanges.getAttr('%s.%s' % (tbl.pkg.name, tbl.name), 'changes')
                        self.bagChanges.setAttr('%s.%s' % (tbl.pkg.name, tbl.name), None, changes='%s\n%s' % (prevchanges, change))
            #for remaining_relation in tbl_actual_rels:
            #    print remaining_relation
                #change = self._dropForeignKey(m_pkg_sql, m_tbl_sql, m_fld_sql)
                #self.changes.append(change)
                #self.bagChanges.setItem('%s.%s.relations.%s' % (tbl.pkg.name, tbl.name, 'fk_%s_%s' % (m_tbl_sql, m_fld_sql)), None, changes=change)
                #prevchanges = self.bagChanges.getAttr('%s.%s' % (tbl.pkg.name, tbl.name), 'changes')
                #self.bagChanges.setAttr('%s.%s' % (tbl.pkg.name, tbl.name), None, changes='%s\n%s' % (prevchanges, change))
                

    def _onStatementToSql(self,command):
        if not command: return None
        command=command.upper()
        if command in ('R','RESTRICT'):
            return 'RESTRICT'
        elif command in ('C','CASCADE'):
            return 'CASCADE'
        elif command in ('N','NO ACTION'):
            return 'NO ACTION'
        elif command in ('SN','SETNULL','SET NULL'):
            return 'SET NULL'
        elif command in ('SD','SETDEFAULT','SET DEFAULT'):
            return 'SET DEFAULT'
            
    def _deferredToSql(self,command):
        if command==None: 
            return None
        if command==True:
            return 'DEFERRABLE INITIALLY DEFERRED'
        if command==False:
            return 'DEFERRABLE INITIALLY IMMEDIATE'


    def _relationToSqlNames(self, rel):
        o_pkg, o_tbl, o_fld = rel['one_relation'].split('.')
        m_pkg, m_tbl, m_fld = rel['many_relation'].split('.')
        
        m_tbl = self.db.table('%s.%s' % (m_pkg, m_tbl)).model

        m_pkg_sql = m_tbl.sqlschema
        m_tbl_sql = m_tbl.sqlname
        m_fld_sql = m_tbl.column(m_fld).sqlname
        
        o_tbl = self.db.table('%s.%s' % (o_pkg, o_tbl)).model
                                    
        o_pkg_sql = o_tbl.sqlschema
        o_tbl_sql = o_tbl.sqlname
        o_fld_sql = o_tbl.column(o_fld).sqlname
        
        return o_pkg_sql, o_tbl_sql, o_fld_sql, m_pkg_sql, m_tbl_sql, m_fld_sql

    def _buildTable(self, tbl):
        """It prepares the sql statement list for adding the new table and its indexes.
        It returns the statement.
        """
        tablechanges = []
        change = self._sqlTable(tbl)
        self.changes.append(change)
        tablechanges.append(change)
        self.bagChanges.setItem('%s.%s' % (tbl.pkg.name, tbl.name), None, changes=change)
        
        changes, bagindexes = self._sqlTableIndexes(tbl)
        self.changes.extend(changes)
        tablechanges.extend(changes)
        
        self.bagChanges['%s.%s.indexes' % (tbl.pkg.name, tbl.name)] = bagindexes
        
        return tablechanges
        
    def _buildView(self, node, sqlschema=None):
        """It prepares the sql statement for adding the new view.
        It returns the statement.
        """
        sql = []
        sql.append(self.sqlView(node, sqlschema=sqlschema))
        return sql
    
    def _buildColumn(self, col):
        """
        Prepares the sql statement for adding the new column to the given table.
        Returns the statement.
        """
        return 'ALTER TABLE %s ADD COLUMN %s' % (col.table.sqlfullname, self._sqlColumn(col))

    def _buildForeignKey(self, o_pkg, o_tbl, o_fld, m_pkg, m_tbl, m_fld, on_up, on_del, init_deferred):
        """
        Prepares the sql statement for adding the new constraint to the given table.
        Returns the statement.
        """
        c_name = 'fk_%s_%s' % (m_tbl, m_fld)
        statement = self.db.adapter.addForeignKeySql(c_name, o_pkg, o_tbl, o_fld, m_pkg, m_tbl, m_fld, on_up, on_del, init_deferred)
        return statement

    def _dropForeignKey(self, referencing_package, referencing_table, referencing_field):
        """
        Prepares the sql statement for dropping the givent constraint from the given table.
        Returns the statement.
        """
        constraint_name = 'fk_%s_%s' % (referencing_table, referencing_field)
        statement = 'ALTER TABLE %s.%s DROP CONSTRAINT %s' % (referencing_package, referencing_table, constraint_name)
        return statement

    def _sqlTable(self, tbl):
        """
        returns the sql statement string that creates the new table
        """        
        tablename = '%s.%s' % (tbl.sqlschema, tbl.sqlname)
        
        sqlfields = []
        for col in tbl.columns.values():
            sqlfields.append(self._sqlColumn(col))
        return 'CREATE TABLE %s (%s);' % (tablename, ', '.join(sqlfields))
    
    def _sqlDatabase(self, tbl):
        """
        returns the sql statement string that creates the new database
        """
        return 'CREATE DATABASE "Dooo"  WITH ENCODING "UNICODE";'
    
    def _sqlTableIndexes(self, tbl):
        """
        returns the list of statements for building table's indexes.
        """
        tablename = tbl.sqlname
        sqlschema=tbl.sqlschema
        pkey = tbl.pkey
        sqlindexes = []
        bagindexes = Bag()
        if tbl.indexes:
            for idx in tbl.indexes.values():
                icols = idx.getAttr('columns')
                icols = ','.join([tbl.column(col.strip()).sqlname for col in icols.split(',')])
                unique = idx.getAttr('unique')
                change = self._buildIndex(tablename, idx.sqlname, icols, sqlschema=sqlschema, unique=unique, pkey=pkey)
                sqlindexes.append(change)
                bagindexes.setItem(idx.sqlname, None, changes=change)
        return (sqlindexes, bagindexes)
    
    def _buildIndex(self, tablename, iname, icols, unique=None, sqlschema=None, pkey=None):
        """
        returns the statement string for creating a table's index
        """
        if icols != pkey:           
            return self.db.adapter.createIndex(iname, columns=icols, table_sql=tablename, sqlschema=sqlschema, unique=unique)

    def _sqlColumn(self, col):
        """
        returns the statement string for creating a table's column
        """
        return self.db.adapter.columnSqlDefinition(sqlname=col.sqlname, 
                                                     dtype=col.dtype, size=col.getAttr('size'), 
                                                     notnull=col.getAttr('notnull', False), 
                                                     pkey=(col.name == col.table.pkey))


if __name__ == '__main__':
    db = GnrSqlDb(implementation='postgres', dbname='pforce',
                 host='localhost', user='postgres', password='postgres',
                 main_schema=None)
    db.importModelFromDb()
    db.saveModel('/Users/fporcari/Desktop/testmodel','py')
    