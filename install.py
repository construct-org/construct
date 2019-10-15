#!/usr/bin/env python
from __future__ import print_function

# Standard library imports
import argparse
import os
import platform
import re
import shutil
import sys
from contextlib import contextmanager
from subprocess import PIPE, Popen, check_call, check_output


# Compat

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
if PY2:
    input = raw_input


# Globals

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
THIS_BIN = os.path.join(THIS_DIR, 'bin')
THIS_LIB = os.path.join(THIS_DIR, 'lib')
APP_NAME = 'construct'
PLATFORM = platform.system()
DEFAULT_VERSION = '0.2.0'
DEFAULT_INSTALL_DIR = {
    'Windows': 'C:/construct',
    'Linux': '/opt/construct',
    'Mac': '/opt/construct'
}[PLATFORM]
DEFAULT_PYTHON = sys.executable
PIP_PACKAGE = (
    'git+https://github.com/construct-org/construct'
    '@%s#egg=construct'
)
ENTRY_POINTS = [
    'construct',
    'construct.bat',
    'construct.ps1',
    'pyconstruct.exe',
    'pyconstruct-script.py',
]
VERBOSE = False
INDENT = ''
STEP = 1


def set_indent(string):
    global INDENT
    INDENT = string


def set_step(value):
    global STEP
    STEP = value


def echo(message, *args, **kwargs):
    output = INDENT + (message % args) + '\n'
    sys.stdout.write(output)
    sys.stdout.flush()


def abort(message, *args):
    output = INDENT + (message % args) + '\n'
    sys.stderr.write(output)
    sys.stderr.write('FAILED!\n')
    sys.stderr.flush()
    sys.exit(1)


@contextmanager
def step(message, *args, **kwargs):
    msg = ('\n' + str(STEP) + '. ' + message) % args
    echo(msg)
    try:
        set_indent('    ')
        yield
        echo('OK!')
    except Exception as e:
        abort('Install step failed...')
    finally:
        set_indent('')
        set_step(STEP + 1)


class Installer(object):
    '''Construct Installer...

    Arguments:
        version (str): x.x.x version string
        name (str): Optional name to use instead of version string
        python (str): Path to python interpreter to use
        where (str): Install directory(defaults: C:/Construct, /opt/construct)
        config (str): Path to construct configuration file
        local (str): If True install from current working directory
        ignore_prompts (bool): Ignore install prompts if True
    '''
    def __init__(
        self,
        version,
        name,
        python,
        where,
        config,
        local,
        ignore_prompts=False
    ):
        self.version = version
        self.name = name or version
        self.python = python
        self.where = os.path.abspath(where)
        self.config = config if config is None else os.path.abspath(config)
        self.pip_package = '.' if local else PIP_PACKAGE % version
        self.ignore_prompts = ignore_prompts
        self.install_path = join_path(self.where, self.name)
        self.install_current = join_path(self.where, 'current')
        self.install_current_bin = join_path(self.where, 'current', 'bin')
        self.install_lib = join_path(self.install_path, 'lib')
        self.install_lib_bin = join_path(self.install_lib, 'bin')
        self.install_bin = join_path(self.install_path, 'bin')
        self.install_env = join_path(self.install_path, 'python')

        if PLATFORM == 'Windows':
            self.install_py = join_path(
                self.install_env,
                'Scripts',
                'python.exe',
            )
            self.install_site = join_path(
                self.install_env,
                'lib',
                'site-packages',
            )
        else:
            pyver = 'python' + get_python_version(python)
            self.install_py = join_path(
                self.install_env,
                'bin',
                'python',
            )
            self.install_site = join_path(
                self.install_env,
                'lib',
                pyver,
                'site-packages',
            )

    def run(self):
        '''Run the installer including any platform specific install steps.'''

        echo(
            '\nInstalling Construct-%s to "%s".',
            self.version,
            self.install_path,
        )
        echo('Using "%s".', self.python)

        with step('Ensure install directories exist...'):
            ensure_exists(self.where)
            ensure_exists(self.install_path)

        with step('Create python virtualenv...'):
            create_venv(self.python, self.install_env, self.install_py)

        with step('Add pth file to virtualenv...'):
            write_pth(self.install_site, self.install_lib, self.install_bin)

        with step('Install construct to virtualenv...'):
            pip_install(
                self.install_py,
                '-I',  # Ignore installed
                '-U',  # Force upgrade
                self.pip_package,
                '--target=%s' % self.install_lib
            )

        with step('Move installed python console scripts...'):
            move_dir(self.install_lib_bin, self.install_bin)

        with step('Update symlink %s...', self.install_current):
            update_symlink(self.install_path, self.install_current)

        with step('Install construct and cons shell scripts...'):
            create_entry_points(self.install_current_bin, self.where)

        # Run platform specific install steps
        {
            'Windows': self.windows_steps,
            'Mac': self.mac_steps,
            'Linux': self.unix_steps,
        }[PLATFORM]()

        echo('\nInstall complete!')
        echo('\nYou should now have access to the construct cli.')
        echo('    cons -h')

    def windows_steps(self):
        '''Windows specific install steps.'''

        if is_elevated():
            with step('Setting windows acls...'):
                win_set_user_acls(self.install_path)

        # Modify system PATH to include construct install directory
        with step('Adding %s to system PATH...', self.where):
            system_path = win_get_env('PATH')
            if self.where not in system_path.split(';'):
                if is_elevated():
                    execute_after(
                        'setx /M PATH "%s;%s"' % (self.where, system_path)
                    )
            execute_after('set "PATH=%s;%%PATH%%"' % self.where)

        if self.config:
            with step('Setting CONSTRUCT_CONFIG to %s...', self.config):
                if is_elevated():
                    execute_after(
                        'setx /M CONSTRUCT_CONFIG "%s"' % self.config
                    )
                execute_after('set "CONSTRUCT_CONFIG=%s"' % self.config)

    def mac_steps(self):
        '''Mac specific install steps'''

        self.unix_steps()
        # TODO: Create Application
        # TODO: Modify plist

    def unix_steps(self):
        '''Linux / Unix install steps'''

        export_cmd = 'export PATH=%s:$PATH' % self.where
        source_cmd = 'source %s/construct.sh' % self.where
        config_cmd = None
        if config:
            config_cmd = 'export CONSTRUCT_CONFIG=%s' % self.config

        if is_elevated():
            bash_profile_path = '/etc/profile'
        else:
            bash_profile_path = os.path.expanduser('~/.profile')

        with step('Add construct to bash profile...'):
            update_profile(
                bash_profile_path,
                export_cmd,
                source_cmd,
                config_cmd,
            )

        with step('Adding %s to PATH...', self.where):
            execute_after(export_cmd)

        with step('Sourcing construct.sh...'):
            execute_after(source_cmd)

        if self.config:
            with step('Setting CONSTRUCT_CONFIG to %s', self.config):
                echo('Setting CONSTRUCT_CONFIG to %s' % self.config)
                execute_after(config_cmd)


