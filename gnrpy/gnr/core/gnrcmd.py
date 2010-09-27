#!/usr/bin/env python
# encoding: utf-8
"""
==========================================================
 A subframework to write command-line utilities for Genro.
==========================================================

Available functionality:
    - :class:`ProgressBar`, a class to draw text-based progressbars. see test_ProgressBar().
    - :class:`AutoDiscovery`, a class to auto-detect current instance, site, package and
      project from ``GENROPY_xxx`` environment variables and/or the current working
      directory.

Future plans:
    - GnrCommand, base class for command-line utilities, will provide parameters
      and options auto-discovery (much like Michele Simionato's plac).
    - ``gnr`` utility, a single entry point for all command-line utilities so we don't
      clutter ``/usr/local/bin`` with many scripts::
    
            Three scripts for the genro-kings under softwell sky,
            Seven for goodsoftware-lords in their halls of stone,
            Nine for mortal customers with money they will buy,
            One for the Dark Lord Gio on his dark throne,
            In the Land of GenroPy where the Commands lie.
            One Script to rule them all, One Script to find them,
            One Script to bring them all and in the darkness bind them
            In the Land of GenroPy where the Commands lie.
"""

from __future__ import with_statement

import math
import sys
from os import environ, getcwd, listdir
from os.path import normpath, splitext, expanduser, expandvars, \
                    isdir, isfile, basename
from os.path import join as path_join
import logging

from gnr.core.gnrbag import Bag

########################################################################

log = logging.getLogger('gnrcmd')

def expandpath(path, full=False):
    """Expand user home directory (~) and envioronment variables.
    
    :param full: if True, returns a normalized path (see os.path.normpath).    
    """
    result = expanduser(expandvars(path))
    if full:
        result = normpath(result)
    return result

