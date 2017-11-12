augroup deoplete-fsharp
    let g:deoplete#max_list = 1000
    set previewheight=5

    autocmd!
    " autocmd  BufNewFile,BufRead            *.fsx  call LaunchFSI()
    " autocmd  BufNewFile,BufRead            *.fsx  command! -buffer QUICKRUNfs :call PyQuickRunFs()
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
    let l = ['///callmekohei'] + getline(1,'$')
    call writefile( l , s:get_temporary_fileName() )
endfunction

function! s:update_completeDone() abort
    let s = getline('.')
    let n = match(s,'\v(\s*)open')
    if n == 0
        call s:write_temporary_file()
    endif
endfunction
