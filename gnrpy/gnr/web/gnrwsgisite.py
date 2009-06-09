from gnr.core.gnrbag import Bag, DirectoryResolver
from gnr.core.gnrlang import gnrImport, getUuid, classMixin, cloneClass
from gnr.core.gnrstring import splitAndStrip
from gnr.web.gnrwebpage import BaseResource
from gnr.web.gnrwsgipage import GnrWsgiPage
from gnr.web.gnrwebreqresp import GnrWebRequest,GnrWebResponse
from beaker.middleware import SessionMiddleware
from paste import fileapp, httpexceptions, request
from paste.httpheaders import ETAG
from weberror.evalexception import EvalException
from webob import Request, Response
from gnr.web.gnrwebapp import GnrWsgiWebApp
import os
from time import time
from threading import RLock
import thread
import mimetypes
#import hashlib
from gnr.core.gnrsys import expandpath

mimetypes.init()

class GnrWebServerError(Exception):
    pass

class GnrWsgiSite(object):
    
    def __call__(self, environ, start_response):
        return self.wsgiapp(environ, start_response)
    
    def __init__(self, script_path, site_name=None, _config=None, _gnrconfig=None):
        self.site_path = os.path.dirname(os.path.abspath(script_path))
        self.site_name = site_name or os.path.basename(self.site_path)
        if _gnrconfig:
            self.gnr_config = _gnrconfig
        else:
            self.gnr_config = self.load_gnr_config()
            self.set_environment()
        if _config:
            self.config = _config
        else:
            self.config = self.load_site_config()
        
        self.home_uri = self.config['wsgi?home_uri'] or '/'
        if self.home_uri[-1]!='/':
            self.home_uri+='/'
        self.mainpackage = self.config['wsgi?mainpackage']
        self.homepage = self.config['wsgi?homepage'] or self.home_uri+'index'
        if not self.homepage.startswith('/'):
            self.homepage = '%s/%s'%(self.home_uri,self.homepage)
        self.secret = self.config['wsgi?secret'] or 'supersecret'
        self.config['secret'] = self.secret
        self.session_key = self.config['wsgi?session_key'] or 'gnrsession'
        self.debug = self.config['wsgi?debug']=='true' or False
        self.cache_max_age = self.config['wsgi?cache_max_age'] or 0
        self.gnrapp = self.build_gnrapp()
        self.wsgiapp = self.build_wsgiapp()
        self.build_automap()
        self.pages_dir = os.path.join(self.site_path, 'pages')
        self.site_static_dir = self.config['resources?site'] or '.'
        if self.site_static_dir and not os.path.isabs(self.site_static_dir):
            self.site_static_dir = os.path.normpath(os.path.join(self.site_path,self.site_static_dir))
        self.find_resources()
        self.find_gnrjs_and_dojo()
        self.page_factories={}
        self.page_factory_lock=RLock()
        
        
    def resource_name_to_path(self,res_id):
        project_resource_path = os.path.join(self.site_path, '..','..','resources',res_id)
        if os.path.isdir(project_resource_path):
            return project_resource_path
        if 'resources' in self.gnr_config['gnr.environment_xml']:
            for path in self.gnr_config['gnr.environment_xml'].digest('resources:#a.path'):
                res_path=expandpath(os.path.join(path,res_id))
                if os.path.isdir(res_path):
                    return res_path
        raise Exception(
            'Error: resource %s not found' % res_id)
    
    def find_gnrjs_and_dojo(self):
        self.dojo_path={}
        self.gnr_path={}
        for lib, path, cdn in self.gnr_config['gnr.environment_xml.static'].digest('js:#k,#a.path,#a.cdn'):
            if lib.startswith('dojo_'):
                self.dojo_path[lib[5:]] = path
            elif lib.startswith('gnr_'):
                self.gnr_path[lib[4:]] = path
    
    
    def find_resources(self):
        self.resources=Bag()
        for resource in self.config['resources']:
            rsrc_path = resource.attr.get('path')
            if rsrc_path:
                self.resources[resource.label] = rsrc_path
            else:
                rsrc_path = self.resource_name_to_path(resource.label)
                self.resources[resource.label] = rsrc_path
        self.resources_dirs = self.resources.values()
        self.resources_dirs.reverse()
        
    def set_environment(self):
        for var,value in self.gnr_config['gnr.environment_xml'].digest('environment:#k,#a.value'):
            var=var.upper()
            if not os.getenv(var):
                os.environ[var]=str(value)
    
    def load_gnr_config(self):
        config_path = expandpath('~/.gnr')
        if os.path.isdir(config_path):
            return Bag(config_path)
        config_path = expandpath(os.path.join('/etc/gnr'))
        if os.path.isdir(config_path):
            return Bag(config_path)
        return Bag()
    

    def load_site_config(self):
        site_config_path = os.path.join(self.site_path,'siteconfig.xml')
        site_config = self.gnr_config['gnr.siteconfig.default_xml']
        for path, site_template in self.gnr_config['gnr.environment_xml'].digest('sites:#a.path,#a.site_template'):
            if path == os.path.dirname(self.site_path):
                if site_config:
                    site_config.update(self.gnr_config['gnr.siteconfig.%s_xml'%site_template] or Bag())
                else:
                    site_config = self.gnr_config['gnr.siteconfig.%s_xml'%site_template]
        if site_config:
            site_config.update(Bag(site_config_path))
        else:
            site_config = Bag(site_config_path)
        return site_config

    def _get_sitemap(self):
        if not hasattr(self,'_sitemap'):
            sitemap_path = os.path.join(self.site_path,'sitemap.xml')
            if not os.path.isfile(sitemap_path):
                sitemap_path = os.path.join(self.site_path,'automap.xml')
            _sitemap = Bag(sitemap_path)
            _sitemap.setBackRef()
            self._sitemap = _sitemap
        return self._sitemap
    sitemap = property(_get_sitemap)
    
    def dispatcher(self,environ,start_response):
        """Main WSGI dispatcher, calls serve_staticfile for static files and self.createWebpage for
         GnrWebPages"""
        t=time()
        req = Request(environ)
        resp = Response()
        path_info = req.path_info
        if path_info==self.home_uri:
            path_info=self.homepage
        if path_info.endswith('.py'):
            path_info = path_info[:-3]
        path_list = path_info.strip('/').split('/')
        path_list = [p for p in path_list if p]
        # if url starts with _ go to static file handling
        page_kwargs=dict(req.params)
        if path_list[0].startswith('_'):
            return self.serve_staticfile(path_list,environ,start_response,**page_kwargs)
        # get the deepest node in the sitemap bag associated with the given url
        page_node,page_args=self.sitemap.getDeepestNode('.'.join(path_list))
        if self.mainpackage and not page_node: # try in the main package
            page_node,page_args=self.sitemap.getDeepestNode('.'.join([self.mainpackage]+path_list))
        if not page_node:
            return self.not_found(environ,start_response)
        page_attr = page_node.getInheritedAttributes()
        if not page_attr.get('path'):
            page_node,page_args=self.sitemap.getDeepestNode('.'.join(path_list+['index']))
        if not page_node:
            return self.not_found(environ,start_response)
        page_attr = page_node.getInheritedAttributes()
        if not page_attr.get('path'):
            return self.not_found(environ,start_response)
        if self.debug:
            page = self.page_create(**page_attr)
        else:
            try:
                page = self.page_create(**page_attr)
            except Exception,exc:
                raise exc
        #page.filepath = page_attr['path'] ### Non usare per favore...
        page.folders= page._get_folders()
        if '_rpc_resultPath' in page_kwargs:
            _rpc_resultPath=page_kwargs.pop('_rpc_resultPath')
        else:
            _rpc_resultPath=None
        if '_user_login' in page_kwargs:
            _user_login=page_kwargs.pop('_user_login')
        else:
            _user_login=None
        if 'page_id' in page_kwargs:
            page_id=page_kwargs.pop('page_id')
        else:
            page_id=None
        if 'debug' in page_kwargs:
            debug=page_kwargs.pop('debug')
        else:
            debug=None
        self.page_init(page,request=req, response=resp, page_id=page_id, debug=debug, 
                            _user_login=_user_login, _rpc_resultPath=_rpc_resultPath)
        if not page:
            return self.not_found(environ,start_response)
        page_method = page_args and page_args[0]
        if page_method and not 'method' in page_kwargs:
            page_kwargs['method'] = page_method
            page_args = page_args[1:]
        theme = getattr(page, 'theme', None) or self.config['dojo?theme'] or 'tundra'
        pagetemplate = getattr(page, 'pagetemplate', None) or self.config['dojo?pagetemplate'] # index
        result = page.index(theme=theme,pagetemplate=pagetemplate,**page_kwargs)
        if isinstance(result, unicode):
            resp.content_type='text/plain'
            resp.unicode_body=result
        elif isinstance(result, basestring):
            resp.body=result
        elif isinstance(result, Response):
            resp=result
        totaltime = time()-t
        resp.headers['X-GnrTime'] = str(totaltime)
        return resp(environ, start_response)
        

    def not_found(self, environ, start_response, debug_message=None):
        exc = httpexceptions.HTTPNotFound(
            'The resource at %s could not be found'
            % request.construct_url(environ),
            comment='SCRIPT_NAME=%r; PATH_INFO=%r; debug: %s'
            % (environ.get('SCRIPT_NAME'), environ.get('PATH_INFO'),
                debug_message or '(none)'))
        return exc.wsgi_application(environ, start_response)
        
    def build_wsgiapp(self):
        """Builds the wsgiapp callable wrapping self.dispatcher with WSGI middlewares """
        wsgiapp=self.dispatcher
        if self.debug:
            wsgiapp = EvalException(wsgiapp, debug=True)
        beaker_path = os.path.join(os.path.dirname(os.path.realpath(self.site_path)),'_data')
        wsgiapp = SessionMiddleware(wsgiapp, key=self.session_key, secret=self.secret, 
                data_dir=beaker_path)
        return wsgiapp
        
    def build_gnrapp(self):
        """Builds the GnrApp associated with this site"""
        instance_path = os.path.join(self.site_path,'instance')
        if os.path.isdir(instance_path):
            self.config.setItem('instances.app',None,path=instance_path)
            return GnrWsgiWebApp(instance_path, site=self)
        instance_path = os.path.join(self.site_path,'..','..','instances',self.site_name)
        if os.path.isdir(instance_path):
            self.config.setItem('instances.app',None,path=instance_path)
            return GnrWsgiWebApp(instance_path,site=self)
        instance_path = self.config['instance?path'] or self.config['instances.#0?path']
        if os.path.isdir(instance_path):
            self.config.setItem('instances.app',None,path=instance_path)
            return GnrWsgiWebApp(instance_path, site=self)
        
    def find_instance(self,instance_name):
        if 'instances' in self.gnr_config['gnr.environment_xml']:
            path_list.extend([expandpath(path) for path in self.gnr_config['gnr.environment_xml'].digest('sites:#a.path') if os.path.isdir(expandpath(path))])
        
    
    def build_automap(self):
        def handleNode(node, pkg=None):
            attr = node.attr
            file_name = attr['file_name']
            node.attr = dict(
                name = '!!%s'%file_name.capitalize(),
                pkg = pkg
                )
            if attr['file_ext']=='py':
                node.attr['path']=attr['rel_path']
            node.label = file_name
            if node._value is None:
                node._value = ''
        self.automap=DirectoryResolver(os.path.join(self.site_path,'pages'),ext='py',include='*.py',exclude='_*,.*,*.pyc')()
        self.automap.walk(handleNode, _mode='', pkg='*')
        for package in self.gnrapp.packages.values():
            packagemap = DirectoryResolver(os.path.join(package.packageFolder, 'webpages'),
                                             include='*.py',exclude='_*,.*')()
            packagemap.walk(handleNode,_mode='',pkg=package.id)
            self.automap[package.id] = packagemap
        self.automap.toXml(os.path.join(self.site_path,'automap.xml'))
    
    def get_page_factory(self, path, pkg = None):
        #if path in self.page_factories:
        #    return self.page_factories[path]
        page_module = gnrImport(path,importAs='%s-%s'%(pkg or 'site',str(path.lstrip('/').replace('/','_')[:-3])))
        page_factory = getattr(page_module,'page_factory',GnrWsgiPage)
        custom_class = getattr(page_module,'GnrCustomWebPage')
        py_requires = splitAndStrip(getattr(custom_class, 'py_requires', '') ,',')
        page_class = cloneClass('GnrCustomWebPage',page_factory)
        page_class.__module__ = page_module
        self.page_class_base_mixin(page_class, pkg=pkg)
        page_class.dojoversion = getattr(custom_class, 'dojoversion', None) or self.config['dojo?version'] or '11'
        page_class.gnrjsversion = getattr(custom_class, 'gnrjsversion', None) or self.config['gnrjs?version'] or '11'
        page_class.maintable = getattr(custom_class, 'maintable', None)
        page_class.eagers = getattr(custom_class, 'eagers', {})
        page_class.css_requires = splitAndStrip(getattr(custom_class, 'css_requires', ''),',')
        page_class.js_requires = splitAndStrip(getattr(custom_class, 'js_requires', ''),',')
        page_class.auth_tags = getattr(custom_class, 'auth_tags', '')
        self.page_class_resourceDirs(page_class, path, pkg=pkg)
        self.page_pyrequires_mixin(page_class, py_requires)
        classMixin(page_class,custom_class)
        self.page_class_resourceDirs(page_class, path, pkg=pkg)
        page_class._packageId = pkg
        self.page_class_custom_mixin(page_class, path, pkg=pkg)
        self.page_factories[path]=page_class
        return page_class

    def page_class_base_mixin(self,page_class,pkg=None):
        """Looks for custom classes in the package"""
        if pkg:
            package = self.gnrapp.packages[pkg]
        if package and package.webPageMixin:
            classMixin(page_class,package.webPageMixin) # first the package standard
        if self.gnrapp.webPageCustom:
            classMixin(page_class,self.gnrapp.webPageCustom) # then the application custom
        if package and package.webPageMixinCustom:
            classMixin(page_class,package.webPageMixinCustom) # finally the package custom

    
    def page_class_custom_mixin(self,page_class, path, pkg=None):
        """Look in the instance custom folder for a file named as the current webpage"""
        path=path.split(os.path.sep)
        if pkg:
            customPagePath=os.path.join(self.gnrapp.customFolder, pkg, 'webpages', *path)
            if os.path.isfile(customPagePath):
                component_page_module = gnrImport(customPagePath)
                component_page_class = getattr(component_page_module,'WebPage',None)
                if component_page_class:
                    classMixin(page_class, component_page_class)
                    
    def page_pyrequires_mixin(self, page_class, py_requires):
        for mix in py_requires:
            if mix:
                self.mixinResource(page_class, page_class._resourceDirs, mix)
    
    def loadResource(self,pkg, *path):
        resourceDirs = self.gnrapp.packages[pkg].resourceDirs
        resource_class = cloneClass('CustomResource',BaseResource)
        self.mixinResource(resource_class, resourceDirs, *path)
        resource_class.site = self
        return resource_class()
        
    def loadTableResource(self, page, table, path):
        application=self.gnrapp
        if isinstance(table, basestring):
            table=application.db.table(table)
        path = os.path.join('tables',table.name,*(path.split('/')))
        resourceDirs = application.packages[table.pkg.name].resourceDirs
        modName, clsName = path.split(':')
        modPathList = self.getResourceList(resourceDirs, modName, 'py') or []
        if modPathList:
            modPathList.reverse()
            resource_module = gnrImport(modPathList.pop(-1))
            resource_class = getattr(resource_module,clsName,None)
            resource_obj = resource_class(page=page,db=application.db, site=self)
            for modPath in modPathList:
                resource_module = gnrImport(modPath)
                resource_class = getattr(resource_module,clsName,None)
                if resource_class:
                    obj.mixin(resource_class)
            if hasattr(resource_obj,'init'):
                resource_obj.init(page)
            return resource_obj
        else:
            raise GnrWebServerError('Cannot import component %s' % modName)
        
    def mixinResource(self, kls,resourceDirs,*path):
        path = os.path.join(*path)
        modName, clsName = path.split(':')
        modPathList = self.getResourceList(resourceDirs, modName, 'py') or []
        if modPathList:
            modPathList.reverse()
            for modPath in modPathList:
                component_module = gnrImport(modPath)
                component_class = getattr(component_module,clsName,None)
                if component_class:
                    classMixin(kls, component_class, site=self)
        else:
            raise GnrWebServerError('Cannot import component %s' % modName)

    def getResourceList(self, resourceDirs, path ,ext=None):
        result=[]
        if ext and not path.endswith('.%s' % ext): path = '%s.%s' % (path, ext)
        for dpath in resourceDirs:
            fpath = os.path.join(dpath, path)
            if os.path.exists(fpath):
                result.append(fpath)
        return result
    def page_create(self,path=None,auth_tags=None,pkg=None,name=None):
        """Given a path returns a GnrWebPage ready to be called"""
        if pkg=='*':
            module_path = os.path.join(self.site_path,path)
            pkg = self.config['packages?default']
        else:
            module_path = os.path.join(self.gnrapp.packages[pkg].packageFolder,'webpages',path)
        try:
            self.page_factory_lock.acquire()
            page_class = self.get_page_factory(module_path, pkg = pkg)
        finally:
            self.page_factory_lock.release()
        page = page_class(self, filepath = module_path, packageId = pkg)
        return page

    def page_init(self,page, request=None, response=None, page_id=None, debug=None, _user_login=None, _rpc_resultPath=None):
        page._rpc_resultPath=_rpc_resultPath
        page.siteFolder = page._sitepath=self.site_path
        page.folders= page._get_folders()
        page._request = request
        page._user_login=_user_login
        if not response: 
            response = Response()
        page._response = response
        page.request = GnrWebRequest(request)
        page.response = GnrWebResponse(response)
        page.response.add_header('Pragma','no-cache')
        page.page_id = page_id or getUuid()
        page._htmlHeaders=[]
        page._cliCtxData = Bag()
        page.pagename = os.path.splitext(os.path.basename(page.filepath))[0].split(os.path.sep)[-1]
        page.pagepath = page.filepath.replace(page.folders['pages'], '')
        page.debug_mode = debug and True or False
        page._dbconnection=None
        
    def page_class_resourceDirs(self,page_class, path, pkg=None):  
        """Find a resource in current _resources folder or in parent folders one"""
        if pkg:
            pagesPath = os.path.join(self.gnrapp.packages[pkg].packageFolder , 'webpages')
        else:
            pagesPath = os.path.join(self.site_path,'pages')
        curdir = os.path.dirname(os.path.join(pagesPath,path))
        resourcePkg = None
        result = [] # result is now empty
        if pkg: # for index page or other pages at root level (out of any package)
            resourcePkg = self.gnrapp.packages[pkg].attributes.get('resourcePkg')
            fpath = os.path.join(self.site_path,'_custom', pkg, '_resources')
            if os.path.isdir(fpath):
                result.append(fpath) # we add a custom resource folder for current package
        fpath = os.path.join(self.site_path, '_resources')

        if os.path.isdir(fpath):
            result.append(fpath) # we add a custom resource folder for common package

        while curdir.startswith(pagesPath):
            fpath = os.path.join(curdir, '_resources')
            if os.path.isdir(fpath):
                result.append(fpath)
            curdir = os.path.dirname(curdir) # we add a resource folder for folder 
                                             # of current page
        if resourcePkg:
            for rp in resourcePkg.split(','):
                fpath = os.path.join(self.gnrapp.packages[rp].packageFolder , 'webpages', '_resources')
                if os.path.isdir(fpath):
                    result.append(fpath)
        #result.extend(self.siteResources)
        resources_list = self.resources_dirs
        result.extend(resources_list)
        page_class.tpldirectories=result+[self.gnr_static_path(page_class.gnrjsversion,'tpl')]
        page_class._resourceDirs = result
        
    def _get_siteResources(self):
        if not hasattr(self,'_siteResources'):
            self._siteResources=[]
            fpath = os.path.join(self.site_static_dir, '_resources')
            if os.path.isdir(fpath):
                self._siteResources.append(fpath) # we add a resource folder for common package
            resources_path = [fpath for fpath in self.resources_dirs if os.path.isdir(fpath)]
            #if os.path.isdir(fpath):
            self._siteResources.extend(resources_path) # we add a resource folder for common package
        return self._siteResources
    siteResources = property(_get_siteResources)
    # so we return a list of any possible resource folder starting from 
    # most customized and ending with most generic ones

    
    def site_static_path(self,*args):
        return os.path.join(self.site_static_dir, *args)

    def site_static_url(self,*args):
        return '%s_site/%s'%(self.home_uri,'/'.join(args))

    def pkg_static_path(self,pkg,*args):
        return os.path.join(self.gnrapp.packages[pkg].packageFolder, *args)

    def pkg_static_url(self,pkg,*args):
        return '%s_pkg/%s/%s'%(self.home_uri,pkg,'/'.join(args))
    
    def rsrc_static_path(self,rsrc,*args):
        return os.path.join(self.resources[rsrc], *args)
    
    def rsrc_static_url(self,rsrc,*args):
        return '%s_rsrc/%s/%s'%(self.home_uri,rsrc,'/'.join(args))
    
    def pages_static_path(self,*args):
        return os.path.join(self.site_path,'pages', *args)
    
    def pages_static_url(self,*args):
        return '%s_pages/%s'%(self.home_uri,'/'.join(args))
    
    def dojo_static_path(self, version,*args):
        return expandpath(os.path.join(self.dojo_path[version], *args))
    
    def dojo_static_url(self, version,*args):
        return '%s_dojo/%s/%s'%(self.home_uri,version,'/'.join(args))
    
    def gnr_static_path(self, version,*args):
        return expandpath(os.path.join(self.gnr_path[version], *args))

    def gnr_static_url(self, version,*args):
        return '%s_gnr/%s/%s'%(self.home_uri,version,'/'.join(args))
        
    def connection_static_path(self,connection_id,page_id,*args):
        return os.path.join(self.site_path,'data','_connections', connection_id, page_id, *args)
        
    def connection_static_url(self, page,*args):
        return '%s_conn/%s/%s/%s'%(self.home_uri,page.connection.connection_id, page.page_id,'/'.join(args))
    ########################### begin static file handling #################################
    
    def serve_staticfile(self,path_list,environ,start_response,download=False,**kwargs):
        handler = getattr(self,'static%s'%path_list[0],None)
        if handler:
            fullpath = handler(path_list)
            if fullpath and not os.path.isabs(fullpath):
                fullpath = os.path.normpath(os.path.join(self.site_path,fullpath))
        else:
            fullpath = None
        if not (fullpath and os.path.exists(fullpath)):
            return self.not_found(environ, start_response)
        if_none_match = environ.get('HTTP_IF_NONE_MATCH')
        if if_none_match:
            mytime = os.stat(fullpath).st_mtime
            if str(mytime) == if_none_match:
                headers = []
                ETAG.update(headers, mytime)
                start_response('304 Not Modified', headers)
                return [''] # empty body
        file_args=dict()
        if download:
            file_args['content_disposition']="attachment; filename=%s" % os.path.basename(fullpath)
        file_responder = fileapp.FileApp(fullpath,**file_args)
        if self.cache_max_age:
            file_responder.cache_control(max_age=self.cache_max_age)
        return file_responder(environ, start_response)
        
    
    def static_dojo(self,path_list):
        return self.dojo_static_path(*path_list[1:])
        
    def static_gnr(self,path_list):
        return self.gnr_static_path(*path_list[1:])
    
    def static_site(self,path_list):
        static_dir = self.config['resources?site'] or '.'
        return os.path.join(static_dir,*path_list[1:])
    
    def static_pages(self,path_list):
        static_dir = self.site_path
        return os.path.join(static_dir,'pages',*path_list[1:])
        
    def static_pkg(self,path_list):
        package_id = path_list[1]
        package = self.gnrapp.packages[package_id]
        if package:
            static_dir = package.packageFolder
            return os.path.join(static_dir,'webpages',*path_list[2:])
            
    def static_rsrc(self,path_list):
        resource_id = path_list[1]
        resource_path = self.resources.get(resource_id)
        if resource_path:
            return os.path.join(resource_path, *path_list[2:])
            
    def static_conn(self, path_list):
        connection_id, page_id = path_list[1],path_list[2]
        return self.connection_static_path(connection_id, page_id,*path_list[3:])
    ##################### end static file handling #################################
