#!/bin/bash

git clone --depth 1 'https://github.com/callmekohei/deoplete-fsharp-bin.git'
mv deoplete-fsharp-bin ftplugin

mkdir syntax
wget 'https://raw.githubusercontent.com/fsharp/vim-fsharp/master/syntax/fsharp.vim' -P './syntax/'

