# ~/.bashrc: executed by bash(1) for non-login shells.

case $- in
    *i*) ;;
      *) return;;
esac
HISTCONTROL=ignoreboth
shopt -s histappend
HISTSIZE=1000
HISTFILESIZE=2000
shopt -s checkwinsize

[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi
case "$TERM" in
    xterm-color|*-256color) color_prompt=yes;;
esac

if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
	color_prompt=yes
    else
	color_prompt=
    fi
fi

if [ "$color_prompt" = yes ]; then
    # PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\[\033[01;34m\]\w\[\033[00m\]\$ '
else
    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
fi
unset color_prompt force_color_prompt

# If this is an xterm set the title to user@host:dir
case "$TERM" in
xterm*|rxvt*)
    PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\u@\h: \w\a\]$PS1"
    ;;
*)
    ;;
esac

if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi

if [ $TILIX_ID ] || [ $VTE_VERSION ]; then
  source /etc/profile.d/vte.sh
fi

# ========================================
# VARIABLES AND SETTINGS
# ========================================

# display git active branch in the prompt
parse_git_branch() {
     git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/(\1)/'
}
export PS1="${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u\[\033[00m\] \[\033[01;34m\]\w\[\033[00m\] \[\e[91m\]\$(parse_git_branch)\[\e[00m\]\$ "


# enable ctrl-s in VIM
stty -ixon
PROMPT_DIRTRIM=2
export EDITOR=vim

# ENV VARIABLES
export APP_DM="$HOME/Projects/deepmk"

# --------------------
# FZF SETTINGS
export FZF_DEFAULT_COMMAND='fd -H --exclude={.git,.idea,.vscode,node_modules}'
export FZF_ALT_C_OPTS="--preview 'tree -C {} | head -200'"
export FZF_COMPLETION_TRIGGER=',,'

_fzf_comprun() {
  local command=$1
  shift
  case "$command" in
    ffcd)           fzf "$@" --preview 'tree -C {} | head -200' ;;
    ffssh)          fzf "$@" --preview 'dig {}' ;;
    *)            fzf "$@" ;;
  esac
}

# hh
_fzf_complete_hh() {
  _fzf_complete --multi --reverse --prompt="hh> " -- "$@" < <(
    ls /home/scheidt/bin/help/
  )
}
[ -n "$BASH" ] && complete -F _fzf_complete_hh -o default -o bashdefault hh

# snip
C_OPT='model'

_SNIP_DIR=$FS_SNIP
_fzf_complete_snip() {
  C_OPT=$3
   if [[ $C_OPT == 'snip' ]]; then
      _fzf_complete --multi --reverse --prompt="topic> " -- "$@" < <(
        ls "$_SNIP_DIR"
      )
   elif [[ $C_OPT != 'snip' ]]; then
      _fzf_complete --multi --reverse --prompt="snippet> " -- "$@" < <(
        ls "$_SNIP_DIR/$C_OPT"
      )
   fi
}
[ -n "$BASH" ] && complete -F _fzf_complete_snip -o default -o bashdefault snip

# ////////////////////////////////////////


[ -f ~/.fzf.bash ] && source ~/.fzf.bash

export DENO_INSTALL="/home/scheidt/.deno"
export PATH="$DENO_INSTALL/bin:$PATH"
export PATH="$HOME/go/bin:$PATH"

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

#THIS MUST BE AT THE END OF THE FILE FOR SDKMAN TO WORK!!!
export SDKMAN_DIR="$HOME/.sdkman"
[[ -s "$HOME/.sdkman/bin/sdkman-init.sh" ]] && source "$HOME/.sdkman/bin/sdkman-init.sh"

# Created by `pipx` on 2024-04-30 23:47:47
export PATH="$PATH:/home/scheidt/.local/bin"
. "$HOME/.cargo/env"
