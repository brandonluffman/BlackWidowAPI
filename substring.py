def link_strings(strings):
    groups = {}
    for string in strings:
        linked = False
        for group in groups:
            for other_string in group:
                if string in other_string:
                    group.append(string)
                    linked = True
                    break
            if linked:
                break
        if not linked:
            groups.append([string])
    return groups

strings = ['hello', 'lo', 'world', 'or', 'h', 'ell']
print(link_strings(strings))