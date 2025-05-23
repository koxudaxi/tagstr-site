import pprint
import re
import textwrap

from tagstr_site.tagtyping import Decoded, Interpolation
from tagstr_site.taglib import decode_raw
from tagstr_site.tstring import Template


class PythonCode(str):
    def __new__(cls, code: list[str]):
        return super().__new__(cls, textwrap.dedent(''.join(code)))


def param_list(names):
    return ', '.join(names)


# FIXME: the only whitespace we currently handle is spaces, not tabs
INITIAL_WHITESPACE_RE = re.compile(r'^( +)')


def code(template: Template) -> PythonCode:
    text = []
    indent_level = None

    def indent(suite):
        lines = []
        for i, line in enumerate(suite.split('\n')):
            lines.append(f'{" " * (indent_level) if i > 0 else ""}{line}\n')
        return ''.join(lines)

    for arg in template.args:
        match arg:
            case str():
                lines = arg.split('\n')
                for line in lines:
                    # Count the initial whitespace, with the side effect
                    # that the last one counted counts 
                    if m := INITIAL_WHITESPACE_RE.search(line):
                        indent_level = len(m.group(0))
                text.append(arg)
            case getvalue, _, _, formatspec:
                value = getvalue()
                # The following can be considered to be a creative use (or
                # abuse) of formatspec. Note that we might want to support use
                # of a lexically scoped var here with the format spec - unlike
                # params/pretty, this functionality cannot be handled by a
                # function in the expression, as we see with
                # code"...{param_list(params)}..."
                match formatspec:
                    case 'params':
                        text.append(param_list(value))
                    case 'pretty':
                        text.append(indent(pprint.pformat(value)))
                    case _:
                        # NOTE: also handles nested code tag usage
                        text.append(indent(str(value)))
    return PythonCode(text)


def useit():
    args = ['x', 'y', 'z']
    results = {'a': 2, 'b': 3, 'c': 5, 'd': 7, 'e': 11}
    print(code(t"""
            def f({args:params}):
                return \\
                    {results:pretty}
        """))


    if __name__ == '__main__':
        useit()
