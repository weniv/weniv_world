s = [
    '   + -- + - + -   ',
    '   + --- + - +   ',
    '   + -- + - + -   ',
    '   + - + - + - +   '
]
word = ''
for code in s:
    bits = code.replace(' ', '').replace('+', '1').replace('-', '0')
    word += chr(int(bits, 2))
say(word)