########################################################################
class AutoDiscovery(object):
    """Try to guess the current project, package, site and instance.
    
    Environment variables:
    
    .. envvar:: GENROPY_PROJECT

        The name of the current project.

    .. envvar:: GENROPY_INSTANCE

        The name of the current instance.
    
    .. envvar:: GENROPY_SITE

        The name of the current site.
    
    .. envvar:: GENROPY_PACKAGE

        The name of the current package.

    We apply these rules:
    
        1. look in the environment for a :envvar:`GENROPY_PROJECT`, :envvar:`GENROPY_SITE`,
           :envvar:`GENROPY_INSTANCE` and :envvar:`GENROPY_PACKAGE` variables. If any are present,
           we cross-check that they point to the right places by looking at the
           declared places in the configuration (.gnr/environment.xml) and
           complain if they don't.

        2. if :envvar:`GENROPY_PROJECT` is missing, we look if the current path is inside
           one of the declared projects in the configuration. If yes, we assume
           that is the current project. If no, we don't have a current project.

        3. if :envvar:`GENROPY_INSTANCE` is missing, we look if the current path is inside
           one of the instances of the current project or if we are inside one
           of the declared instances in the configuration. If yes, we assume
           that is the current instance. If no, we don't have a current instance.

        4. if :envvar:`GENROPY_SITE` is missing... (same as the previous step)

        5. if :envvar:`GENROPY_PACKAGE` is missing... (same as the previous step)

        6. If we have a project, but we don't have an instance/site/package
           -and- the project has only one instance/site/package, then we
           assume that's the current one.
    
    Attributes:
    
    .. attribute:: current_project
    
        the current project, if found
    
    .. attribute:: current_package
    
        the current package, if found
    
    .. attribute:: current_instance
    
        the current instance, if found
    
    .. attribute:: current_site
    
        the current site, if found
    
    .. attribute:: project_packages
    
        all packages in the current project, if a project has been found
    
    .. attribute:: project_instances
    
        all instances in the current project, if a project has been found
    
    .. attribute:: project_sites
    
        all sites in the current project, if a project has been found
        
    .. attribute:: project_commands
    
        all commands in the current project, if a project has been found
    
    .. attribute:: all_projects
    
        all projects in this GenroPy installation
        
    .. attribute:: all_instances
    
        all instances in this GenroPy installation
    
    .. attribute:: all_packages
    
        all packages in this GenroPy installation
    
    .. attribute:: all_sites
    
        all sites in this GenroPy installation
    
    .. attribute:: all_commands
    
        all commands in this GenroPy installation
    
    .. attribute:: config_file
    
        path to the configuration file (e.g. ``~/gnr/environment.xml``)
    
    """

    def __init__(self, config_file='~/.gnr/environment.xml'):
        """Constructor.
        """
        self.current_project = None
        self.current_package = None
        self.current_instance = None
        self.current_site = None
        
        self.project_packages = None
        self.project_instances = None
        self.project_sites = None
        self.project_commands = None
        
        self.all_projects = {}
        self.all_packages = {}
        self.all_instances = {}
        self.all_sites = {}
        self.all_commands = {}
        
        self.config_file=config_file
        
        self._load_configuration()
        self._auto_discovery()
    
    def report(self, all=False):
        """Print a summary of what AutoDiscovery found.

        If ``all`` is False, it will print only the current project, instance, packages and site.
        If ``all`` is True, will print a full report including all available items in this GenroPy installation.
        """
        print "Current Project:", repr(self.current_project)
        print "Current Instance:", repr(self.current_instance)
        print "Current Package:", repr(self.current_package)
        print "Current Site:", repr(self.current_site)
        
        if all:
            print "Projects:"
            for p in self.all_projects.values():
                print "  ", repr(p)
            print "Instances:"
            for i in self.all_instances.values():
                print "  ", repr(i)
        
        
    def _load_configuration(self):
        """Load GenroPy configuration"""
        cfg = Bag(expanduser(self.config_file))

        def get_section(section_name, attr_name='path'):
            if cfg[section_name]:
                for k,v in cfg[section_name].digest('#k,#a.' + attr_name):
                    yield k, expandpath(v)
        
        # Change os.environ, so expandvars() will expand our vars too
        for k,v in get_section('environment', attr_name='value'):
            environ[k.upper()] = v

        for name, path in get_section('projects'):
            for p_name, p in AutoDiscovery.Project.all(path):
                self.all_projects[p_name] = p
                self.all_packages.update(p.packages())
                self.all_instances.update(p.instances())
                self.all_sites.update(p.sites())
                self.all_commands.update(p.commands())
        
        for name, path in get_section('instances'):
            self.all_instances.update(AutoDiscovery.Instance.all(path))
        
        for name, path in get_section('sites'):
            self.all_sites.update(AutoDiscovery.Site.all(path))
        
        for name, path in get_section('commands'):
            self.all_commands.update(AutoDiscovery.Command.all(path))
        
        for name, path in get_section('packages'):
            self.all_packages.update(AutoDiscovery.Package.all(path))
            
    
    def _auto_discovery(self):
        """Guess current project, package, instance and site."""
        self.current_project = self._guess_current('PROJECT',self.all_projects)
        if self.current_project:
            self.project_instances = dict(self.current_project.instances())
            self.project_packages = dict(self.current_project.packages())
            self.project_sites = dict(self.current_project.sites())
            self.project_commands = dict(self.current_project.commands())
        self.current_instance = self._guess_current('INSTANCE',self.all_instances, self.project_instances)
        self.current_package = self._guess_current('PACKAGE', self.all_packages, self.project_packages)
        self.current_site = self._guess_current('SITE', self.all_sites, self.project_sites)
    
    def _guess_current(self, name, all_items, project_items=None):
        """Guess the current PROJECT/INSTANCE/PACKAGE/SITE"""
        current_name = environ.get(name, None)
        if current_name and (current_name in all_items):
            if project_items and (current_name not in project_items):
                self.warn("current %s (from environment) is not in the current project" % name)
            return all_items[current_name]
        current_path = normpath(getcwd())
        if project_items:
            for item in project_items.itervalues():
                if current_path.startswith(item.path):
                    return item
        if all_items:
            for item in all_items.itervalues():
                if current_path.startswith(item.path):
                    if project_items:
                        self.warn("current %s (from working directory) is not in the current project" % name)
                    return item
        if project_items and len(project_items) == 1:
            self.warn("project has just one %s, assuming it's the current one" % name)
            return project_items.values()[0]
    
    def warn(self, msg):
        global log
        log.warn(msg)
    
    class Item(object):
        """
        :class:`AutoDiscovery`'s attributes contain instances of this class and its subclasses.
        
        They have the following public attributes:
        
        .. attribute:: name
        
            the name of this item
        
        .. attribute:: path
        
            the absolute path to this item
        """
        def __init__(self, path):
            self.path = expandpath(path, full=True)
            self.name = basename(path)
        
        def _is_valid(self):
            """Returns if this is a valid item.
            Subclasses override it."""
            return True
        
        def __repr__(self):
            return "<%s %s in %s>" % (self.__class__.__name__, repr(self.name), repr(self.path))
        
        @classmethod
        def all(cls, base_path):
            if isdir(base_path):
                for name in listdir(base_path):
                    if name.startswith('.'): continue
                    path = path_join(base_path, name)
                    item = cls(path)
                    if item._is_valid():
                        yield item.name, item
        
    class Project(Item):
        """
        Project have these additional methods:
        """
        
        common_project_dirs = 'instances sites packages commands'.split()
        def _is_valid(self):
            return any([isdir(path_join(self.path,d)) for d in self.common_project_dirs])
    
        def instances(self):
            """all instances in this project"""
            return AutoDiscovery.Instance.all(path_join(self.path,'instances'))
        
        def sites(self):
            """all sites in this project"""
            return AutoDiscovery.Site.all(path_join(self.path,'sites'))
        
        def commands(self):
            """all commands in this project"""
            return AutoDiscovery.Command.all(path_join(self.path,'commands'))
        
        def packages(self):
            """all packages in this project"""
            return AutoDiscovery.Package.all(path_join(self.path,'packages'))
    
    class Instance(Item):
        def _is_valid(self):
            return isfile(path_join(self.path,'instanceconfig.xml'))
    
    class Site(Item):
        def _is_valid(self):
            return isfile(path_join(self.path,'siteconfig.xml')) and \
                   isfile(path_join(self.path,'root.py'))
    
    class Command(Item):
        def __init__(self, path):
            AutoDiscovery.Item.__init__(self, path)
            self.name = splitext(self.name)[0] #remove extension
            
        def _is_valid(self):
            p = path_join(self.path)
            return isfile(p)
        
    class Package(Item):
        common_package_dirs = 'models webpages'.split()
        def _is_valid(self):
            return any([isdir(path_join(self.path,d)) for d in self.common_package_dirs])

