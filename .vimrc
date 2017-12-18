set autoindent                                                                                                                                         
colorscheme monokai                                                                                                                                    
set number                                                                                                                                             
set ic                                                                                                                                                       
                                                                                                                                                       
call plug#begin('~/.vim/plugged')                                                                                                                      
  Plug 'junegunn/fzf', { 'dir': '~/.fzf', 'do': './install --all' }                                                                                    
  Plug 'junegunn/fzf.vim'                                                                                                                              
  Plug 'craigemery/vim-autotag'                                                                                                                        
  Plug 'vim-airline/vim-airline'                                                                                                                       
  Plug 'vim-airline/vim-airline-themes'                                                                                                                
  "  Plug 'korniltsev/cscope_maps'
call plug#end()                                                                                                                                        
                                                                                                                                                       
let g:airline_theme="deus"                                                                                                                             
map <silent> <C-f> :BTags<CR>                                                                                                                          
map <silent> <C-p> :FZF<CR>  
