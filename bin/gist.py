#!/usr/bin/env python
"""
Gist
----

Gist is a command line tool for interacting with `gist.github.com`_. Usage
information is available through the command line interface help.

.. _gist.github.com: <https://gist.github.com>

.. important::
    On your first usage the script will use basic auth to authorize an oauth
    token. Once authorized you will not be asked for your username or password
    again. Your password and username are never stored and are only sent to
    Github.com over an HTTPS connection.

Here a few examples of useage::

   $ python gist.py create gist.py # Creates a new gist named gist.py


.. TODO:
  * Make `create` and `edit` work with multiple files
  * Add support for fork`
  * Add documentation

"""
from argparse import ArgumentParser, FileType
import base64
from contextlib import closing
import getpass
from httplib import HTTPSConnection
import json
import os
import sys


HOST = 'api.github.com'


# `copy_url` from lodgeit.py
# :license: 3-Clause BSD
# :authors: 2007-2008 Georg Brandl <georg@python.org>,
#           2006 Armin Ronacher <armin.ronacher@active-4.com>,
#           2006 Matt Good <matt@matt-good.net>,
#           2005 Raphael Slinckx <raphael@slinckx.net>
def copy_url(url):
    """Copy the url into the clipboard."""
    # try windows first
    try:
        import win32clipboard
    except ImportError:
        # then give pbcopy a try.  do that before gtk because
        # gtk might be installed on os x but nobody is interested
        # in the X11 clipboard there.
        from subprocess import Popen, PIPE
        for prog in 'pbcopy', 'xclip':
            try:
                client = Popen([prog], stdin=PIPE)
            except OSError:
                continue
            else:
                client.stdin.write(url)
                client.stdin.close()
                client.wait()
                break
        else:
            try:
                import pygtk
                pygtk.require('2.0')
                import gtk
                import gobject
            except ImportError:
                return
            gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD).set_text(url)
            gobject.idle_add(gtk.main_quit)
            gtk.main()
    else:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(url)
        win32clipboard.CloseClipboard()


def authorize(user, password):
    with closing(HTTPSConnection(HOST, timeout=10)) as conn:
        data = {
            'scopes': ['gist', 'repo'],
            'note': 'Authorization for gist.py commandline tool',
            }
        encoded_auth = base64.b64encode('%s:%s' % (user, password))
        conn.request('POST', '/authorizations', json.dumps(data),
                     {'Authorization': 'Basic %s' % encoded_auth,
                      'User-Agent': 'GIST',
                      'Content-Type': 'application/json'})
        resp = conn.getresponse()
        return json.loads(resp.read())


def create(token, filename, content, message, public):
    with closing(HTTPSConnection(HOST, timeout=10)) as conn:
        data = {
            'public': public,
            'desciption': message,
            'files': {
                filename: {
                    "content": content
                    }
                },
            }
        path = '/gists'
        conn.request('POST', path, json.dumps(data),
                     {
                'Content-Type': 'application/json',
                'User-Agent': 'GIST',
                'Authorization': 'bearer %s' % token,
                      }
                     )
        resp = conn.getresponse()

        if resp.status >= 200 and resp.status < 300:
            resp_data = json.loads(resp.read())
            print resp_data['html_url']
            copy_url(resp_data['html_url'])
        else:
            print '%s %s' % (resp.status, resp.read())


def create_controller(token, namespace):
    paste = namespace.paste
    if not paste and not os.isatty(sys.stdin.fileno()):
        paste = sys.stdin

    if paste:
        name = namespace.name or os.path.basename(paste.name)
        create(token, name, paste.read(),
               namespace.message, namespace.public)


def delete_controller(token, namespace):
    for id_ in namespace.ids:
        delete(token, id_, namespace.verbose)


def delete(token, id_, verbose):
    path = '/gists/%s' % id_
    with closing(HTTPSConnection(HOST, timeout=10)) as conn:
        conn.request('DELETE', path, headers={
                'Authorization': 'bearer %s' % token,
                'User-Agent': 'GIST',
                }
                     )
        resp = conn.getresponse()
        if resp.status == 204:
            print 'Deleted %s' % id_


