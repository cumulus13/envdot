"""
set_or_dict - parse loose '{...}' text into a set or a dict.

Rules
-----
* '{}' / '' / '{ }'             -> {}   (empty dict, like Python)
* every element has a ':' pair   -> dict
* otherwise                      -> set
* Backslash is ALWAYS literal (Windows paths are safe, no \\n \\t corruption).
* Quoted values stay str verbatim; unquoted plain ints / floats convert.
  Leading zeros, '+' prefix and >18-digit numbers stay str (zip codes, phones, ids).
* Nested containers are kept as raw str.
* Malformed input (unterminated quote, unclosed bracket) raises ValueError.
* Non-str input is returned unchanged.
"""
import re

__all__ = ["set_or_dict"]

_INT = re.compile(r"-?(?:0|[1-9][0-9]*)\Z")
_FLOAT = re.compile(r"-?(?:0|[1-9][0-9]*)?\.[0-9]+(?:[eE][+-]?[0-9]+)?\Z")
_MAX_DIGITS = 18

_OPEN = ("(", "[", "{")
_CLOSE = (")", "]", "}")
_QUOTES = ("'", '"')
_TOKEN_START = ("", ",", ":")   # last significant char before a new token begins


def _scan(s, sep, maxsplit=-1):
    """Split s on `sep`, ignoring separators inside quotes or brackets.

    - Backslash is literal; a quote ends at the next identical quote char.
    - A quote opens only at the start of a token (so it's stays literal).
    - A bracket opens only at the start of a token (so C:\\Program Files (x86)\\a
      stays literal).
    - When sep == ':' a Windows drive-letter colon (C:\\) is not a separator.
    """
    parts, start, quote, depth, prev = [], 0, None, 0, ""   # prev = last non-space char
    n = len(s)
    for i, ch in enumerate(s):
        if quote:
            if ch == quote:
                quote, prev = None, ch
            continue
        if ch in _QUOTES and (prev in _TOKEN_START or prev in _OPEN):
            quote = ch
        elif ch in _OPEN and (depth > 0 or prev in _TOKEN_START):
            depth += 1
        elif ch in _CLOSE:
            if depth > 0:
                depth -= 1
        elif ch == sep and depth == 0 and maxsplit != 0:
            drive = (
                sep == ":" and i >= 1 and i + 1 < n and s[i + 1] == "\\"
                and s[i - 1].isascii() and s[i - 1].isalpha()
                and (i == 1 or not s[i - 2].isalnum())
            )
            if not drive:
                parts.append(s[start:i])
                start = i + 1
                maxsplit -= 1
                prev = ch
                continue
        if not ch.isspace():
            prev = ch
    if quote:
        raise ValueError("unterminated quote")
    if depth:
        raise ValueError("unbalanced brackets")
    parts.append(s[start:])
    return parts


def _scalar(tok):
    tok = tok.strip()
    if len(tok) >= 2 and tok[0] == tok[-1] and tok[0] in _QUOTES:
        return tok[1:-1]                      # quoted -> str, verbatim
    if _INT.match(tok) and len(tok) <= _MAX_DIGITS + 1:
        return int(tok)
    if _FLOAT.match(tok) and len(tok) <= 40:
        return float(tok)
    return tok                                # bare word / path / container text


def set_or_dict(text, pair_in_quotes=False):
    """Parse '{a, b}' -> set, '{a: 1, b: 2}' -> dict, '{}' -> {}.

    pair_in_quotes=True treats {'aaa:111', 'bbb:222'} as a dict
    (each quoted element is one key:value pair).
    """
    if not isinstance(text, str):
        return text
    text = text.strip()
    if len(text) >= 2 and text.startswith("{") and text.endswith("}"):
        text = text[1:-1].strip()
    if not text:
        return {}

    elements = [e.strip() for e in _scan(text, ",") if e.strip()]
    if not elements:
        return {}

    def pair(e):
        kv = _scan(e, ":", 1)
        if len(kv) == 2:
            return kv
        if pair_in_quotes and len(e) >= 2 and e[0] == e[-1] and e[0] in _QUOTES:
            kv = _scan(e[1:-1], ":", 1)
            if len(kv) == 2:
                return kv
        return None

    pairs = [pair(e) for e in elements]
    if all(p is not None for p in pairs):
        return {_scalar(k): _scalar(v) for k, v in pairs}
    return {_scalar(e) for e in elements}


