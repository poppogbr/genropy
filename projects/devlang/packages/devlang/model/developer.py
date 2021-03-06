# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('developer', pkey='id', name_long='!!Developer',
                        name_plural='!!Developers')
        tbl.column('id', size='22', group='_', name_long='Id')
        tbl.column('first_name', size=':30', name_long='!!Firstname', indexed=True, validate_case='c')
        tbl.column('last_name', name_long='!!Lastname', validate_case='c')
        tbl.column('email', name_long='!!Email')
        tbl.column('website', name_long='!!Website')
        tbl.column('address', name_long='!!Full Address')
        tbl.column('country_code', name_long='!!Country code')
        tbl.column('country_name', name_long='!!Country')
        tbl.column('area', name_long='!!State')
        tbl.column('subarea', name_long='!!Sub Area')
        tbl.column('locality', name_long='!!Suburb')
        tbl.column('thoroughfare', name_long='!!Street')
        tbl.column('postal_code', name_long='!!Postcode')
        tbl.column('latlonbox', name_long='!!Lat lon box')
        tbl.column('coordinates', name_long='!!Coordinates')
        tbl.formulaColumn('name_full', "($first_name ||' '|| $last_name)", name_long='!!Full name') # formula
        