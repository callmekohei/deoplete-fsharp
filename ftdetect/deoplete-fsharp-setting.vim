augroup deoplete-fsharp
    let g:deoplete#max_list = 1000
    set previewheight=5

    autocmd!
    autocmd  BufNewFile,BufRead            *.fsx  call LaunchFSI()
    autocmd  BufNewFile,BufRead            *.fsx  command! -buffer QUICKRUNfs :call PyQuickRunFs()
    autocmd  BufNewFile,BufRead *.fs,*.fsi,*.fsx  set filetype=fsharp
    autocmd  BufNewFile,BufRead *.fs,*.fsi,*.fsx  call s:create_temporary_file()
    autocmd  VimLeavePre        *.fs,*.fsi,*.fsx  call s:cleanup_temporary_file() 
    autocmd  VimLeave           *.fs,*.fsi,*.fsx  call s:cleanup()
    autocmd  CompleteDone       *.fs,*.fsi,*.fsx  call s:update_completeDone()
    autocmd  InsertLeave        *.fs,*.fsi,*.fsx  :silent execute ":write! !tee | (echo '// dummy line' && cat) > " . s:create_temporary_filePath()
    autocmd  InsertEnter        *.fs,*.fsi,*.fsx  :silent execute ":write! !tee | (echo '// dummy line' && cat) > " . s:create_temporary_filePath() 
    autocmd  BufWrite           *.fs,*.fsi,*.fsx  :silent execute ":write! !tee | (echo '// dummy line' && cat) > " . s:create_temporary_filePath()
augroup END

function! s:create_temporary_filePath() abort
    return substitute( expand('%:p:r') . '_deoplete-fsharp_temporary_file.fsx' , '\#', '\\#' , 'g' )
endfunction

function! s:create_temporary_file() abort
    execute ":silent write! !tee | (echo '// dummy line' && cat) > " . s:create_temporary_filePath() 
endfunction

function! s:cleanup_temporary_file() abort
    execute ":silent !rm " . s:create_temporary_filePath()
endfunction

function! s:cleanup() abort
    let pid = getpid()
    execute ":silent !ps -o pid -g" . pid . "| tail -n +4 | sort -r | xargs kill"
endfunction

function! s:update_completeDone() abort
    let s = getline('.')
    let n = match(s,'\v(\s*)open')
    if n == 0
        execute ":silent write! !tee | (echo '// dummy line' && cat) >  " . s:create_temporary_filePath() 
    endif
endfunction