# Windows Utilities

def get_winreg():
    '''Get the winreg module'''
    try:
        import _winreg as winreg
    except:
        import winreg
    return winreg


def winreg_env_lookup(user=False):
    '''Get the System or User Environment registry root key and path'''
    winreg = get_winreg()
    user_reg_path = 'Environment'
    reg_path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
    if user:
        return winreg.HKEY_CURRENT_USER, user_reg_path
    else:
        return winreg.HKEY_LOCAL_MACHINE, reg_path


def win_get_env(name, user=False):
    '''Get an environment variables value from the windows registry.'''
    winreg = get_winreg()
    root, path = winreg_env_lookup(user)

    try:
        with winreg.OpenKey(root, path) as key:
            return winreg.QueryValueEx(key, name)[0]
    except WindowsError:
        return ''


def win_set_env(name, value, user=False):
    '''Set an environment variable using the windows registry.'''
    winreg = get_winreg()
    root, path = winreg_env_lookup(user)

    try:
        with winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS) as key:
            try:
                reg_type = winreg.QueryValueEx(key, name)[1]
            except:
                if '%' in value:
                    reg_type = winreg.REG_EXPAND_SZ
                else:
                    reg_type = winreg.REG_SZ
            winreg.SetValueEx(key, name, 0, reg_type, value)
            return True
    except WindowsError:
        return False


def win_send_wm_settingchange(path):
    '''Broadcasts the WM_SETTINGCHANGE for an environment variable.

    Causes windows processes to detect the change and refresh their
    environment variables.
    '''
    import ctypes
    from ctypes.wintypes import HWND, UINT, WPARAM, LPARAM, LPVOID
    send_message = ctypes.windll.user32.SendMessageW
    send_message.argtypes = HWND, UINT, WPARAM, LPVOID
    send_message.restype = LPARAM
    HWND_BROADCAST = 0xFFFF
    WM_SETTINGCHANGE = 0x1A
    send_message(HWND_BROADCAST, WM_SETTINGCHANGE, 0, path)


def win_set_user_acls(where):
    '''Set Windows Ownership and ACLs using icalcs'''
    where = escape(where.replace('/', '\\').rstrip('\\'))
    success = run(
        'icacls %s\* /grant Users:(F) /inheritance:e /T' % where,
        abort_on_fail=False,
    )
    if not success:
        echo('Error: Failed to set permissions for %s', where)


