with open('build_result.txt', 'r', encoding='utf-16le') as f:
    text = f.read()
with open('proper_error.txt', 'w', encoding='utf-8') as f:
    f.write(text)