if __name__ == "__main__":
    f = set_or_dict
    ok = lambda got, exp: (got == exp) or (_ for _ in ()).throw(AssertionError(f"{got!r} != {exp!r}"))
    def raises(t):
        try: f(t)
        except ValueError: return True
        return False

    ok(f("{}"), {}); ok(f(""), {}); ok(f("{ }"), {}); ok(f("{,}"), {})
    ok(f("{a, b, c}"), {"a", "b", "c"})
    ok(f("{aaa:111, bbb:222}"), {"aaa": 111, "bbb": 222})
    ok(f("{'a,b': 1, 'c': 2}"), {"a,b": 1, "c": 2})
    ok(f("{'a:b': 1}"), {"a:b": 1})
    ok(f("{'a:b', 'c:d'}"), {"a:b", "c:d"})
    ok(f("{'u': 'http://x:80'}"), {"u": "http://x:80"})
    ok(f("{u: http://x:80}"), {"u": "http://x:80"})
    ok(f("{name: it's, x: 1}"), {"name": "it's", "x": 1})
    ok(f('{"k": \'say "hi"\'}'), {"k": 'say "hi"'})
    ok(f("{-1: -2.5}"), {-1: -2.5})
    ok(f("{1,2,3}"), {1, 2, 3})
    ok(f("{'111': 111}"), {"111": 111})
    ok(f("{zip: 007}"), {"zip": "007"})
    ok(f("{n: +628123}"), {"n": "+628123"})
    ok(f("{n: " + "9" * 5000 + "}"), {"n": "9" * 5000})
    ok(f("{a:1, b}"), {"a:1", "b"})
    ok(f("{a,,b,}"), {"a", "b"})
    ok(f("{'x': [1,2], y: (3, 4)}"), {"x": "[1,2]", "y": "(3, 4)"})
    ok(f("{a:1, a:2}"), {"a": 2})
    # Windows paths
    ok(f(r"{p: C:\Users\x}"), {"p": r"C:\Users\x"})
    ok(f(r"{p:C:\x}"), {"p": r"C:\x"})
    ok(f(r"{'p': 'C:\new\table'}"), {"p": r"C:\new\table"})
    ok(f(r"{'p': 'C:\temp\', 'q': 1}"), {"p": "C:\\temp\\", "q": 1})
    ok(f(r'{"p": "C:\dir\"}'), {"p": "C:\\dir\\"})
    ok(f(r"{'C:\a', 'D:\b'}"), {r"C:\a", r"D:\b"})
    ok(f(r"{C:\a, D:\b}"), {r"C:\a", r"D:\b"})
    ok(f(r"{C:\a: 1}"), {r"C:\a": 1})
    ok(f(r"{C:\dir\sub: D:\x\y, e: 2}"), {r"C:\dir\sub": r"D:\x\y", "e": 2})
    ok(f(r"{p: C:\Program Files (x86)\a, q: 1}"), {"p": r"C:\Program Files (x86)\a", "q": 1})
    ok(f(r"{p: C:\a[1.txt, q: 1}"), {"p": r"C:\a[1.txt", "q": 1})
    ok(f(r"{'\\srv\share\', '\\srv\b\'}"), {"\\\\srv\\share\\", "\\\\srv\\b\\"})
    ok(f("{'aaa:111','bbb:222'}", pair_in_quotes=True), {"aaa": 111, "bbb": 222})
    ok(f(None), None); ok(f(5), 5)
    assert raises("{a: 'open}") and raises("{a: [1, 2}") and raises("{'x}")

    import random
    al = ["C:\\Users\\x\\", "D:\\n\\t\\", "a,b", "a:b", "it's", 'say "hi"',
          "\\\\srv\\share\\", "plain", "x y", "\\", "C:\\a[1", "(x86)"]
    random.seed(1)
    for _ in range(20000):
        keys = random.sample(al, random.randint(1, 4))
        d = {k: random.choice(al) for k in keys}
        if any("'" in s and '"' in s for s in list(d) + list(d.values())):
            continue
        q = lambda s: f"'{s}'" if "'" not in s else f'"{s}"'
        t = "{" + ", ".join(f"{q(k)}: {q(v)}" for k, v in d.items()) + "}"
        assert f(t) == d, t
    print("all tests passed")
    
    string1 = "{aaa, bbb, ccc}"
    string2 = "{'aaa', 'bbb', 'ccc'}"
    string3 = '{"aaa", "bbb", "ccc"}'
    string4 = "{1:aaa, 2:bbb, 3:ccc}"
    string5 = "{1:'aaa', 2:'bbb', 3:'ccc'}"
    string6 = '{1:"aaa", 2:"bbb", 3:"ccc"}'
    string7 = " {aaa, bbb, ccc} "
    string8 = " {'aaa', 'bbb', 'ccc'} "
    string9 = ' {"aaa", "bbb", "ccc"} '
    string10 = " {1:aaa, 2:bbb, 3:ccc} "
    string11 = " {1:'aaa', 2:'bbb', 3:'ccc'} "
    string12 = ' {1:"aaa", 2:"bbb", 3:"ccc"} '
    string13 = " {'1':aaa, '2':bbb, '3':ccc} "
    string14 = " {'1':'aaa', '2':'bbb', '3':'ccc'} "
    string15 = ' {"1":"aaa", "2":"bbb", "3":"ccc"} '

    string16 = "{'aaa:111', 'bbb:222', 'ccc:333'}"
    string17 = "{'aaa', 'bbb', 'ccc:333'}"


    result1 = set_or_dict(string1)
    print(type(result1))
    print(result1)
    # Output: <class 'set'>
    # Output: {'bbb', 'ccc', 'aaa'}

    print("---")

    result2 = set_or_dict(string2)
    print(type(result2))
    print(result2)
    # Output: <class 'dict'>
    # Output: {1: 'aaa', 2: 'bbb', 3: 'ccc'}

    result3 = set_or_dict(string3)
    print(type(result3))
    print(result3)

    result4 = set_or_dict(string4)
    print(type(result4))
    print(result4)

    result5 = set_or_dict(string5)
    print(type(result5))
    print(result5)

    result6 = set_or_dict(string6)
    print(type(result6))
    print(result6)

    result7 = set_or_dict(string7)
    print(type(result7))
    print(result7)

    result8 = set_or_dict(string8)
    print(type(result8))
    print(result8)

    result9 = set_or_dict(string9)
    print(type(result9))
    print(result9)

    result10 = set_or_dict(string10)
    print(type(result10))
    print(result10)

    result11 = set_or_dict(string11)
    print(type(result11))
    print(result11)

    result12 = set_or_dict(string12)
    print(type(result12))
    print(result12)

    result13 = set_or_dict(string13)
    print(type(result13))
    print(result13)

    result14 = set_or_dict(string14)
    print(type(result14))
    print(result14)

    result15 = set_or_dict(string15)
    print(type(result15))
    print(result15)

    result16 = set_or_dict(string16)
    print(type(result16))
    print(result16)

    result17 = set_or_dict(string17)
    print(type(result17))
    print(result17)


