#!/usr/bin/env python3

from pathlib import Path

FILES = [
    'Types.lean',
    'Funs.lean',
]

ROOT = Path('foo/SrcTranslated')

def run():
    for f in FILES:
      p = ROOT / f
      encoding = 'utf-8'
      s = p.read_text(encoding=encoding)
      patch(s)
      p.write_text(s, encoding=encoding)

def patch(s):
    pass


if __name__ == '__main__':
    run()
