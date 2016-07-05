#!/usr/bin/env python2

server = 'ftp.astron.nl'
subdir = '/outgoing/Measures/'
grammar = 'WSRT_Measures_%s-000001.ztar'
maintainer = 'Gijs Molenaar (launchpad ppa build key) <gijs@pythonic.nl>'
ppa_repo = 'kernsuite/kern-dev'
releases = ('xenial',)

import re
from ftplib import FTP
import os
import sys
import tarfile
import shutil
from datetime import datetime
from time import mktime
from email.utils import formatdate
from pytz import timezone
from subprocess import call


def now():
    return formatdate(mktime(datetime.now(timezone('Africa/Johannesburg')).timetuple()))


HERE = os.path.dirname(__file__)
print('changing dir to ' + HERE)
os.chdir(HERE)

print('connect to the server')
conn = FTP(server, user='anonymous', passwd='info@astron.nl')

print ('get last version')
latest = -1
regex = re.compile(subdir + grammar % '(\d{8})')
for i in conn.nlst(subdir):
    match = regex.match(i)
    if match:
        timestamp = int(match.group(1))
        if timestamp > latest:
            latest = timestamp
print(latest)

base_file = grammar % latest
if not os.access(base_file, os.R_OK):
    print('downloading ' + base_file)
    downloaded = open(base_file, 'wb')
    conn.cwd(subdir)
    conn.retrbinary(cmd='RETR %s' % base_file, callback=downloaded.write)
    downloaded.close()
else:
    print('we already have latest version')


new_dir = 'casacore-data-' + str(latest)
tarball = 'casacore-data_%s.orig.tar.gz' % str(latest)
if os.access(tarball, os.R_OK):
    print '%s already exists, not creating' % tarball
else:
    if os.access(new_dir, os.X_OK):
        print('removing old extracted data')
        shutil.rmtree(new_dir)
        
    print('extracting tarbal')
    os.mkdir(new_dir)
    os.chdir(new_dir)
    open_tar = tarfile.open('../' + base_file)
    for item in open_tar:
        open_tar.extract(item)
    os.chdir('..')

    print('create new tarball')
    with tarfile.open('casacore-data_%s.orig.tar.gz' % str(latest), "w:gz") as tar:
        tar.add(new_dir, arcname=os.path.basename(new_dir))

    
if os.access( os.path.join(new_dir, 'debian'), os.X_OK):
    print('work folder already has debian folder, skipping copy')
else:
    print('copying debian template')
    shutil.copytree('debian', os.path.join(new_dir, 'debian'))

for suit in releases:
    print('updating debian changelog for ' + suit)
    f = open('debian/changelog', 'r')
    content = "".join(f.readlines())\
        .replace('{{ version }}', str(latest))\
        .replace('{{ maintainer }}', maintainer)\
        .replace('{{ timestamp }}', now())\
        .replace('{{ suit }}', suit)
    f.close()
    f = open(os.path.join(new_dir, 'debian/changelog'), 'w')
    f.write(content)
    f.close()
    print(content)

    os.chdir(new_dir)
    print('building package for ' + suit)
    if call(['dpkg-buildpackage']):
        sys.exit(1)

    print('building source package' + suit)
    if call(['debuild', '-sa', '-S']):
        sys.exit(1)

    print('uploading for ' + suit)
    if call(['dput', 'ppa:%s' % ppa_repo, '../casacore-data_%s-1%s_source.changes' % (latest, suit)]):
        sys.exit(1)

    os.chdir('..')
