#!/usr/bin/env python

import os, glob, shutil
from distutils.core import setup
from foobnix.util.configuration import VERSION, FOOBNIX_TMP, FOOBNIX_TMP_RADIO

if not os.path.exists(FOOBNIX_TMP):
    os.mkdir(FOOBNIX_TMP)
    os.mkdir(FOOBNIX_TMP_RADIO)

def capture(cmd):
    return os.popen(cmd).read().strip()

def removeall(path):
    if not os.path.isdir(path):
        return

    files = os.listdir(path)

    for x in files:
        fullpath = os.path.join(path, x)
        if os.path.isfile(fullpath):
            f = os.remove
            rmgeneric(fullpath, f)
        elif os.path.isdir(fullpath):
            removeall(fullpath)
            f = os.rmdir
            rmgeneric(fullpath, f)

def rmgeneric(path, __func__):
    try:
        __func__(path)
    except OSError, (errno, strerror):
        pass

# Create mo files:

if not os.path.exists("mo/"):
    os.mkdir("mo/")
for lang in ('ru', 'uk', 'he'):
    pofile = "po/" + lang + ".po"
    mofile = "mo/" + lang + "/foobnix.mo"
    if not os.path.exists("mo/" + lang + "/"):
        os.mkdir("mo/" + lang + "/")
    print "generating", mofile
    os.system("msgfmt %s -o %s" % (pofile, mofile))

# Copy script "foobnix" file to foobnix dir:
shutil.copyfile("foobnix.py", "foobnix/foobnix")

versionfile = file("foobnix/version.py", "wt")

versionfile.write("""
# generated by setup.py
VERSION = %r
""" % VERSION)
versionfile.close()

setup(name='foobnix',
        version=VERSION,
        description='GTK+ client for the Music Player Daemon (MPD).',
        author='Ivan Ivanenko',
        author_email='ivan.ivanenko@gmail.com',
        url='www.foobnix.com',
        classifiers=[
            'Development Status ::  Beta',
            'Environment :: X11 Applications',
            'Intended Audience :: End Users/Desktop',
            'License :: GNU General Public License (GPL)',
            'Operating System :: Linux',
            'Programming Language :: Python',
            'Topic :: Multimedia :: Sound :: Players',
            ],
         packages=[
                "foobnix",
                "foobnix.application",
                "foobnix.base",
                "foobnix.directory",
                "foobnix.glade",
                "foobnix.lyric",
                "foobnix.model",
                "foobnix.online",
                "foobnix.online.google",
                "foobnix.online.integration",
                "foobnix.player",
                "foobnix.playlist",
                "foobnix.preferences",
                "foobnix.radio",
                "foobnix.thirdparty",
                "foobnix.trayicon",
                "foobnix.util",
                "foobnix.window"                                
                ],
        package_data={'foobnix': ['glade/*.glade', 'glade/*.png']},
        #package_dir={"src/foobnix": "foobnix/"},
        scripts=['foobnix/foobnix'],
        data_files=[('share/foobnix', ['README', 'CHANGELOG', 'TODO', 'TRANSLATORS']),
                    (FOOBNIX_TMP, ['version']),
                    ('share/applications', ['foobnix.desktop']),
                    ('share/pixmaps', glob.glob('foobnix/pixmaps/*')),
                    (FOOBNIX_TMP_RADIO, glob.glob('radio/*')),
                    ('share/man/man1', ['foobnix.1']),
                    ('/usr/share/locale/uk/LC_MESSAGES', ['mo/uk/foobnix.mo']),
                    ('/usr/share/locale/he/LC_MESSAGES', ['mo/he/foobnix.mo']),
                    ('/usr/share/locale/ru/LC_MESSAGES', ['mo/ru/foobnix.mo'])
                    ]
                    
        )


# Cleanup (remove /build, /mo, and *.pyc files:

print "Cleaning up..."
try:
    removeall("build/")
    os.rmdir("build/")
    pass
except:
    pass
try:
    removeall("mo/")
    os.rmdir("mo/")
except:
    pass
try:
    for f in os.listdir("."):
        if os.path.isfile(f):
            if os.path.splitext(os.path.basename(f))[1] == ".pyc":
                os.remove(f)
except:
    pass
try:
    os.remove("foobnix/foobnix")
except:
    pass
try:
    os.remove("foobnix/version.py")
except:
    pass
try:
    os.remove(os.getenv("HOME") + "/foobnix_conf.pkl")
except:
    pass

