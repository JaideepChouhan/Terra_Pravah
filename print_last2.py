with open('test_service_out.log', 'r', errors='ignore') as f:
    text = f.read()
    
# since PS might inject null bytes or whatever
clean_text = text.replace('\x00', '')
lines = clean_text.split('\n')
for line in lines[-20:]:
    print(line)
