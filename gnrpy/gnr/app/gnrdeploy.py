import os
import glob
from gnr.core.gnrbag import Bag
from gnr.core.gnrsys import expandpath

class PathResolver(object):
    """add???"""
    entities = dict(
            instance='instances',
            site='sites',
            resource='resources',
            package='packages',
            project='projects')
            
    def __init__(self, gnr_config=None):
        self.gnr_config = gnr_config or self.load_gnr_config()
        
    def load_gnr_config(self):
        """add???
        
        :returns: add???
        """
        home_config_path = expandpath('~/.gnr')
        global_config_path = expandpath(os.path.join('/etc/gnr'))
        if os.path.isdir(home_config_path):
            config = Bag(home_config_path)
        elif os.path.isdir(global_config_path):
            config = Bag(global_config_path)
        else:
            config = Bag()
        self.set_environment(config)
        return config
        
    def set_environment(self, config):
        """add???
        
        :param config: add???
        :returns: add???
        """
        for var, value in config['gnr.environment_xml'].digest('environment:#k,#a.value'):
            var = var.upper()
            if not os.getenv(var):
                os.environ[var] = str(value)
                
    def js_path(self, lib_type='gnr', version='11'):
        """add???
        
        :param lib_type: add???. Default value is ``gnr``
        :param version: add???. Default value is ``11``
        :returns: add???
        """
        path = self.gnr_config['gnr.environment_xml.static.js.%s_%s?path' % (lib_type, version)]
        if path:
            path = os.path.join(expandpath(path), 'js')
        return path
        
    def entity_name_to_path(self, entity_name, entity_type, look_in_projects=True):
        """add???
        
        :param entity_name: add???
        :param entity_type: add???
        :param look_in_projects: add???. Default value is ``True``
        :returns: add???
        """
        entity = self.entities.get(entity_type)
        if not entity:
            raise Exception('Error: entity type %s not known' % entity_type)
        if entity in self.gnr_config['gnr.environment_xml']:
            for path in [expandpath(path) for path in
                         self.gnr_config['gnr.environment_xml'].digest('%s:#a.path' % entity) if
                         os.path.isdir(expandpath(path))]:
                entity_path = os.path.join(path, entity_name)
                if os.path.isdir(entity_path):
                    return expandpath(entity_path)
        if look_in_projects and 'projects' in self.gnr_config['gnr.environment_xml']:
            projects = [expandpath(path) for path in self.gnr_config['gnr.environment_xml'].digest('projects:#a.path')
                        if os.path.isdir(expandpath(path))]
            for project_path in projects:
                for path in glob.glob(os.path.join(project_path, '*/%s' % entity)):
                    entity_path = os.path.join(path, entity_name)
                    if os.path.isdir(entity_path):
                        return expandpath(entity_path)
        raise Exception('Error: %s %s not found' % (entity_type, entity_name))
        
    def site_name_to_path(self, site_name):
        """add???
        
        :param site_name: add???
        :returns: add???
        """
        return self.entity_name_to_path(site_name, 'site')
        
    def instance_name_to_path(self, instance_name):
        """add???
        
        :param instance_name: add???
        :returns: add???
        """
        return self.entity_name_to_path(instance_name, 'instance')
        
    def package_name_to_path(self, package_name):
        """add???
        
        :param package_name: add???
        :returns: add???
        """
        return self.entity_name_to_path(package_name, 'package')
        
    def resource_name_to_path(self, resource_name):
        """add???
        
        :param resource_name: add???
        :returns: add???
        """
        return self.entity_name_to_path(resource_name, 'resource')
        
    def project_name_to_path(self, project_name):
        """add???
        
        :param project_name: add???
        :returns: add???
        """
        return self.entity_name_to_path(project_name, 'project', look_in_projects=False)
        
    def project_repository_name_to_path(self, project_repository_name, strict=True):
        """add???
        
        :param project_repository_name: add???
        :param strict: add???. Default value is ``True``
        :returns: add???
        """
        if not strict or 'gnr.environment_xml.projects.%s' % project_repository_name in self.gnr_config:
            path = self.gnr_config['gnr.environment_xml.projects.%s?path' % project_repository_name]
            if path:
                return expandpath(path)
        else:
            raise Exception('Error: Project Repository %s not found' % project_repository_name)
            
class ProjectMaker(object):
    """add???"""
    def __init__(self, project_name, base_path=None):
        self.project_name = project_name
        self.base_path = base_path or '.'
        
    def do(self):
        """add???"""
        self.project_path = os.path.join(self.base_path, self.project_name)
        self.packages_path = os.path.join(self.project_path, 'packages')
        self.sites_path = os.path.join(self.project_path, 'sites')
        self.instances_path = os.path.join(self.project_path, 'instances')
        self.resources_path = os.path.join(self.project_path, 'resources')
        for path in (self.project_path, self.packages_path, self.sites_path, self.instances_path, self.resources_path):
            if not os.path.isdir(path):
                os.mkdir(path)
                
