" show line numbers:
set number

set tabstop=4
set shiftwidth=4
set expandtab

" change line number style 
highlight LineNr term=bold cterm=NONE ctermfg=DarkGrey ctermbg=NONE gui=NONE guifg=DarkGrey guibg=NONE

" Enable use of the mouse for all modes
set mouse=a

" Display the cursor position on the last line of the screen or in the status
" line of a window
set ruler
" Always display the status line, even if only one window is displayed
set laststatus=2

" Use case insensitive search, except when using capital letters
set ignorecase
set smartcase

" open new window at right side
set splitright

" line move up and down
nmap <C-Down> :m +1<CR>
nmap <C-Up> :m -2<CR>


" ============
" KEY MAPPINGS
" ============

" [CTRL + ↑] Move line up (N,I)
nmap <C-Down> :m +1<CR>
" insert mode:
inoremap <C-Up> <Esc> :m -2<CR>i

" [CTRL + ↓] Move line down (N,I)
nmap <C-Up> :m -2<CR>
" insert mode:
inoremap <C-Down> <Esc> :m +1<CR>i

" [CTRL + y] Duplicate line (N,I)
nnoremap <C-Y> Yp
inoremap <C-Y> <Esc> Ypi

" [CTRL + s] Save file -> Need to add to .bashrc 'stty -ixon'
noremap <silent> <C-S>          :update<CR>
vnoremap <silent> <C-S>         <C-C>:update<CR>
inoremap <silent> <C-S>         <C-O>:update<CR>

" [CTRL + d] Delete entire line (N,I)
noremap <C-D> dd
inoremap <C-D> <Esc> ddi
inoremap DD <esc>dd

" [CTRL + c] copy selection to clipboard
vnoremap <C-C> :w !xclip -i -sel c<CR><CR>