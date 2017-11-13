@echo off

git clone --depth 1 https://github.com/callmekohei/deopletefs_win32
move deopletefs_win32 ftplugin

powershell -Command "(new-object System.Net.WebClient).Downloadfile('https://raw.githubusercontent.com/fsharp/vim-fsharp/master/syntax/fsharp.vim', 'fsharp.vim')"
mkdir syntax
move fsharp.vim syntax