class SiteMaker(object):
    """Handle the autocreation of the ``sites`` folder. To autocreate the ``sites`` folder, please type in your console::
        
        gnrmksite sitesname
        
    where ``sitesname`` is the name of your ``sites`` folder.
    """
    def __init__(self, site_name, base_path=None, resources=None, instance=None, dojo_version='11',
                 wsgi_port=None, wsgi_reload=None, wsgi_mainpackage=None, wsgi_debug=None, config=None):
        self.site_name = site_name
        self.base_path = base_path or '.'
        self.resources = resources or []
        self.instance = instance
        self.wsgi_port = wsgi_port
        self.wsgi_reload = wsgi_reload
        self.wsgi_mainpackage = wsgi_mainpackage
        self.wsgi_debug = wsgi_debug
        self.dojo_version = dojo_version
        self.config = config
        
    def do(self):
        """add???"""
        self.site_path = os.path.join(self.base_path, self.site_name)
        pages_path = os.path.join(self.site_path, 'pages')
        root_py_path = os.path.join(self.site_path, 'root.py')
        siteconfig_xml_path = os.path.join(self.site_path, 'siteconfig.xml')
        if not os.path.isdir(self.site_path):
            os.mkdir(self.site_path)
        if not os.path.isdir(pages_path):
            os.mkdir(pages_path)
        if not os.path.isfile(root_py_path):
            root_py = open(root_py_path, 'w')
            root_py.write("""#!/usr/bin/env python2.6
import sys
sys.stdout = sys.stderr
from gnr.web.gnrwsgisite import GnrWsgiSite
site = GnrWsgiSite(__file__)

def application(environ,start_response):
    return site(environ,start_response)

if __name__ == '__main__':
    from gnr.web.server import NewServer
    server=NewServer(__file__)
    server.run()""")
            root_py.close()
        if not os.path.isfile(siteconfig_xml_path):
            if not self.config:
                siteconfig = Bag()
                if self.instance:
                    siteconfig.setItem('instances.%s' % self.instance, None)
                for resource in self.resources:
                    if isinstance(resource, tuple) or isinstance(resource, list):
                        resource, resource_path = resource
                        siteconfig.setItem('resources.%s' % resource, None, path=resource_path)
                    else:
                        siteconfig.setItem('resources.%s' % resource, None)
                wsgi_options = dict()
                for option in ('reload', 'debug', 'port', 'mainpackage'):
                    value = getattr(self, 'wsgi_%s' % option, None)
                    if value:
                        wsgi_options[option] = value
                siteconfig.setItem('wsgi', None, **wsgi_options)
                siteconfig['connection_timeout'] = None
                siteconfig['connection_refresh'] = None
                siteconfig.setItem('dojo', None, version=self.dojo_version)
            else:
                siteconfig = self.config
            siteconfig.toXml(siteconfig_xml_path)

class InstanceMaker(object):
    """Handle the autocreation of the ``instances`` folder. To autocreate the ``instances`` folder, please type in your console::
        
        gnrmkinstance instancesname
        
    where ``instancesname`` is the name of your ``instances`` folder.
    """
    def __init__(self, instance_name, base_path=None, packages=None, authentication=True, authentication_pkg=None,
                 db_dbname=None, db_implementation=None, db_host=None, db_port=None,
                 db_user=None, db_password=None, use_dbstores=False, config=None):
        self.instance_name = instance_name
        self.base_path = base_path or '.'
        self.packages = packages or []
        self.db_dbname = db_dbname
        self.authentication = authentication
        if self.authentication:
            self.authentication_pkg = authentication_pkg
            if not self.authentication_pkg and self.packages:
                package = self.packages[0]
                if isinstance(package, tuple) or isinstance(package, list):
                    package = package[0]
                self.authentication_pkg = package
            if not self.authentication_pkg:
                self.authentication_pkg = 'adm'
        self.db_implementation = db_implementation
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.use_dbstores = use_dbstores
        self.config = config
        
    def do(self):
        """add???"""
        self.instance_path = os.path.join(self.base_path, self.instance_name)
        custom_path = os.path.join(self.instance_path, 'custom')
        data_path = os.path.join(self.instance_path, 'data')
        instanceconfig_xml_path = os.path.join(self.instance_path, 'instanceconfig.xml')
        folders_to_make = [self.instance_path, custom_path, data_path]
        if self.use_dbstores:
            dbstores_path = os.path.join(self.instance_path, 'dbstores')
            folders_to_make.append(dbstores_path)
        for path in folders_to_make:
            if not os.path.isdir(path):
                os.mkdir(path)
        if not os.path.isfile(instanceconfig_xml_path):
            if not self.config:
                instanceconfig = Bag()
                instanceconfig.setItem('packages', None)
                for package in self.packages:
                    if isinstance(package, tuple) or isinstance(package, list):
                        package, package_path = package
                        instanceconfig.setItem('packages.%s' % package, None, path=package_path)
                    else:
                        instanceconfig.setItem('packages.%s' % package, None)
                db_options = dict()
                for option in ('dbname', 'implementation', 'host', 'port', 'username', 'password'):
                    value = getattr(self, 'db_%s' % option, None)
                    if value:
                        db_options[option] = value
                instanceconfig.setItem('db', None, **db_options)
                if self.authentication:
                    instanceconfig.setItem('authentication', None, pkg=self.authentication_pkg)
                    instanceconfig.setItem('authentication.py_auth', None, defaultTags="user", pkg="adm",
                                           method="authenticate")
            else:
                instanceconfig = self.config
            instanceconfig.toXml(instanceconfig_xml_path)
            