def edit_controller(token, namespace):
    paste = namespace.paste
    if not paste and not os.isatty(sys.stdin.fileno()):
        paste = sys.stdin

    filename = namespace.name or os.path.basename(paste.name)
    path = '/gists/%s' % (
        namespace.id)

    with closing(HTTPSConnection(HOST, timeout=10)) as conn:
        data = {
            'files': {
                filename: {
                    "content": paste.read()
                    }
                },
            }
        if namespace.message:
            data.update({'description': namespace.message})
        conn.request('PATCH', path, json.dumps(data),
                     {
                'Content-Type': 'application/json',
                'User-Agent': 'GIST',
                'Authorization': 'bearer %s' % token,
                      })

        resp = conn.getresponse()

        if resp.status >= 200 and resp.status < 300:
            resp_data = json.loads(resp.read())
            print resp_data['html_url']
            copy_url(resp_data['html_url'])
        else:
            print '%s %s' % (resp.status, resp.read())


def list_controller(token, namespace):
    if namespace.all:
        path = '/gists/public'
    elif namespace.user:
        path = '/users/%s/gists' % namespace.user
    elif namespace.starred:
        path = '/gists/starred'
    else:
        path = '/gists'

    with closing(HTTPSConnection(HOST, timeout=10)) as conn:
        conn.request('GET', path, headers={
                'User-Agent': 'GIST',
                'Authorization': 'bearer %s' % token,
                })
        resp = conn.getresponse()
        if resp.status == 200:
            data = json.loads(resp.read())
            # Order by `created_date` descending
            order_cmp = lambda x, y: x['created_at'] > y['created_at']
            for _gist in sorted(data, cmp=order_cmp):
                if namespace.only_public and _gist['public'] == False:
                    continue
                if namespace.only_private and _gist['public'] == True:
                    continue
                if namespace.verbose:
                    print "%s:\n  description: %s\n  files: %s" % (
                    _gist['html_url'], _gist['description'],
                    ' '.join(_gist['files'].keys()))
                   #TODO:dc: stream out gist content
                else:
                    print _gist['html_url']
        else:
            print ' '.join([str(resp.status), resp.read()])


def star_controller(token, namespace):
    for id_ in namespace.ids:
        star(token, id_, namespace.verbose)


def star(token, id_, verbose):
    path = '/gists/%s/star' % id_
    with closing(HTTPSConnection(HOST, timeout=10)) as conn:
        conn.request('PUT', path, headers={
                'Content-Length': '0',
                'User-Agent': 'GIST',
                'Authorization': 'bearer %s' % token,
                })
        resp = conn.getresponse()
        if resp.status == 204:
            print 'Starred %s' % id_


def unstar_controller(token, namespace):
    for id_ in namespace.ids:
        unstar(token, id_, namespace.verbose)


def unstar(token, id_, verbose):
    path = '/gists/%s/star' % id_
    with closing(HTTPSConnection(HOST, timeout=10)) as conn:
        conn.request('DELETE', path, headers={
                'User-Agent': 'GIST',
                'Authorization': 'bearer %s' % token,
                })
        resp = conn.getresponse()
        if resp.status == 204:
            print 'Unstarred %s' % id_


def view_controller(token, namespace):
    for id_ in namespace.ids:
        view(token, id_, namespace.verbose)


def view(token, gist_id, verbose):
    path = '/gists/%s' % gist_id
    with closing(HTTPSConnection(HOST, timeout=10)) as conn:
        conn.request('GET', path, headers={
                'User-Agent': 'GIST',
                'Authorization': 'bearer %s' % token,
                })
        resp = conn.getresponse()
        if resp.status == 200:
            data = json.loads(resp.read())
            for file_ in data['files'].values():
                if verbose:
                    print '-' * 10
                    print 'name:%s \n  raw_url: %s \n  size: %s' % (
                        file_['filename'], file_['raw_url'], file_['size'])
                    print '-' * 10
                print file_['content']


def repo_list_controller(token, namespace):
    if namespace.user:
        path = '/users/%s/repos' % namespace.user
    elif namespace.org:
        path = '/orgs/%s/repos' % namespace.org
    else:
        path = '/user/repos'

    # TODO:dc: add forks

    with closing(HTTPSConnection(HOST, timeout=10)) as conn:
        conn.request('GET', path, headers={
                'User-Agent': 'GIST',
                'Authorization': 'bearer %s' % token,
                })
        resp = conn.getresponse()
        if resp.status == 200:
            data = json.loads(resp.read())
            for repo in data:
                print "%s %s %s" % (
                    repo['name'],
                    repo['description'].encode('ascii', 'replace'),
                    repo['html_url'])
        else:
            print ' '.join([str(resp.status), resp.read()])

