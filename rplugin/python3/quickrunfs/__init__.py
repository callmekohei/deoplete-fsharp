# ===========================================================================
#  FILE    : __init__.py
#  AUTHOR  : callmekohei <callmekohei at gmail.com>
#  License : MIT license
# ===========================================================================

import atexit
import collections
import neovim
import os
import queue
import re
import subprocess
import threading
import time
from deoplete.util import debug


@ neovim.plugin
class quickrunfsHeader(object):

    def __init__(self,vim):
        self.vim = vim


    @ neovim.function('LaunchFSI', sync = False)
    def launchFSI(self,arg):

        self.filePath = self.expand( self.vim.eval( "substitute( expand('%:p:r') . '_deoplete-fsharp_temporary_file.fsx' , '\#', '\\#' , 'g' )" ) )
        fsi_path = self.expand( re.split('rplugin', __file__)[0] + self.expand('ftplugin/bin_quickrunfs/quickrunfs.exe') )

        self.util = Util( fsi_path, 10 )
        self.util.start()


    def expand(self,path):
        return os.path.expandvars(os.path.expanduser(path))

    def tail(self, n, iterable):
        return list(collections.deque(iterable, maxlen=n))


    @ neovim.function('PyQuickRunFs', sync = False)
    def fsiShow(self,arg):

        start = time.time()

        lst = list(filter(lambda b:os.path.basename(b.name) == 'quickrunfs-output', self.vim.buffers ))

        if len(lst) != 0:
            self.vim.command("bw!{quickrunfs-output}")

        self.vim.command("vsplit quickrunfs-output")
        self.vim.command("setlocal buftype=nofile")
        self.vim.command("setlocal bufhidden=hide")
        self.vim.command("setlocal noswapfile")
        self.vim.command("setlocal nobuflisted")

        buf_quickrunfs = self.vim.current.buffer

        self.vim.command("wincmd p")

        self.util.send(self.filePath)

        if len(lst) == 0:
            lines = (self.util.read())[1:]
        else:
            lines = self.util.read()


        ### for Persimmon.Script
        s = "============================== summary ==============================="
        if s in lines:
            try:
                l = min([ i for i, word in enumerate(lines) if word.startswith('begin') ])
                m = max([ i for i, word in enumerate(lines) if word.startswith('end') ])

                head_lines = []
                if l > 0:
                    head_lines = lines[0:l]
                testReport_lines = lines[l:m+1]
                tail_lines = lines[m+3:]

                n = max([ i for i, word in enumerate(testReport_lines) if word.startswith('begin') ])
                tpl = self.util.isViolatedMassages ( testReport_lines[n] )

                if tpl[0] :
                    n = len(testReport_lines) - min([ i for i, word in enumerate(testReport_lines) if word.startswith(tpl[1]) ])
                    testReport_lines = self.tail(n, testReport_lines)
                    lines = head_lines + testReport_lines + tail_lines
                else:
                    lines = head_lines + ["PASS"] + tail_lines
            except:
                s = "============================== summary ==============================="
                l = min([ i for i, word in enumerate(lines) if word.startswith(s) ])

                head_lines = []
                if l > 0:
                    head_lines = lines[0:l]
                tail_lines = lines[l+2:]            
                lines = head_lines + ["PASS"] + tail_lines


        line_number = 0
        for line in lines:
            buf_quickrunfs.append( line.strip(), line_number )
            line_number = line_number + 1

        elapsed_time = time.time() - start
        buf_quickrunfs.append( ("*** time : {0}".format(round(elapsed_time,6))) + " s ***" )


class Util(threading.Thread):

    def __init__(self, exe_path, timeOut_s):
        super(Util, self).__init__()
        self.exe_path  = exe_path
        self.timeOut_s = timeOut_s
        self.event     = threading.Event()
        self.lines     = queue.Queue()
        self.namespace = []


    def run(self):

        # launch quickrunfs
        command      = [ 'mono', self.exe_path ]
        opts         = { 'stdin': subprocess.PIPE, 'stdout': subprocess.PIPE, 'stderr': subprocess.PIPE, 'universal_newlines': True }
        self.process = subprocess.Popen( command , **opts )
        atexit.register(lambda: self.process.kill())

        # create worker thread
        self.worker        = threading.Thread(target=self.work, args=(self,))
        self.worker.daemon = True
        self.worker.start()


    def work(self,_):
        while True:
            data = self.process.stdout.readline()
            self.lines.put(data, True)
            self.event.set()


    def send(self,txt):
        self.event.clear()
        self.process.stdin.write(txt + '\n')
        self.process.stdin.flush()


    def read(self):
        self.event.wait(self.timeOut_s)

        list = []
        while True:
            if self.lines.empty():
                break
            else:
                list.append( (self.lines.get_nowait()).strip() )

        return list


    def isViolatedMassages(self,s) :
        if not self.namespace :
            self.namespace.append(s)
            return (True, "")
        elif self.namespace[-1] != s:
            self.namespace.append(s)
            return (True, self.namespace[-1])
        else:
            return (False, self.namespace[-1])
