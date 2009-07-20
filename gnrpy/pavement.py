from __future__ import with_statement
import urllib2
import tarfile
import os
import hashlib
from paver.easy import *
from paver.setuputils import setup, find_packages
from setuptools.command import *
DOJO_VERSION='11'
DOJO_URL_BASE='http://www.softwell.it/dojo/'
DOJO_MD5={'11':'0076080b78a91ade5c365aedaf1c0a4c'}

data_files = []


#options(
#    setup=Bunch(
#        name='genropy',
#        version='0.7',
#        author='Softwell S.a.s.',
#        url='http://www.genropy.org/',
#        author_email='info@genropy.org',
#        license='LGPL',
#        scripts=['scripts/gnrdbsetup','scripts/gnrmkinstance','scripts/gnrmkpackage','scripts/gnrmksite','scripts/gnrwsgiserve',
#                'scripts/gnrsendmail','scripts/gnrsitelocalize','scripts/gnrtrdeamon','scripts/rmltester','scripts/gnrsync4d'],
#        packages=['gnr', 'gnr.core', 'gnr.app','gnr.web', 'gnr.sql'],
#        package_dir={'gnr': 'gnrpy/gnr'},
#        data_files=data_files,
#        install_requires = ['paste','beaker','mako','webob','dateutil','simplejson',],
#        zip_safe=False,
#        extras_require = dict(
#            pdf = ['z3c.rml'],
#            postgres = ['psycopg'],
#            pg8000 = ['pg8000'],
#            sqlite = ['pysqlite']
#            )
#        )
#)
setup(
        name='gnrpy',
        version='0.7',
        author='Softwell S.a.s.',
        url='http://www.genropy.org/',
        author_email='info@genropy.org',
        license='LGPL',
        scripts=['../scripts/gnrdbsetup','../scripts/gnrmkinstance','../scripts/gnrmkpackage','../scripts/gnrmksite','../scripts/gnrwsgiserve',
                '../scripts/gnrsendmail','../scripts/gnrsitelocalize','../scripts/gnrtrdeamon','../scripts/rmltester','../scripts/gnrsync4d',
                '../scripts/wk2pdf'],
        packages=['gnr', 'gnr.core', 'gnr.app','gnr.web', 'gnr.sql'],
        #packages=find_packages(exclude=['ez_setup', 'examples', 'packages']),
        #package_dir={'gnr': 'gnrpy/gnr'},
        #namespace_packages=['gnr'],
        data_files=data_files,
        install_requires = ['paste','beaker','mako','webob','weberror','vobject','pytz','babel',],
        zip_safe=False,
        extras_require = dict(
            pdf = ['z3c.rml'],
            postgres = ['psycopg2'],
            pg8000 = ['pg8000'],
            sqlite = ['pysqlite']
            )
        )


def isToImport(fname):
    name, ext = os.path.splitext(fname)
    if name.startswith('.'):
        return False
    if ext not in ('.pyc',):
        return True
        
def getAllFiles(path, installPath):
    data_files = []
    for dirpath, dirnames, filenames in os.walk(path):
        # Ignore dirnames that start with '.'
        for i, dirname in enumerate(dirnames):
            if dirname.startswith('.'): del dirnames[i]
        data_files.append([os.path.join(installPath, dirpath.replace(path,'')), [os.path.join(dirpath, f) for f in filenames if isToImport(f)]])
    return data_files

@task
def dojo():
    filename='dojo_%s.tgz'%DOJO_VERSION
    get_dojo=True
    if os.path.isfile(filename):
        with open(filename,'rb') as dojo_file:
            if hashlib.md5(dojo_file.read()).hexdigest()==DOJO_MD5.get(DOJO_VERSION):
                get_dojo=False
    if get_dojo:
        with open(filename,'wb') as dojo_file:
            url=DOJO_URL_BASE+DOJO_VERSION
            dojo_file.write(urllib2.urlopen(DOJO_URL_BASE+filename).read())
        dojo_tgz = tarfile.open(filename,'r|*')
        dojo_tgz.extractall()
    
@task
def install_dojo():
    data_files.extend(getAllFiles('dojo_%s/'%DOJO_VERSION,'lib/dojo_%s/'%DOJO_VERSION))
    
@task
@cmdopts([('gnrhome=', 'i', 'Genro home path')])
@needs(['dojo', 'install_dojo'])
def install_genro():
    try:
        import _gnrhome
        genro_path=_gnrhome.PATH
        with open(os.path.join('gnrpy','gnr','core','gnrhome.py'),'w') as genrohomefile:
            genrohomefile.write('PATH="%s"\n'%genro_path)
    except:
        genro_path='/usr/local/genro'
    data_files.extend(getAllFiles('gnrjs/',os.path.join(genro_path,'lib/gnrjs/')))
    data_files.extend(getAllFiles('gnrpy/packages/',os.path.join(genro_path,'packages/')))
    data_files.extend(getAllFiles('bin/',os.path.join(genro_path,'bin/')))
    data_files.append([os.path.join(genro_path,'data/sites'),['README.txt']])
    data_files.append([os.path.join(genro_path,'data/instances'),['README.txt']])

@task
@cmdopts([('gnrhome=', 'i', 'Genro home path')])
def configure():
    if options.configure.has_key('gnrhome') and options.configure.gnrhome:
        genro_path=options.configure.gnrhome
        with open('_gnrhome.py','w') as genrohomefile:
            genrohomefile.write('PATH="%s"\n'%genro_path)

@task
def install():
    call_task('setuptools.command.install')
    
@task
@needs(['generate_setup', 'setuptools.command.develop'])
def develop(options):
    pass

@task
@needs(['generate_setup', 'setuptools.command.sdist'])
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass    

