# ===========================================================================
#  FILE    : __init__.py
#  AUTHOR  : callmekohei <callmekohei at gmail.com>
#  License : MIT license
# ===========================================================================

import atexit
import neovim
import os
import queue
import re
import subprocess
import threading
import time


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


    @ neovim.function('PyPersimmon', sync = False)
    def persimon(self,arg):

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

        # create dll file
        command  = ['fsharpc', '-a', self.filePath]
        p = subprocess.Popen( command, stdout=subprocess.PIPE, universal_newlines=True )
        out, err = p.communicate()
        p.kill()

        # mono Persimmon.Console.exe
        persimmonConsole_same_folder     = self.expand(os.path.dirname( self.filePath ) + "/Persimmon.Console.exe")
        persimmonConsole_tools_folder    = self.expand(os.path.dirname( self.filePath ) + "//tools/Persimmon.Console.exe")
        persimmonConsole_packages_folder = self.expand(os.path.dirname( self.filePath ) + "/packages/Persimmon.Console/tools/Persimmon.Console.exe")
        persimmonConsole = self.expand( re.split('rplugin', __file__)[0] + self.expand('ftplugin/tools/Persimmon.Console.exe') )
        fp = os.path.splitext(self.filePath)[0] + ".dll"

        if os.path.isfile(persimmonConsole_same_folder) :
            cmd = [ 'mono', persimmonConsole_same_folder, fp ]
        elif os.path.isfile(persimmonConsole_tools_folder) :
            cmd = [ 'mono', persimmonConsole_tools_folder, fp ]
        elif os.path.isfile(persimmonConsole_packages_folder) :
            cmd = [ 'mono', persimmonConsole_packages_folder, fp ]
        else:
            cmd = [ 'mono', persimmonConsole, fp ]

        process = subprocess.Popen( cmd , stdout=subprocess.PIPE, universal_newlines=True)
        out, err = process.communicate()
        process.kill()

        try:
            os.remove(fp)

            line_number = 0
            for line in out.split('\n'):
                buf_quickrunfs.append( line.strip(), line_number )
                line_number = line_number + 1

            elapsed_time = time.time() - start
            buf_quickrunfs.append( ("*** time : {0}".format(round(elapsed_time,6))) + " s ***" )

        except Exception as e:
            self.fsiShow(arg)


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
                list.append( self.lines.get_nowait() )

        return list

