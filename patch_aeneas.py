#!/usr/bin/env python3
"""Apply post-extraction tweaks to the generated Lean files.

The patches below are hardcoded copies of `tweaks.substitutions` in
aeneas-config.yml (that YAML stays the human-readable source of truth; this
script does not parse it). Each entry is applied in order to every file:

    (LITERAL, find, replace)   -> str.replace(find, replace)
    (REGEX,   pattern, repl)   -> re.sub(pattern, repl, ...)   ($1 -> \\g<1>)

A patch that doesn't match a given file is a no-op -- many are specific to
either Types.lean or Funs.lean.
"""

import re
from pathlib import Path

ROOT = Path('foo/SrcTranslated')
FILES = ['Types.lean', 'Funs.lean']

LITERAL = 'literal'
REGEX = 'regex'

PATCHES = [
    # Disable linters for the auto-generated files.
    (LITERAL, 'open Aeneas Aeneas.Std Result ControlFlow Error\nset_option linter.dupNamespace false\nset_option linter.hashCommand false\nset_option linter.unusedVariables false\n',
              'set_option linter.style.headerAlt false\nset_option linter.style.header false\nset_option linter.style.longLine false\nset_option linter.style.setOption false\nset_option linter.style.whitespace false\nset_option linter.dupNamespace false\nset_option linter.hashCommand false\nset_option linter.unusedVariables false\n\nopen Aeneas Aeneas.Std Result ControlFlow Error\n'),

    # https://github.com/AeneasVerif/aeneas/issues/1043
    (REGEX, '\\n  map := fun[\\s\\S]*?(?=\\n  enumerate)',
            '\n  -- See https://github.com/AeneasVerif/aeneas/issues/1043'),
    (REGEX, '\\n  collect := fun[\\s\\S]*?(?=\\n\\})',
            '\n  -- See https://github.com/AeneasVerif/aeneas/issues/1043'),

    # https://github.com/AeneasVerif/aeneas/issues/1043
    (REGEX, 'next := core\\.iter\\.adapters\\.map\\.Map\\.Insts\\.CoreIterTraitsIteratorIterator\\.next[\\s\\S]*?(?=\\n  step_by)',
            'next := sorry -- See https://github.com/AeneasVerif/aeneas/issues/1043'),

    # https://github.com/Beneficial-AI-Foundation/SparsePostQuantumRatchet-verify/issues/102
    (REGEX, 'impl_def(\\s+[\\w.]+\\.Insts\\.ProstMessageMessage\\s*:[\\s\\S]*?):= \\{[\\s\\S]*?\\n\\}',
            'def\\g<1>:= sorry -- See https://github.com/Beneficial-AI-Foundation/SparsePostQuantumRatchet-verify/issues/102'),

    # Fix local variable `chain` shadowing module namespace `chain.Chain` in `send`.
    # https://github.com/Beneficial-AI-Foundation/SparsePostQuantumRatchet-verify/issues/101
    (LITERAL, 'let chain ←\n                    match val2.key with',
              "let chain' /- See https://github.com/Beneficial-AI-Foundation/SparsePostQuantumRatchet-verify/issues/101 -/ ←\n                    match val2.key with"),
    (LITERAL, 'let chain ←\n                match val2.key with',
              "let chain' /- See https://github.com/Beneficial-AI-Foundation/SparsePostQuantumRatchet-verify/issues/101 -/ ←\n                match val2.key with"),
    (LITERAL, 'chain.Chain.send_key chain i3',
              "chain.Chain.send_key chain' i3 /- #101 rename -/"),
    (LITERAL, 'chain.Chain.send_key chain i1',
              "chain.Chain.send_key chain' i1 /- #101 rename -/"),

    # Fix local variable `chain` shadowing module namespace `chain.Chain` in `recv`.
    # https://github.com/Beneficial-AI-Foundation/SparsePostQuantumRatchet-verify/issues/101
    (LITERAL, 'let chain ←\n                            match val5.key with',
              "let chain' /- See https://github.com/Beneficial-AI-Foundation/SparsePostQuantumRatchet-verify/issues/101 -/ ←\n                            match val5.key with"),
    (LITERAL, 'let chain ←\n                    match val3.key with',
              "let chain' /- See https://github.com/Beneficial-AI-Foundation/SparsePostQuantumRatchet-verify/issues/101 -/ ←\n                    match val3.key with"),
    (LITERAL, 'chain.Chain.into_pb chain\n',
              "chain.Chain.into_pb chain' /- #101 rename -/\n"),
    (LITERAL, 'chain.Chain.recv_key chain msg_key_epoch index',
              "chain.Chain.recv_key chain' msg_key_epoch index /- #101 rename -/"),

    # Fix local variable `v1` shadowing module namespace `v1.chunked.states` in `recv`.
    # https://github.com/Beneficial-AI-Foundation/SparsePostQuantumRatchet-verify/issues/101
    (LITERAL, 'let v1 := read_discriminant v\n      let i ← lift (IScalar.hcast .U8 v1)',
              "let v1' := read_discriminant v /- See https://github.com/Beneficial-AI-Foundation/SparsePostQuantumRatchet-verify/issues/101 -/\n      let i ← lift (IScalar.hcast .U8 v1')"),

    # Sorry merge closure FnOnce call_once assignments (Aeneas types them wrong).
    # https://github.com/AeneasVerif/aeneas/issues/1046
    (REGEX, 'call_once :=\\n    proto\\.pq_ratchet\\.\\S+\\.merge\\.closure\\S*\\.Insts\\.CoreOpsFunctionFnOnceTupleTupleTuple\\.call_once\\n    bytesbufbuf_implBufInst\\n}',
            'call_once := sorry -- See https://github.com/AeneasVerif/aeneas/issues/1046\n}'),

    # Sorry merge function bodies (broken Result.map with mistyped closures).
    # https://github.com/AeneasVerif/aeneas/issues/1046
    (REGEX, '(def proto\\.pq_ratchet\\.(?:pq_ratchet_state\\.Inner|v1_msg\\.InnerMsg|v1_state\\.InnerState)\\.merge\\n[\\s\\S]*?):= do[\\s\\S]*?(?=\\n/-- )',
            '\\g<1>:= sorry -- See https://github.com/AeneasVerif/aeneas/issues/1046'),

    # Fix ok_or none type inference.
    # https://github.com/AeneasVerif/aeneas/issues/1018
    (LITERAL, 'core.option.Option.ok_or none Error.StateDecode',
              'core.option.Option.ok_or (none : Option _) Error.StateDecode -- See https://github.com/AeneasVerif/aeneas/issues/1018'),
    (REGEX, '(\\| core\\.ops\\.control_flow\\.ControlFlow\\.Continue) val2 (=>\\n\\s+let \\S+ ← encoding\\.polynomial\\.PolyDecoder\\.from_pb val2)',
            '\\g<1> (val2 : proto.pq_ratchet.PolynomialDecoder) /- See https://github.com/AeneasVerif/aeneas/issues/1018 -/ \\g<2>'),
    (REGEX, '(\\| core\\.ops\\.control_flow\\.ControlFlow\\.Continue) val4 (=>\\n\\s+let \\S+ ← encoding\\.polynomial\\.PolyDecoder\\.from_pb val4)',
            '\\g<1> (val4 : proto.pq_ratchet.PolynomialDecoder) /- See https://github.com/AeneasVerif/aeneas/issues/1018 -/ \\g<2>'),
]


def patch(s):
    """Apply every patch in PATCHES, in order, returning the patched string."""
    for kind, pattern, replace in PATCHES:
        if kind == REGEX:
            s = re.sub(pattern, replace, s)
        else:
            s = s.replace(pattern, replace)
    return s


def run():
    encoding = 'utf-8'
    for f in FILES:
        p = ROOT / f
        p.write_text(patch(p.read_text(encoding=encoding)), encoding=encoding)


if __name__ == '__main__':
    run()
