#!/usr/bin/env python
'''
Utility functions
'''
import re
import os
import hashlib

try:    from urllib import request
except: from urllib import urlopen
else:   urlopen = request.urlopen



def mgetter(callable):
    def f(match):
        key = match.group(1)
        val = callable(key,'{'+key+'}')
        return val
    return f

subn_reobj = re.compile(r'{(\w+)}')
def format_get(string, getter):
    '''Format <string> using the function <getter(key, default)> which
    returns the value for the <key> or <default> if not found.
    '''
    ret = re.subn(subn_reobj, mgetter(getter), string)
    return ret[0]

def format(string, **items):
    '''Format <string> using <items>'''
    return format_get(string, items.get)



def string2list(string, delims=', '):
    if not isinstance(string, type('')):
        return string
    return [x.strip() for x in re.split('[%s]+'%delims, string) if x.strip()]

def update_if(d, p, **kwds):
    '''Return a copy of d updated with kwds.

    If no such item is in d, set item from kwds, else call p(k,v) with
    kwds item and only set if returns True.

    '''
    if p is None:
        p = lambda k,v: v is not None 
    d = dict(d)                 # copy
    for k,v in kwds.items():
        if not k in d:
            d[k] = v
            continue
        if p(k, v):
            d[k] = v

    return d

    
import subprocess
from subprocess import CalledProcessError

try:
    from subprocess import check_output
except ImportError:
    class CalledProcessError(Exception):
        """This exception is raised when a process run by check_call() or
        check_output() returns a non-zero exit status.
        The exit status will be stored in the returncode attribute;
        check_output() will also store the output in the output attribute.
        """
        def __init__(self, returncode, cmd, output=None):
            self.returncode = returncode
            self.cmd = cmd
            self.output = output
        def __str__(self):
            return "Command '%s' returned non-zero exit status %d" % (self.cmd, self.returncode)

    def check_output(*popenargs, **kwargs):
        r"""Run command with arguments and return its output as a byte string.

        If the exit code was non-zero it raises a CalledProcessError.  The
        CalledProcessError object will have the return code in the returncode
        attribute and output in the output attribute.

        The arguments are the same as for the Popen constructor.  Example:

        >>> check_output(["ls", "-l", "/dev/null"])
        'crw-rw-rw- 1 root root 1, 3 Oct 18  2007 /dev/null\n'

        The stdout argument is not allowed as it is used internally.
        To capture standard error in the result, use stderr=STDOUT.

        >>> check_output(["/bin/sh", "-c",
        ...               "ls -l non_existent_file ; exit 0"],
        ...              stderr=STDOUT)
        'ls: non_existent_file: No such file or directory\n'
        """
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise CalledProcessError(retcode, cmd, output=output)
        return output


def envvars(envtext):
    '''
    Parse envtext as lines of 'name=value' pairs, return result as a
    dictionary.  Values beginning with '()' are allowed to span
    multiple lines and expected to end with a closing brace.
    '''
    def lines(text):
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            yield line
    lines = lines(envtext)      # this looses the first?

    ret = dict()
    for line in lines:
        name, val = line.split('=',1)
        if not val.startswith('()') or val.endswith('}'):
            ret[name] = val
            continue

        # we have a multi-lined shell function, slurp until we get an ending '}'
        val = [val]
        for line in next(lines):
            val.append(line)
            if line.endswith('}'):
                break
            continue
        ret[name] = '\n'.join(val)
    return ret

def get_unpacker(filename, dirname = '.'):
    if filename.endswith('.zip'): 
        return 'unzip -d %s %s' % (dirname, filename)
    
    text2flags = {'.tar.gz':'xzf', '.tgz':'xzf', '.tar.bz2':'xjf', 'tbz2':'xjf', '.tar':'xf' }
    for ext, flags in text2flags.items():
        if filename.endswith(ext):
            return 'tar -C %s -%s %s' % (dirname, flags, filename)
    return 'tar -C %s -xf %s' % (dirname, filename)

def nuke_file(path):
    'Delete the given file'
    if os.path.exists(path):
        os.remove(path)


def download_urllib(url, target):
    '''Download a file from URL to target using urllib, return URL
    actually downloaded.  An IOError is raised on any failure and the
    target will not exist.
    '''
    try:
        web = urlopen(url)
    except Exception:
        import traceback
        traceback.print_exc()
        err = "download: urllib failed to open %s"% url
        raise IOError(err)

    http_code = web.getcode()

    if http_code == 301:
        return download_urllib(web.geturl(), target)

    if http_code != 200:
        err = 'download: urllib failed to download (%s) %s' % (http_code, url)
        raise IOError(err)

    fp = open(target, "wb")
    fp.write(web.read())
    return web.geturl()

def download_wget(url, target):
    try:
        check_output(['wget','--quiet', '--no-check-certificate','-O',target,url])
    except Exception,err:
        nuke_file(target)
        raise IOError,err
    return url                  # in general, this is a small lie

def download_curl(url, target):
    try:
        check_output(['curl','--silent', '--insecure','-o',target,url])
    except Exception,err:
        nuke_file(target)
        raise IOError,err
    return url                  # in general, this is a small lie

def download_any(url, target):

    for maybe in download_urllib, download_wget, download_curl:
        try:
            return maybe(url, target)
        except IOError, err:
            nuke_file(target)
            print (err)
            if maybe != download_curl:
                print ('...still trying') 
            pass

    raise IOError('unable to download %s to %s' % (url, target))

def download(url, target, checksum=None):
    '''Download <url> to <target>, return actual URL downloaded.

    If checksum is given compare it to the one formed from the
    downloaded file.  The checksum is of the form <type>:<hash> where
    <type> names a hash function in hashlib.

    An IOError is raised on any failure.
    '''
    try:
        goturl = download_any(url, target)
    except IOError:
        nuke_file(target)
        raise

    if not checksum:
        return goturl

    hasher_name, ref = checksum.split(":")
    # FIXME: check the hasher method exists. check for typos.
    hasher = getattr(hashlib, hasher_name)()
    hasher.update(open(target,"rb").read())
    data = hasher.hexdigest()
    if data != ref:
        nuke_file(target)
        raise IOError("download: checksum mismatch: %s != %s" % (data, ref))

    return goturl

def download_mirror(urls, target, checksum=None):
    '''
    Download a file from a list of possible URLs.

    Returns o first success or raises IOError.

    The <urls> may be a single URL or a sequence of URLs.
    '''

    if hasattr(urls, 'startswith'):
        urls = [urls]

    #print 'download_mirror(URLS="%s", TARGET="%s")' % (str(urls), target)

    for url in urls:
        try:
            return download(url, target, checksum)
        except IOError:
            pass

    raise IOError('download: unable to download "%s"' % \
                  os.path.basename(target))

