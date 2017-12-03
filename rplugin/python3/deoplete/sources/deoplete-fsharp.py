# ===========================================================================
#  FILE    : deoplete-fsharp.py
#  AUTHOR  : callmekohei <callmekohei at gmail.com>
#  License : MIT license
# ===========================================================================

import atexit
import functools
import os
import queue
import re
import subprocess
import threading
import time

try:
    import ujson as json
except ImportError:
    import json

from deoplete.source.base import Base
from deoplete.util import getlines, expand
from deoplete.util import debug

class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)
        self.name      = 'deopletefs'
        self.mark      = '[deopletefs]'
        self.filetypes = ['fsharp']

        # input pattern
        dotHints           = [ r"(\(|<|[a-zA-Z]|\"|\[)*(?<=(\)|>|[a-zA-Z0-9]|\"|\]))\." ]
        oneWordHints       = [ r"^[a-zA-Z]$", "\s*[a-zA-Z]$", "typeof\<[a-zA-Z]$", "(\(\))[a-zA-Z]$", "(\<|\>)[a-zA-Z]$", "(\[|\])[a-zA-Z]$"  ]
        attributeHints     = [ r"\[<[a-zA-Z]*" ]
        self.input_pattern = '|'.join( dotHints + oneWordHints + attributeHints )
 

    def on_init(self, context):

        self.filePath = expand( self.vim.eval( "substitute( expand('%:p:r') . '_deoplete-fsharp_temporary_file.fsx' , '\#', '\\#' , 'g' )" ) )
        fsc_path      = expand( re.split('rplugin', __file__)[0] + expand('ftplugin/bin_deopletefs/deopletefs.exe') )

        post_data = {
              "Row"      : -9999 # dummy row
            , "Col"      : -9999 # dummy col
            , "Line"     : ''    # dummy line
            , "FilePath" : self.filePath
            , "Source"   : '\n'.join( getlines( self.vim ) )
            , "Init"     : 'dummy_init'
        }
        
        self.util = Util(fsc_path, 20, json.dumps(post_data))
        self.util.start()


    def on_event(self, context):

        if context['event'] == 'Init':

            start = time.time()
            self.vim.command("echo '*** deopletefs initializing... ***'")

            self.util.read()

            elapsed_time = time.time() - start
            self.vim.command("echo 'finish initialize! ( time : " + str(round(elapsed_time,6)) + " s )'")


            post_data = {
                  "Row"      : -9999 # dummy row
                , "Col"      : 1
                , "Line"     : ''
                , "FilePath" : self.filePath
                , "Source"   : '\n'.join( getlines( self.vim ) )
                , "Init"     : 'real_init'
            }

            self.util.send(json.dumps(post_data))


        elif context['event'] == 'BufWritePost':
            pass
        else:
            pass


    def get_complete_position(self, context):
        m = re.search( r'\w*$', context['input'] )
        return m.start() if m else -1


    def gather_candidates(self, context):
        try:

            post_data = {
                  "Row"      : context['position'][1]
                , "Col"      : context['complete_position'] - 1
                , "Line"     : context['input']
                , "FilePath" : self.filePath
                , "Source"   : '\n'.join( getlines( self.vim ) )
                , "Init"     : 'false'
            }

            self.util.send(json.dumps(post_data))
            messages = self.util.read()

            return [
                {
                      "word": json_data['word']
                    , "info": '\n'.join( functools.reduce ( lambda a , b : a + b , json_data['info'] ) )
                }
                for json_data in [ json.loads(s) for s in messages ]
            ]

        except Exception as e:
            return [ str(e) ]


class Util(threading.Thread):

    def __init__(self, exe_path, timeOut_s, txt):
        super(Util, self).__init__()

        self.exe_path  = exe_path
        self.txt       = txt
        self.timeOut_s = timeOut_s

        self.event     = threading.Event()

        self.lines     = queue.Queue()


    def run(self):

        # launch deopletefs
        command      = [ 'mono', self.exe_path ]
        opts         = { 'stdin': subprocess.PIPE, 'stdout': subprocess.PIPE, 'stderr': subprocess.PIPE, 'universal_newlines': True }
        self.process = subprocess.Popen( command , **opts )
        atexit.register(lambda: self.process.kill())

        # initialize deopletefs
        self.send(self.txt)

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
