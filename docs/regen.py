#!/usr/bin/env python3
'''
    A custom documentation generator because sphinx-apidoc doesn't quite do
    what I want it to. The autosummary thing is really close to what I want.
    However, the documentation for how to use it is lacking.
    
    This is designed to generate docs for our flat import structure in a
    manner that is friendly to the readthedocs theme.
'''

import os
import sys
import inspect
import shutil

from os.path import abspath, join, dirname, exists

import sphinx.apidoc

mod_doc = '''
%(header)s

.. automodule:: %(module)s
    :members:

.. autosummary::
    %(cls_names)s

.. toctree::
    :hidden:
    
    %(cls_files)s

'''

cls_doc = '''
%(header)s

.. automodule:: %(clsmodname)s
    :members:
    :undoc-members:
    :show-inheritance:
    :exclude-members: initTable, getTable, getSmartDashboardType, updateTable, startLiveWindowMode, stopLiveWindowMode, valueChanged
'''

def heading(name, c):
    return '%s\n%s' % (name, c*len(name))


def write_if_changed(fname, contents):
    
    try:
        with open(fname, 'r') as fp:
            old_contents = fp.read()
    except:
        old_contents = ''
        
    if old_contents != contents:
        with open(fname, 'w') as fp:
            fp.write(contents)
    

def gen_package(mod):
    
    # TODO: This might break if there is more than one class per file.. but
    #       since WPILib is emulating java, this probably won't happen... 
    
    name = mod.__name__
    
    docdir = abspath(join(dirname(__file__), name))
    pkgrst = abspath(join(dirname(__file__), '%s.rst' % name))
    
    old_files = {}
    if exists(docdir):
        for fname in os.listdir(docdir):
            old_files[join(docdir, fname)] = True
    else:
        os.mkdir(docdir)
    
    classes = []
    
    for clsname, cls in inspect.getmembers(mod, inspect.isclass):
        # Skip undocumented classes - only stubs will be undocumented.
        if not cls.__doc__:
            continue
        
        fname = join(docdir, '%s.rst' % clsname)
        clsmodname = cls.__module__
        write_if_changed(
            fname, 
            cls_doc % {
                'modname': name,
                'header':  heading(clsname, '-'),
                'clsname': clsname,
                'clsmodname': clsmodname
            })
        
        old_files.pop(fname, None)
        classes.append((clsmodname, clsname))

    classes = sorted(classes)

    # Create toctree
        
    cls_names = ['%s.%s' % (clsmodule, clsname) for clsmodule, clsname in classes]
    cls_files = ['%s/%s' % (name, clsname) for clsmodule, clsname in classes]

    write_if_changed(
        pkgrst,
        mod_doc % {
            'header': heading(name + ' Package', '='),
            'module': name,
            'cls_names': '\n    '.join(cls_names),
            'cls_files': '\n    '.join(cls_files)
        })
        
    old_files.pop(pkgrst, None)
        
    # delete any files that were not written, since this is an autogenerated directory
    for fname in old_files.keys():
        os.unlink(fname)

def main():
    
    sys.path.insert(0, abspath(join(dirname(__file__), '..', 'wpilib')))
    sys.path.insert(0, abspath(join(dirname(__file__), '..', 'hal-base')))
    sys.path.insert(0, abspath(join(dirname(__file__), '..', 'hal-sim')))
    
    import wpilib
    import wpilib.buttons
    import wpilib.command
    import wpilib.interfaces
    
    gen_package(wpilib)
    gen_package(wpilib.buttons)
    gen_package(wpilib.command)
    gen_package(wpilib.interfaces)
    


if __name__ == '__main__':
    main()
