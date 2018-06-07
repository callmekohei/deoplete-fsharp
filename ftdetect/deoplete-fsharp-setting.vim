augroup deoplete-fsharp
    set previewheight=5
    " for fast rendering of fsharp.vim syntax
    set regexpengine=1
    autocmd!
    autocmd  BufNewFile,BufRead *.fs,*.fsi,*.fsx  set filetype=fsharp
    autocmd  BufNewFile,BufRead *.fs,*.fsi,*.fsx  call s:write_temporary_file()
    autocmd  BufWinLeave        *.fs,*.fsi,*.fsx  call s:cleanup_temporary_file()
    autocmd  CompleteDone       *.fs,*.fsi,*.fsx  call s:update_completeDone()
    autocmd  InsertLeave        *.fs,*.fsi,*.fsx  call s:write_temporary_file()
    autocmd  InsertEnter        *.fs,*.fsi,*.fsx  call s:write_temporary_file()
    autocmd  BufWrite           *.fs,*.fsi,*.fsx  call s:write_temporary_file()
augroup END

function! s:get_temporary_fileName() abort
    return substitute( expand('%:p:r') . '_deoplete-fsharp_temporary_file.fsx' , '\#', '\\#' , 'g' )
endfunction

function! s:cleanup_temporary_file() abort
    if has('win32') || has('win32unix')
        execute ":silent !del " . s:get_temporary_fileName()
    else
        execute ":silent !rm " . s:get_temporary_fileName()
    endif
endfunction

function! s:write_temporary_file() abort
    call writefile( getline(1,'$') , s:get_temporary_fileName() )
endfunction

function! s:update_completeDone() abort
    let s = getline('.')
    let n = match(s,'\v(\s*)open')
    if n == 0
        call s:write_temporary_file()
    endif
endfunction

" see also:
" quick-run can not execute well at vim's launch. #175
" https://github.com/thinca/vim-quickrun/issues/175
if has('nvim')
    if exists('g:quickrun_config.fsharpCheck')
        augroup fsharpCheck

            let s:err     = '%f(%l\,%c):\ %m'
            let s:blank01 = '%-G %.%#'
            let s:blank02 = '%-G'
            let s:invalid = '%-G%[%^/]%.%#'

            let s:lst = [
                \   s:err
                \ , s:blank01
                \ , s:blank02
                \ , s:invalid
                \ ]

            autocmd!
            autocmd FileType fsharp let &errorformat = join( s:lst , ',' )
            autocmd BufWinEnter  *.fsx  call quickrun#run( g:quickrun_config.fsharpCheck )
            autocmd BufWritePost *.fsx  call quickrun#run( g:quickrun_config.fsharpCheck )
        augroup end
    endif
endif
