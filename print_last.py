with open('build_test4.log', 'r', encoding='utf-16le', errors='replace') as f:
    lines = f.readlines()
for line in lines[-20:]:
    print(line.strip())
