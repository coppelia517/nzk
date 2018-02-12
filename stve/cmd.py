import os
import sys
import time
import threading
import subprocess

from stve import PYTHON_VERSION
from stve import STRING_SET
from stve.exception import *

if PYTHON_VERSION == 2:
    FileNotFoundError = IOError

class ThreadWithReturn(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(ThreadWithReturn, self).__init__(*args, **kwargs)
        self._return = None

    def run(self):
        if self._Thread__target is not None:
            self._return = self._Thread__target(*self._Thread__args, **self._Thread__kwargs)

    def join(self, timeout=None):
        super(ThreadWithReturn, self).join(timeout=timeout)
        return self._return

def run_bg(cmd, cwd=None, debug=False, shell=False):
    if shell == False and type(cmd) in STRING_SET:
        cmd = [c for c in cmd.split() if c != '']
    if debug:
        sys.stderr.write(''.join(cmd) + '\n')
        sys.stderr.flush()
    if PYTHON_VERSION == 2:
        try:
            proc = subprocess.Popen(cmd,
                                    cwd     = cwd,
                                    stdout  = subprocess.PIPE,
                                    stderr  = subprocess.PIPE,
                                    shell   = shell)
            proc_thread = ThreadWithReturn(target=proc.communicate)
            proc_thread.daemon = True
            proc_thread.start()
        except OSError as e:
            raise RunError(cmd, None, message='Raise Exception : %s' % str(e))
        returncode = proc.returncode
        return (returncode)
    else:
        try:
            proc2 = subprocess.Popen(cmd,
                                     cwd     = cwd,
                                     stdout  = subprocess.PIPE,
                                     stderr  = subprocess.PIPE,
                                     shell   = shell)
            #out, err = proc2.communicate()
        except FileNotFoundError as e:
            out = "{0}: {1}\n{2}".format(type(e).__name__, e, traceback.format_exc())
            raise RunError(cmd, None, message='Raise Exception : %s' % out)
        except Exception as e:
            if proc2 != None: proc2.kill()
            out = "{0}: {1}\n{2}".format(type(e).__name__, e, traceback.format_exc())
            raise TimeoutError({
                'cmd'       : cmd,
                'out'       : None,
                'message'   : 'command %s is time out' % cmd
            })
        except OSError as e:
            raise RunError(cmd, None, message='Raise Exception : %s' % str(e))
        return 0

def run(cmd, cwd=None, timeout=300, debug=False, shell=False):
    if shell == False and type(cmd) in STRING_SET:
        cmd = [c for c in cmd.split() if c != '']
    if debug:
        sys.stderr.write(''.join(cmd) + '\n')
        sys.stderr.flush()

    try:
        if PYTHON_VERSION == 2:
            proc = subprocess.Popen(cmd,
                                    cwd     = cwd,
                                    stdout  = subprocess.PIPE,
                                    stderr  = subprocess.PIPE,
                                    shell   = shell)
            proc_thread = ThreadWithReturn(target=proc.communicate)
            proc_thread.start()
            result = proc_thread.join(timeout)
            if proc_thread.is_alive():
                try:
                    proc.kill()
                except OSError as e:
                    out = "{0}: {1}\n{2}".format(type(e).__name__, e, traceback.format_exc())
                    raise RunError(cmd, None, message='Raise Exception : %s' % out)
                raise TimeoutError({
                    'cmd'       : cmd,
                    'out'       : None,
                    'message'   : 'command %s is time out' % cmd
                })
            returncode = proc.returncode
            if shell: returncode = 0
            if result == None:
                out = None; err = None;
            else:
                out = result[0]; err = result[1]
        else:
            try:
                proc2 = subprocess.Popen(cmd,
                                         cwd     = cwd,
                                         stdout  = subprocess.PIPE,
                                         stderr  = subprocess.PIPE,
                                         shell   = shell)
                out, err = proc2.communicate(timeout=timeout)
                returncode = proc2.returncode
                if shell: returncode = 0
            except FileNotFoundError as e:
                out = "{0}: {1}\n{2}".format(type(e).__name__, e, traceback.format_exc())
                raise RunError(cmd, None, message='Raise Exception : %s' % out)
            except Exception as e:
                if proc2 != None: proc2.kill()
                out = "{0}: {1}\n{2}".format(type(e).__name__, e, traceback.format_exc())
                raise TimeoutError({
                    'cmd'       : cmd,
                    'out'       : None,
                    'message'   : 'command %s is time out' % cmd
                })

    except OSError as e:
        out = "{}: {}\n{}".format(type(e).__name__, e, traceback.format_exc())
        raise RunError(cmd, None, message='Raise Exception : %s' % out)

    except RuntimeError as e:
        out = "{}: {}\n{}".format(type(e).__name__, e, traceback.format_exc())
        raise RunError(cmd, None, message='Raise Exception : %s' % out)
    try:
        if PYTHON_VERSION == 2:
            if isinstance(out, bytes): out = out.decode("utf8")
            if isinstance(err, bytes): err = err.decode("utf8")
        else:
            if isinstance(out, bytes): out = str(out.decode("utf8"))
            if isinstance(err, bytes): err = str(err.decode("utf8"))
            #if isinstance(out, bytes): out = str(out.decode(sys.stdin.encoding))
            #if isinstance(err, bytes): err = str(err.decode(sys.stdin.encoding))
    except UnicodeDecodeError as e:
        out = "{}: {}\n{}".format(type(e).__name__, e, traceback.format_exc())
        sys.stderr.write(out)
    return (returncode, out, err)
