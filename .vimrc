set nocompatible
filetype off

set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
Plugin 'VundleVim/Vundle.vim'
Plugin 'scrooloose/nerdtree'
Bundle 'L9'
Bundle 'FuzzyFinder'
call vundle#end()
filetype plugin indent on

" open nerdtree and focus next buffer after nerdtree
autocmd VimEnter * NERDTree
autocmd VimEnter * wincmd p
"
let g:fuf_file_exclude = '\v\~$|\.o$|\.exe$|\.bak$|\.swp$|\.class$'
