import re


def delete_unclosed_blocks(line: str) -> str:
    """My approach:
    simplify task to boundary cases without either opening or closing or
    both parenthesis, then process cases with any combinations of them.
    """
    while True:
        if '(' not in line:
            return line
        elif ')' not in line:
            open_paren_index = line.index('(')
            return line[:open_paren_index]
        else:
            open_paren_index = line.rindex('(')
            close_paren_index = line.rindex(')')
            if open_paren_index < close_paren_index:
                return line
            elif open_paren_index > close_paren_index:
                line = line[:open_paren_index]


def delete_unclosed_blocks_regex(line: str) -> str:
    if '(' not in line:
        return line
    elif ')' not in line:
        open_paren_index = line.index('(')
        return line[:open_paren_index]
    else:
        return re.match(r'.*\)[^(]*', line).group(0)


if __name__ == '__main__':
    for func in (delete_unclosed_blocks, delete_unclosed_blocks_regex):
        fixtures = ({
            'input': 's',
            'expected': 's'
        }, {
            'input': ')s',
            'expected': ')s'
        }, {
            'input': '(s',
            'expected': '',
        }, {
            'input': '((s',
            'expected': ''
        }, {
            'input': '(s)',
            'expected': '(s)'
        }, {
            'input': 'a((b)c(d))',
            'expected': 'a((b)c(d))'
        }, {
            'input': '(a((b)(b',
            'expected': '(a((b)'
        }, {
            'input': 'a((b)((b',
            'expected': 'a((b)'
        }, )
        for fix in fixtures:
            exp = fix['expected']
            inp = fix['input']
            out = func(fix['input'])
            msg = f"Expected: '{exp}', input: '{inp}', output: '{out}', " \
                f"function: {func.__name__}"
            assert fix['expected'] == out, msg
