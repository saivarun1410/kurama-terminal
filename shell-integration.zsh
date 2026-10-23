# Source this from ~/.zshrc after building Kurama.
export PATH="${${(%):-%x}:A:h}:$PATH"
autoload -Uz add-zsh-hook

_kurama_before_command() {
  local command="${1:l}"
  local first="${command%% *}"
  if [[ "$first" == (sudo|ssh|sftp|scp|gpg|pass|op|security) ]] || [[ "$first" == read && "$command" == *-s* ]]; then
    _kurama_auto_privacy=1
    kurama privacy on
  fi
}

_kurama_after_command() {
  if [[ "${_kurama_auto_privacy:-0}" == 1 ]]; then
    _kurama_auto_privacy=0
    kurama privacy off
  fi
}

_kurama_on_exit() {
  kurama wave
}

add-zsh-hook preexec _kurama_before_command
add-zsh-hook precmd _kurama_after_command
add-zsh-hook zshexit _kurama_on_exit
kurama start