def test_AutoDiscovery():
    ad = AutoDiscovery()
    ad.report(all=True)        


########################################################################
class GnrCommand(object):
    """Base class for Genro commands.
    
    NOT YET COMPLETE. DO NOT USE.
    """

    def __init__(self, auto_discovery=None):
        """Constructor"""
        self.auto_discovery = auto_discovery or AutoDiscovery()
    
    def main(self):
        """main entry point."""
        raise NotImplementedError, "Subclasses should override main()."            
    
########################################################################
class ProgressBar(object):
    """Provides a text-based progress bar.
    
    Example::
    
        import time
        with ProgressBar('ProgressBar test') as pg:
            for n in xrange(333):
                time.sleep(0.01)
                pg.update(n/3.33)
                if n > 233:
                    raise Exception, "Something bad happened."
    """

    def __init__(self, label, label_width=20, bar_width=40,
                 min_value=0, max_value=100, fd=sys.stdout, progress_label=''):
        """Constructor"""
        self.label = label
        self.min_value = min_value
        self.max_value = max_value
        self.label_width = label_width
        self.bar_width = bar_width
        self.progress_label = progress_label
        self.progress_value = min_value
        self.fd = fd
        print >> self.fd, self.label, "...",
        self.update(self.min_value)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.update(self.max_value)
            print >> self.fd, "done."
        else:
            print >> self.fd, "ERROR (%s%s)" % (self.progress_label, str(self.progress_value))
        
    def update(self, value, progress_value=None):
        """Draws the progress bar.

        Here's how it looks::
        
            Label padded to length     [**********----------------------]  45.12%
        """
        self.progress_value = progress_value or value
        progress = float(value - self.min_value) / float(self.max_value - self.min_value)
        occupied_bar_chars = int(math.floor(self.bar_width * progress))
        occupied_bar = "*" * occupied_bar_chars
        free_bar = "-" * (self.bar_width - occupied_bar_chars)
        print >> self.fd, "\r%*s [%s%s] % 5.2f%%" % (self.label_width, self.label, occupied_bar, free_bar, progress * 100.0),
        self.fd.flush()

def test_ProgressBar(testError=False):
    import time
    with ProgressBar('ProgressBar test') as pg:
        for n in xrange(333):
            time.sleep(0.01)
            pg.update(n/3.33)
            if testError and (n > 233):
                raise Exception, "Something bad happened."

if __name__ == '__main__':
    # test_ProgressBar()
    test_AutoDiscovery()