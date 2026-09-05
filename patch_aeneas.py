#!/usr/bin/env python3

import re
from pathlib import Path

ROOT = Path('foo/SrcTranslated')
FILES = ['Types.lean', 'Funs.lean']

def mk_find(pattern, replacement):
    return lambda s: s.replace(pattern, replacement)

def mk_regex(pattern, replacement):
    return lambda s: re.sub(pattern, replacement, s)

PATCHES = [
    # Disable linters for the auto-generated files.
    mk_find(
        """\
open Aeneas Aeneas.Std Result ControlFlow Error
set_option linter.dupNamespace false
set_option linter.hashCommand false
set_option linter.unusedVariables false
""",
        """\
set_option linter.style.headerAlt false
set_option linter.style.header false
set_option linter.style.longLine false
set_option linter.style.setOption false
set_option linter.style.whitespace false
set_option linter.dupNamespace false
set_option linter.hashCommand false
set_option linter.unusedVariables false

open Aeneas Aeneas.Std Result ControlFlow Error
"""
    ),

    # https://github.com/AeneasVerif/aeneas/issues/1043
    mk_regex(
        r'\n  map := fun[\s\S]*?(?=\n  enumerate)',
        '\n  -- See https://github.com/AeneasVerif/aeneas/issues/1043'
    ),
    mk_regex(
        r'\n  collect := fun[\s\S]*?(?=\n\})',
        '\n  -- See https://github.com/AeneasVerif/aeneas/issues/1043'
    ),

    # https://github.com/AeneasVerif/aeneas/issues/1043
    mk_regex(
        r'next := core\.iter\.adapters\.map\.Map\.Insts\.CoreIterTraitsIteratorIterator\.next[\s\S]*?(?=\n  step_by)',
        'next := sorry -- See https://github.com/AeneasVerif/aeneas/issues/1043'
    ),

    # https://github.com/Beneficial-AI-Foundation/SparsePostQuantumRatchet-verify/issues/102
    mk_regex(
        r'impl_def(\s+[\w.]+\.Insts\.ProstMessageMessage\s*:[\s\S]*?):= \{[\s\S]*?\n\}',
        r'def\g<1>:= sorry -- See https://github.com/Beneficial-AI-Foundation/SparsePostQuantumRatchet-verify/issues/102'
    ),

    # Fix local variable `chain` shadowing module namespace `chain.Chain` in `send`.
    # https://github.com/Beneficial-AI-Foundation/SparsePostQuantumRatchet-verify/issues/101
    mk_find(
        """let chain ←
                    match val2.key with""",
        """let chain' /- See https://github.com/Beneficial-AI-Foundation/SparsePostQuantumRatchet-verify/issues/101 -/ ←
                    match val2.key with"""
    ),
    mk_find(
        """let chain ←
                match val2.key with""",
        """let chain' /- See https://github.com/Beneficial-AI-Foundation/SparsePostQuantumRatchet-verify/issues/101 -/ ←
                match val2.key with"""
    ),
    mk_find(
        'chain.Chain.send_key chain i3',
        "chain.Chain.send_key chain' i3 /- #101 rename -/"
    ),
    mk_find(
        'chain.Chain.send_key chain i1',
        "chain.Chain.send_key chain' i1 /- #101 rename -/"
    ),

    # Fix local variable `chain` shadowing module namespace `chain.Chain` in `recv`.
    # https://github.com/Beneficial-AI-Foundation/SparsePostQuantumRatchet-verify/issues/101
    mk_find(
        """let chain ←
                            match val5.key with""",
        """let chain' /- See https://github.com/Beneficial-AI-Foundation/SparsePostQuantumRatchet-verify/issues/101 -/ ←
                            match val5.key with"""
    ),
    mk_find(
        """let chain ←
                    match val3.key with""",
        """let chain' /- See https://github.com/Beneficial-AI-Foundation/SparsePostQuantumRatchet-verify/issues/101 -/ ←
                    match val3.key with"""
    ),
    mk_find(
        'chain.Chain.into_pb chain\n',
        "chain.Chain.into_pb chain' /- #101 rename -/\n"
    ),
    mk_find(
        'chain.Chain.recv_key chain msg_key_epoch index',
        "chain.Chain.recv_key chain' msg_key_epoch index /- #101 rename -/"
    ),

    # Fix local variable `v1` shadowing module namespace `v1.chunked.states` in `recv`.
    # https://github.com/Beneficial-AI-Foundation/SparsePostQuantumRatchet-verify/issues/101
    mk_find(
        """let v1 := read_discriminant v
      let i ← lift (IScalar.hcast .U8 v1)""",
        """let v1' := read_discriminant v /- See https://github.com/Beneficial-AI-Foundation/SparsePostQuantumRatchet-verify/issues/101 -/
      let i ← lift (IScalar.hcast .U8 v1')"""
    ),

    # Sorry merge closure FnOnce call_once assignments (Aeneas types them wrong).
    # https://github.com/AeneasVerif/aeneas/issues/1046
    mk_regex(
        r'call_once :=\n    proto\.pq_ratchet\.\S+\.merge\.closure\S*\.Insts\.CoreOpsFunctionFnOnceTupleTupleTuple\.call_once\n    bytesbufbuf_implBufInst\n}',
        'call_once := sorry -- See https://github.com/AeneasVerif/aeneas/issues/1046\n}'
    ),

    # Sorry merge function bodies (broken Result.map with mistyped closures).
    # https://github.com/AeneasVerif/aeneas/issues/1046
    mk_regex(
        r'(def proto\.pq_ratchet\.(?:pq_ratchet_state\.Inner|v1_msg\.InnerMsg|v1_state\.InnerState)\.merge\n[\s\S]*?):= do[\s\S]*?(?=\n/-- )',
        r'\g<1>:= sorry -- See https://github.com/AeneasVerif/aeneas/issues/1046'
    ),

    # Fix ok_or none type inference.
    # https://github.com/AeneasVerif/aeneas/issues/1018
    mk_find(
        'core.option.Option.ok_or none Error.StateDecode',
        'core.option.Option.ok_or (none : Option _) Error.StateDecode -- See https://github.com/AeneasVerif/aeneas/issues/1018'
    ),
    mk_regex(
        r'(\| core\.ops\.control_flow\.ControlFlow\.Continue) val2 (=>\n\s+let \S+ ← encoding\.polynomial\.PolyDecoder\.from_pb val2)',
        r'\g<1> (val2 : proto.pq_ratchet.PolynomialDecoder) /- See https://github.com/AeneasVerif/aeneas/issues/1018 -/ \g<2>'
    ),
    mk_regex(
        r'(\| core\.ops\.control_flow\.ControlFlow\.Continue) val4 (=>\n\s+let \S+ ← encoding\.polynomial\.PolyDecoder\.from_pb val4)',
        r'\g<1> (val4 : proto.pq_ratchet.PolynomialDecoder) /- See https://github.com/AeneasVerif/aeneas/issues/1018 -/ \g<2>'
    ),
]

def patch(s):
    for f in PATCHES:
        s = f(s)
    return s


def run():
    encoding = 'utf-8'
    for f in FILES:
        p = ROOT / f
        s = p.read_text(encoding=encoding)
        s = patch(s)
        p.write_text(s, encoding=encoding)


if __name__ == '__main__':
    run()