_cmd_controllers = {
    'gist': {
        'create': create_controller,
        'delete': delete_controller,
        'edit': edit_controller,
        'list': list_controller,
        'star': star_controller,
        'unstar': unstar_controller,
        'view': view_controller,
        },
    'repo': {
        'list': repo_list_controller,
        }
}


def build_gist_cli(subparsers):
    gist = subparsers.add_parser('gist', help='Manage gists')

    gist_subparsers = gist.add_subparsers(dest="sub_cmd")
    create_parser = gist_subparsers.add_parser(
        'create', help='Create a new gist')
    create_parser.add_argument(
        '-n', '--name',
        help='Give an explicit filename. Most useful for stdin.',
        default=None)
    create_parser.add_argument(
        '-m', '--message', help='A message describing this gist', default='')
    create_parser.add_argument(
        '--public', help='Set the default visibility for this paste.',
        default=False)
    create_parser.add_argument(
        'paste', nargs='?', help='Accepts a filename or - for stdin',
        type=FileType('r'), default=None)

    delete_parser = gist_subparsers.add_parser(
        'delete', help='View a specific gist')
    delete_parser.add_argument('ids', nargs='+')

    edit_parser = gist_subparsers.add_parser(
        'edit', help='View a specific gist')
    edit_parser.add_argument('--id', help='Gist id')
    edit_parser.add_argument('paste', nargs='?',
                             help='Accepts a filename or - for stdin',
                             type=FileType('r'))
    edit_parser.add_argument(
        '-m', '--message', help='A message describing this gist', default='')
    edit_parser.add_argument(
        '-n', '--name',
        help='Give an explicit filename. Most useful for stdin.',
        default=None)

    list_parser = gist_subparsers.add_parser(
        'list', help='List gists. Defaults to showing all your gists')
    list_group = list_parser.add_mutually_exclusive_group()
    list_group.add_argument(
        '-u', '--user', help='A users public gists', default=None)
    list_group.add_argument(
        '-a', '--all', help='All public gists', action='store_true')
    list_group.add_argument(
        '--only-private', help='Only your private gists', action='store_true')
    list_group.add_argument(
        '--only-public', help='Only your public gists', action='store_true')
    list_group.add_argument(
        '--starred', help='Your starred gists', action='store_true')

    sync_parser = gist_subparsers.add_parser(
        'sync', help='Syncronize owned gists to a local path')
    sync_parser.add_argument(
        '-d', '--path', help='Output directory to sync gists to')

    star_parser = gist_subparsers.add_parser(
        'star', help='View a specific gist')
    star_parser.add_argument('ids', nargs='+')

    unstar_parser = gist_subparsers.add_parser(
        'unstar', help='View a specific gist')
    unstar_parser.add_argument('ids', nargs='+')

    view_parser = gist_subparsers.add_parser(
        'view', help='View a specific gist')
    view_parser.add_argument('ids', nargs='+')
    return subparsers


def build_repo_cli(subparsers):
    repo = subparsers.add_parser('repo', help='Manage repos')
    repo_subparsers = repo.add_subparsers(dest='sub_cmd')
    list_parser = repo_subparsers.add_parser(
        'list', help='List repos owned by a user or org')
    list_group = list_parser.add_mutually_exclusive_group()
    list_group.add_argument(
        '-u', '--user', help='A users repos', default=None)
    list_group.add_argument(
        '-o', '--org', help='An orgs repos', default=None)


def main():
    parser = ArgumentParser()

    parser.add_argument('-c', '--config',
                        help='Configuration to use, defaults to ~/.gist',
                        default=os.path.join('~', '.gist'))

    parser.add_argument('-v', '--verbose',
                        help='Turn on additional output', action='store_true')

    parser.add_argument('--login', help='Github login to use',
                        default=getpass.getuser())

    subparsers = parser.add_subparsers(dest='cmd')
    build_gist_cli(subparsers)
    build_repo_cli(subparsers)
    namespace = parser.parse_args()

    auth = {}
    info_path = os.path.expanduser(namespace.config)
    if os.path.exists(info_path):
        with open(info_path) as fp:
            auth = json.load(fp)
    else:
        auth = authorize(namespace.login, getpass.getpass('Password: '))
        with open(info_path, 'w+') as fp:
            json.dump(auth, fp)

    _sub_controllers = _cmd_controllers.get(namespace.cmd)
    fn = None
    if _sub_controllers:
        fn = _sub_controllers.get(namespace.sub_cmd)

    if fn:
        fn(auth['token'], namespace)
    else:
        parser.print_help()

    sys.exit(-1)

if __name__ == '__main__':
    main()
