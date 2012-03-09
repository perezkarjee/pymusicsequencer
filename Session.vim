let SessionLoad = 1
if &cp | set nocp | endif
let s:cpo_save=&cpo
set cpo&vim
map! <F4> <F4>
map! <Home> <Home>
map! <End> <End>
map! <S-F4> <S-F4>
map! <S-F3> <S-F3>
map! <S-F2> <S-F2>
map! <S-F1> <S-F1>
map! <F3> <F3>
map! <F2> <F2>
map! <F1> <F1>
imap <C-PageDown> L$
imap <C-PageUp> H
cnoremap <C-F4> c
inoremap <C-F4> c
cnoremap <C-Tab> w
inoremap <C-Tab> w
cnoremap <M-Space> :simalt ~
inoremap <M-Space> :simalt ~
cmap <S-Insert> +
imap <S-Insert> 
noremap  gggHG
vnoremap  "+y
noremap  
nnoremap  :update
vnoremap  :update
onoremap  :update
nmap  "+gP
omap  "+gP
vnoremap  "+x
noremap  
noremap  u
noremap # #
inoremap Â  :simalt ~
cnoremap Â  :simalt ~
map Q gq
nmap <silent> \c <Plug>Traditionalj
nmap <silent> \x <Plug>Traditional
vmap <silent> \c <Plug>VisualTraditionalj
vmap <silent> \x <Plug>VisualTraditional
nmap gx <Plug>NetrwBrowseX
map <F2> :w!
map <F3> :mks!
map <F9> :w:!E:\python26\python "%"
map <F4> <F4>
noremap <Plug>Comment :call EnhancedCommentify('', 'comment')
noremap <Plug>DeComment :call EnhancedCommentify('', 'decomment')
noremap <Plug>Traditional :call EnhancedCommentify('', 'guess')
noremap <Plug>FirstLine :call EnhancedCommentify('', 'first')
noremap <Plug>VisualComment :call EnhancedCommentify('', 'comment',				    line("'<"), line("'>"))
noremap <Plug>VisualDeComment :call EnhancedCommentify('', 'decomment',				    line("'<"), line("'>"))
noremap <Plug>VisualTraditional :call EnhancedCommentify('', 'guess',				    line("'<"), line("'>"))
noremap <Plug>VisualFirstLine :call EnhancedCommentify('', 'first',				    line("'<"), line("'>"))
map <F8> :w:!compilepyrex.py "%"
map <Home> <Home>
map <End> <End>
map <S-F4> <S-F4>
map <S-F3> <S-F3>
map <S-F2> <S-F2>
map <S-F1> <S-F1>
map <F1> <F1>
nmap <S-Insert> "+gP
nmap <C-PageDown> L$
nmap <C-PageUp> H
vmap <C-PageDown> L$
vmap <C-PageUp> H
nnoremap <silent> <Plug>NetrwBrowseX :call netrw#NetBrowseX(expand("<cWORD>"),0)
noremap <C-F4> c
noremap <C-Tab> w
noremap <M-Space> :simalt ~
vmap <S-Insert> 
vnoremap <BS> d
vmap <C-Del> "*d
vnoremap <S-Del> "+x
vnoremap <C-Insert> "+y
omap <S-Insert> "+gP
cnoremap  gggHG
inoremap  gggHG
inoremap  :update
inoremap  u
cmap  +
inoremap  
inoremap  u
inoremap # X<BS>#
noremap Â  :simalt ~
imap <silent> \c <Plug>Traditionalji
imap <silent> \x <Plug>Traditional
let &cpo=s:cpo_save
unlet s:cpo_save
set autoindent
set background=dark
set backspace=indent,eol,start
set backup
set balloonexpr=eclim#util#Balloon(eclim#util#GetLineError(line('.')))
set diffexpr=MyDiff()
set encoding=utf-8
set expandtab
set fileencodings=ucs-bom,utf-8,default,latin1
set formatoptions=tcroq
set guifont=µ¸¿òÃ¼:h9:cHANGEUL
set helplang=En
set history=50
set hlsearch
set iminsert=0
set imsearch=0
set incsearch
set keymodel=startsel,stopsel
set omnifunc=syntaxcomplete#Complete
set noremap
set ruler
set runtimepath=~/vimfiles,C:\\Program\ Files\\Vim/vimfiles,C:\\Program\ Files\\Vim\\vim72,C:\\Program\ Files\\Vim/vimfiles/after,~/vimfiles/after,C:/Program\ Files/Vim/vimfiles/eclim,C:/Program\ Files/Vim/vimfiles/eclim/after
set selection=exclusive
set selectmode=mouse,key
set sessionoptions=blank,buffers,curdir,folds,help,localoptions,options,resize,unix,winpos,winsize
set shiftround
set shiftwidth=4
set shortmess=aoO
set smartindent
set smarttab
set softtabstop=4
set whichwrap=b,s,<,>,[,]
set wildignore=*.pyc
set window=49
let s:so_save = &so | let s:siso_save = &siso | set so=0 siso=0
let v:this_session=expand("<sfile>:p")
silent only
cd C:\drumsynth
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +275 TheorySequencer.py
badd +43 asd.py
badd +1 pysynth.py
badd +58 exportmy.py
badd +412 simpleAdv.py
badd +3 simpleMud.py
badd +2041 digdig.py
badd +219 chunkhandler.pyx
badd +4588 simpleConstruct.py
badd +47 cpart.c
badd +18 cpart.h
badd +3252 chunk.pyx
badd +1 glut.py
silent! argdel *
set lines=50 columns=165
winpos 1 0
edit simpleConstruct.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winheight=1 winwidth=1
argglobal
setlocal keymap=
setlocal noarabic
setlocal autoindent
setlocal balloonexpr=
setlocal nobinary
setlocal bufhidden=
setlocal buflisted
setlocal buftype=
setlocal nocindent
setlocal cinkeys=0{,0},0),:,!^F,o,O,e
setlocal cinoptions=
setlocal cinwords=if,else,while,do,for,switch
setlocal comments=s1:/*,mb:*,ex:*/,://,b:#,:XCOMM,n:>,fb:-
setlocal commentstring=#%s
setlocal complete=.,w,b,u,t,i
setlocal completefunc=
setlocal nocopyindent
setlocal nocursorcolumn
setlocal nocursorline
setlocal define=
setlocal dictionary=
setlocal nodiff
setlocal equalprg=
setlocal errorformat=
setlocal expandtab
if &filetype != 'python'
setlocal filetype=python
endif
setlocal foldcolumn=0
setlocal foldenable
setlocal foldexpr=0
setlocal foldignore=#
setlocal foldlevel=0
setlocal foldmarker={{{,}}}
setlocal foldmethod=manual
setlocal foldminlines=1
setlocal foldnestmax=20
setlocal foldtext=foldtext()
setlocal formatexpr=
setlocal formatoptions=tcroq
setlocal formatlistpat=^\\s*\\d\\+[\\]:.)}\\t\ ]\\s*
setlocal grepprg=
setlocal iminsert=0
setlocal imsearch=0
setlocal include=s*\\(from\\|import\\)
setlocal includeexpr=substitute(v:fname,'\\.','/','g')
setlocal indentexpr=GetPythonIndent(v:lnum)
setlocal indentkeys=0{,0},:,!^F,o,O,e,<:>,=elif,=except
setlocal noinfercase
setlocal iskeyword=@,48-57,_,128-167,224-235
setlocal keywordprg=
setlocal nolinebreak
setlocal nolisp
setlocal nolist
setlocal makeprg=
setlocal matchpairs=(:),{:},[:]
setlocal modeline
setlocal modifiable
setlocal nrformats=octal,hex
set number
setlocal number
setlocal numberwidth=4
setlocal omnifunc=pythoncomplete#Complete
setlocal path=
setlocal nopreserveindent
setlocal nopreviewwindow
setlocal quoteescape=\\
setlocal noreadonly
setlocal norightleft
setlocal rightleftcmd=search
setlocal noscrollbind
setlocal shiftwidth=4
setlocal noshortname
setlocal smartindent
setlocal softtabstop=4
setlocal nospell
setlocal spellcapcheck=[.?!]\\_[\\])'\"\	\ ]\\+
setlocal spellfile=
setlocal spelllang=en
setlocal statusline=
setlocal suffixesadd=.py
setlocal swapfile
setlocal synmaxcol=3000
if &syntax != 'python'
setlocal syntax=python
endif
setlocal tabstop=8
setlocal tags=
setlocal textwidth=0
setlocal thesaurus=
setlocal nowinfixheight
setlocal nowinfixwidth
setlocal wrap
setlocal wrapmargin=0
silent! normal! zE
let s:l = 4588 - ((24 * winheight(0) + 24) / 49)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
4588
normal! 012l
lcd C:\drumsynth
if exists('s:wipebuf')
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=aoO
let s:sx = expand("<sfile>:p:r")."x.vim"
if file_readable(s:sx)
  exe "source " . s:sx
endif
let &so = s:so_save | let &siso = s:siso_save
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