def win_inst_pywin32(python_exe):
    '''Bootstraps pywin32.'''
    try:
        import win32com
        return
    except ImportError:
        pass

    pip_install(python_exe, 'pypiwin32', '--target', LIB)
    os.environ['PATH'] = os.path.abspath(LIB) + ';' + os.environ['PATH']
    sys.path.insert(1, join_path(LIB, 'win32'))
    sys.path.insert(1, join_path(LIB, 'win32', 'lib'))
    sys.path.insert(1, join_path(LIB, 'win32', 'Pythonwin'))


def win_desktop_shortcut(python_exe):
    '''Use pywin32 to create a desktop shortcut.'''
    win_inst_pywin32(python_exe)
    from win32com.client import Dispatch

    # Setup paths
    path = os.path.join(os.path.expanduser('~/Desktop'), 'desktop_app.lnk')
    target = os.path.normpath(self.get_entry_point_path(APP_NAME + '.bat'))
    wDir = os.path.dirname(target)
    icon = os.path.normpath(os.path.join(self.app_dir, 'icon.ico'))

    # Create shortcut
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = wDir
    shortcut.IconLocation = icon
    shortcut.save()


# Linux / Unix Utilities

def update_profile(bash_profile_path, export_cmd, source_cmd, config_cmd=None):
    '''Update bash profile on Linux and MacOS'''
    touch(bash_profile_path)

    with open(bash_profile_path, 'r') as f:
        bash_profile = f.read()

    changed = False
    if export_cmd not in bash_profile:
        bash_profile += '\n' + export_cmd + '\n'
        changed = True
    if source_cmd not in bash_profile:
        bash_profile += source_cmd + '\n'
        changed = True
    if config_cmd:
        match = re.search(r'export CONSTRUCT_CONFIG.*', bash_profile, re.M)
        if not match:
            bash_profile += export_cmd + '\n'
        else:
            string = match.group(0)
            bash_profile = bash_profile.replace(string, export_cmd)
        changed = True
    if changed:
        echo('Creating backup profile %s.bak', bash_profile_path)
        shutil.copy2(bash_profile_path, bash_profile_path + '.bak')
        echo('Writing %s', bash_profile_path)
        with open(bash_profile_path, 'w') as f:
            f.write(bash_profile)


# General Purpose Utilities

def join_path(*paths):
    '''Join and normalize a path'''
    return os.path.normpath(os.path.join(*paths)).replace('\\', '/')


def is_elevated():
    '''Check if this process is elevated'''
    return bool(int(os.environ.get('SCRIM_ADMIN', 1)))


def execute_after(cmd):
    '''Write a shell command to be executed when the python script exits.'''
    script = os.environ.get('SCRIM_PATH')
    if script:
        with open(script, 'a') as f:
            f.write(cmd + '\n')


def ensure_exists(folder):
    '''Make sure a folder exists.'''
    if not os.path.exists(folder):
        echo('Create %s', folder)
        os.makedirs(folder)
    else:
        echo('%s already exists.', folder)


def touch(fname, times=None):
    '''Touch a file'''
    with open(fname, 'a'):
        os.utime(fname, times)


