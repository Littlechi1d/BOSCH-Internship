def check_string(string):

    new_string = ''
    for item in string:
        if (item >='a' and item <='f') or (item >='A' and item <='F') or (item >='0' and item <='9') or (item == '.'):
            new_string += item
        else:
            continue
    
    return new_string

if __name__ == "__main__":
    output = check_string('a1 23 234 > ?!@ ger fuj 7')
    print(output)