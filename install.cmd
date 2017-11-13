@echo off

git clone --depth 1 https://github.com/callmekohei/deopletefs_win32
move deoplete-fsharp-bin ftplugin

powershell -Command "(new-object System.Net.WebClient).Downloadfile('https://raw.githubusercontent.com/fsharp/vim-fsharp/master/syntax/fsharp.vim', 'fsharp.vim')"
mkdir syntax
move fsharp.vim syntax