class PackageMaker(object):
    """Handle the autocreation of the ``packages`` folder. To autocreate the ``packages`` folder, please type in your console::
        
        gnrmkpackage packagesname
        
    where ``packagesname`` is the name of your ``packages`` folder.
    """
    def __init__(self, package_name, base_path=None, sqlschema=None,
                 name_short=None, name_long=None, name_full=None,
                 login_url=None, comment=None):
        self.package_name = package_name
        self.base_path = base_path or '.'
        self.name_short = name_short or self.package_name.capitalize()
        self.name_full = name_full or self.package_name.capitalize()
        self.name_long = name_long or self.package_name.capitalize()
        self.sqlschema = sqlschema or self.package_name.lower()
        self.comment = comment or '%s package' % self.package_name
        self.login_url = login_url or '%s/login' % self.package_name
        
    def do(self):
        """add???"""
        self.package_path = os.path.join(self.base_path, self.package_name)
        self.model_path = os.path.join(self.package_path, 'model')
        self.lib_path = os.path.join(self.package_path, 'lib')
        self.webpages_path = os.path.join(self.package_path, 'webpages')
        self.resources_path = os.path.join(self.webpages_path, '_resources')
        self.main_py_path = os.path.join(self.package_path, 'main.py')
        self.menu_xml_path = os.path.join(self.package_path, 'menu.xml')
        self.examplemodel_py_example_path = os.path.join(self.model_path, 'example_table.py')
        self.examplewebpage_py_example_path = os.path.join(self.webpages_path, 'example_webpage.py')
        for path in (self.package_path, self.model_path, self.lib_path, self.webpages_path, self.resources_path):
            if not os.path.isdir(path):
                os.mkdir(path)
        if not os.path.exists(self.menu_xml_path):
            menu_xml = open(self.menu_xml_path, 'w')
            menu_xml.write("""<?xml version="1.0" encoding="UTF-8"?>
<GenRoBag>
</GenRoBag>
""")
            menu_xml.close()
        if not os.path.exists(self.main_py_path):
            main_py_options = dict(comment=self.comment, sqlschema=self.sqlschema, name_short=self.name_short,
                                   name_long=self.name_long, name_full=self.name_full, login_url=self.login_url)
            main_py = open(self.main_py_path, 'w')
            main_py.write("""#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='%(comment)s',sqlschema='%(sqlschema)s',
                name_short='%(name_short)s', name_long='%(name_long)s', name_full='%(name_full)s')
                
    def config_db(self, pkg):
        pass
        
    def loginUrl(self):
        return '%(login_url)s'
        
class Table(GnrDboTable):
    pass
""" % main_py_options)
            main_py.close()
        if not os.path.exists(self.examplemodel_py_example_path):
            examplemodel_py_example = open(self.examplemodel_py_example_path, 'w')
            examplemodel_py_example.write("""# encoding: utf-8

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('example', rowcaption='hello_code')
        tbl.column('hello_code',size='4',name_long='!!Hello code') # char(4)
        tbl.column('hello_value',size=':40',name_long='!!Hello value') # varchar(40)
        tbl.column('hello_date',dtype='D',name_long='!!Hello date') # date
        
        # dtype -> sql
        #   C       char (can be omitted; you have to specify its size)
        #   D       date
        #   DH      datetime
        #   H       time
        #   I       integer
        #   L       long integer
        #   R       float
        #   T       text (can be omitted; you must not specify its size)
        #   X       XML/Bag""")
            examplemodel_py_example.close()
        if not os.path.exists(self.examplewebpage_py_example_path):
            examplewebpage_py_example = open(self.examplewebpage_py_example_path, 'w')
            examplewebpage_py_example.write("""# -*- coding: UTF-8 -*-
            
class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        pass""")
            examplewebpage_py_example.close()
            
class ResourceMaker(object):
    """add???"""
    def __init__(self, resource_name, base_path=None):
        """add???
        
        :param resource_name: add???
        :param base_path: add???. Default value is ``None``
        """
        self.resource_name = resource_name
        self.base_path = base_path or '.'
        
    def do(self):
        """add???"""
        self.resource_path = os.path.join(self.base_path, self.resource_name)
        for path in (self.resource_path, ):
            if not os.path.isdir(path):
                os.mkdir(path)
                
class ModWsgiMaker(object):
    """add???"""
    pass
        
if __name__ == '__main__':
    pather = PathResolver()
    print pather.package_name_to_path('edicon')
    print pather.project_name_to_path('trasporti')
    print pather.instance_name_to_path('satlow')
    print pather.site_name_to_path('moscati')