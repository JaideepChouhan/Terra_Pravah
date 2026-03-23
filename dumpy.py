with open('test2_out.log', 'r', encoding='utf-16le', errors='ignore') as f:
    text = f.read()
    
# Remove nulls if any
clean_text = text.replace('\0', '')
print(clean_text)
