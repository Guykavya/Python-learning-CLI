- Thinking `import counter` reuses the running script. The running script is cached as `"__main__"`,
  so the name `"counter"` is not found and the file runs again.
- Forgetting the second `loading counter as counter` line, or putting it after `loading helper`.
  `helper` imports `counter` on its first line, before its own print.
- Thinking the second run also enters the `if __name__ == "__main__":` block. Its name is `counter`.
- Thinking both functions share one `hits` list. Each module object has its own globals.
