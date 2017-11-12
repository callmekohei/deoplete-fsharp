@echo off

git clone --depth 1 https://github.com/callmekohei/deoplete-fsharp-bin.git
move deoplete-fsharp-bin ftplugin

curl -O https://raw.githubusercontent.com/fsharp/vim-fsharp/master/syntax/fsharp.vim
mkdir syntax
move fsharp.vim syntax



