# Tab completion for `learn` and `./learn`. Loaded from ~/.bashrc; `learn completion` prints the line.
_learn_complete() {
    local IFS=$'\n'
    COMPREPLY=($(compgen -W "$("${COMP_WORDS[0]}" _complete "$COMP_CWORD" "${COMP_WORDS[@]}" 2>/dev/null)" \
        -- "${COMP_WORDS[COMP_CWORD]}"))
}
complete -F _learn_complete learn ./learn
