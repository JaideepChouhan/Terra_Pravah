with open('test2_out.log', 'r', encoding='utf-16le', errors='ignore') as f:
    text = f.read()

with open('test2_clean.txt', 'w', encoding='utf-8') as f:
    f.write(text)