def command_available(cmd):
    '''Check if a shell command is available'''
    try:
        check_call(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        return True
    except:
        return False


def escape(path):
    '''Wrap a path in double quotes if it has a space in it.'''
    if ' ' in path:
        return '"%s"' % path
    return path


def run(cmd, abort_on_fail=True, **kwargs):
    '''Run a shell command and return False if it fails or (stdout, stderr)'''
    kwargs.setdefault('shell', True)
    if not VERBOSE:
        kwargs.setdefault('stderr', PIPE)
        kwargs.setdefault('stdout', PIPE)

    echo('%s', cmd)
    proc = Popen(cmd, **kwargs)
    stdout, stderr = proc.communicate()

    if proc.returncode != 0:
        if abort_on_fail:
            abort('Failed to execute: %s', cmd)
        return False

    return stdout, stderr


def get_python_version(python):
    '''Get the python version from a python executable.'''
    return check_output(
        'python -c "import sys; print(sys.version[:3])"',
        shell=True
    ).strip()


def create_venv(python, env_dir, env_py):
    '''Create a virtualenv using the specified python interpreter.'''
    if os.path.exists(env_dir):
        echo('Virtualenv already exists %s.', env_dir)
        return

    echo('Creating virtualenv %s.', env_dir)
    if command_available(python + ' -c "import virtualenv"'):
        run(python + ' -m virtualenv --no-site-packages ' + env_dir)
    elif command_available(python + ' -c "import venv"'):
        run(python + ' -m venv ' + env_dir)
    else:
        success = run(
            python + ' -m pip install virtualenv',
            abort_on_fail=False,
        )
        if success:
            run(python + ' -m virtualenv --no-site-packages ' + env_dir)
        else:
            abort(
                'Failed to setup a virtualenv for construct.\n\n'
                'Install virtualenv for "%s"',
                python
            )

    # Upgrade pip
    echo('Upgrading pip...')
    pip_install(env_py, '-U', 'pip')


def pip_install(python, *args):
    '''Pip install using the specified python interpreter'''
    args = [python, '-m', 'pip', 'install'] + list(args)
    run(' '.join(args), abort_on_fail=True)


def move_dir(src, dest):
    '''Move a directory recursively.'''
    if not os.path.isdir(dest):
        echo('Creating %s', dest)
        os.makedirs(dest)

    for src_root, subdirs, files in os.walk(src):
        dest_root = src_root.replace(src, dest)

        if not os.path.isdir(dest_root):
            echo('Creating %s', dest_root)
            os.makedirs(dest_root)

        for f in files:
            echo('%s > %s', join_path(src_root, f), join_path(dest_root, f))
            src_path = join_path(src_root, f)
            dest_path = join_path(dest_root, f)
            if os.path.exists(dest_path):
                os.remove(dest_path)
            os.rename(src_path, dest_path)

    shutil.rmtree(src)


def update_symlink(src, dest):
    '''Creates or updates a symlink'''
    if PLATFORM == 'Windows':
        src = os.path.normpath(src)
        dest = os.path.normpath(dest)
        is_dir = os.path.isdir(src)
        if os.path.isdir(dest):
            run('rmdir %s' % dest)
        if os.path.isfile(dest):
            run('del %s' % dest)
        if is_dir:
            stdout, stderr = run('mklink /D %s %s' % (dest, src))
        else:
            stdout, stderr = run('mklink %s %s' % (dest, src))
    else:
        if os.path.isdir(dest):
            os.remove(dest)
        os.symlink(src, dest)


def create_entry_points(bin, dest):
    '''Copies scripts from construct_setup/bin to dest'''
    for entry_point in ENTRY_POINTS:
        bin_path = join_path(bin, entry_point)
        dest_path = join_path(dest, entry_point)
        if not os.path.isfile(bin_path):
            continue
        update_symlink(
            join_path(bin, entry_point),
            join_path(dest, entry_point),
        )


def write_pth(site, lib, bin):
    '''Creates a pth file pointing to custom python lib directory.'''
    lib_path = os.path.relpath(lib, site).replace('\\', '/')
    bin_path = os.path.relpath(bin, site).replace('\\', '/')
    site_path = join_path(site, 'construct.pth')

    echo('Writing %s.', site_path)
    set_indent('    ' * 2)
    echo(lib_path)
    echo(bin_path)
    set_indent('    ')

    with open(site_path, 'w') as f:
        f.write('\n'.join([lib_path, bin_path]))


def main():
    if not command_available('git --version'):
        abort(
            'Git is required to install construct.\n\n'
            'Download it from https://git-scm.com/.'
        )

    parser = argparse.ArgumentParser('construct_installer', add_help=True)
    parser.add_argument(
        '--version',
        required=False,
        action='store',
        default=DEFAULT_VERSION
    )
    parser.add_argument(
        '--python',
        action='store',
        help='Python Executable',
        default=DEFAULT_PYTHON
    )
    parser.add_argument(
        '--where',
        action='store',
        help='Where to install',
        default=DEFAULT_INSTALL_DIR
    )
    parser.add_argument(
        '--config',
        action='store',
        help='Location of a construct configuration file.',
        default=''
    )
    parser.add_argument(
        '--local',
         action='store_true',
         help='Install from local directory.',
    )
    parser.add_argument(
        '--name',
         action='store',
         help='Use a specific name instead of version.',
         default=None,
    )
    parser.add_argument(
        '--ignore-prompts',
         action='store_true',
         help='Do not request user input.',
         default=False,
    )
    parser.add_argument(
        '--debug',
         action='store_true',
         help='Do not request user input.',
         default=False,
    )

    args = parser.parse_args()
    args.python = escape(args.python)

    if args.debug:
        global VERBOSE
        VERBOSE = True
    delattr(args, 'debug')

    if not command_available(args.python + ' -c "import pip"'):
        abort(
            'pip is required to install construct.\n\n'
            'Get it from https://pip.pypa.io/en/stable/installing/.'
        )
    if not is_elevated() and PLATFORM == 'Windows':
        echo(
            'To fully install Construct you need Admin priviledges. The '
            'following features will be disabled.\n\n'
            '    - Setting system environment variables\n'
            '    - Setting folder permissions\n'
        )
        if not args.ignore_prompts:
            answer = input('Would you like to install anyway? [y] or n\n')
            if answer and answer.lower().startswith('n'):
                echo('Abort.')
                sys.exit()

    Installer(**vars(args)).run()


if __name__ == "__main__":
    main()
