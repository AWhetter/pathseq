from __future__ import annotations

import collections
from dataclasses import dataclass
from decimal import Decimal
import enum
import re

from statemachine import StateMachine, State

from ._error import NotASequenceError, ParseError
from ._file_num_seq import FileNumSequence
from ._ast import (
    PaddedRange,
    ParsedSequence,
    Ranges,
)

_PREFIX_SEPARATORS = {".", "_"}
RANGE_RE = re.compile(
    r"""
        -?\d+(?:\.\d+)?
        (?:                       # optional range
            -                     #   range delimiter
            -?\d+(?:\.\d+)?       #   end frame
            (?:                   #   optional stepping
                x                 #     step type
                \d+(?:\.\d+)?     #     step value
            )?
        )?
    """,
    re.VERBOSE,
)
PAD_FORMAT_RE = re.compile(
    r"""
        (?:
            \#+(?:\.\#+)?
            | <UDIM>
            | <UVTILE>
        )
    """,
    flags=re.VERBOSE,
)
RANGES_RE = re.compile(
    f"""
    (
        (?:{RANGE_RE.pattern} (?:, {RANGE_RE.pattern})*)?
        {PAD_FORMAT_RE.pattern}
    )
    """,
    flags=RANGE_RE.flags | PAD_FORMAT_RE.flags | re.VERBOSE,
)


class TokenType(enum.Enum):
    RANGE = enum.auto()
    INTER_RANGE = enum.auto()
    STEM = enum.auto()
    PREFIX = enum.auto()
    SUFFIXES = enum.auto()


@dataclass
class Token:
    type: TokenType
    value: str
    column: int

    @property
    def end_column(self) -> int:
        return self.column + len(self.value)


def _tokenise_seq(seq: str) -> list[Token]:
    raw_tokens = re.split(RANGES_RE, seq)
    if len(raw_tokens) == 1:
        raise NotASequenceError(seq)

    return process_tokens(seq, raw_tokens)


def process_tokens(seq: str, raw_tokens: list[str]) -> list[Token]:
    if seq.endswith("."):
        raise ParseError(seq, len(seq) - 1, reason="Suffixes cannot end with a '.'")

    starts_with_range = not bool(raw_tokens[0])
    if starts_with_range:
        raise ParseError(seq, 0, reason="Expected a stem but got a range")

    ends_with_range = not bool(raw_tokens[-1])
    if ends_with_range:
        raise ParseError(
            seq, len(seq), reason="Expected file suffixes but path ends with a range"
        )

    column = 0
    tokens: list[Token] = []
    for i, raw_token in enumerate(raw_tokens):
        if i == 0:
            separator = None
            if raw_token != "." and any(
                raw_token.endswith(sep) for sep in _PREFIX_SEPARATORS
            ):
                separator = Token(
                    TokenType.PREFIX,
                    raw_token[-1],
                    column + len(raw_token) - 1,
                )
                raw_token = raw_token[:-1]

            token = Token(
                TokenType.STEM,
                raw_token,
                column,
            )
            tokens.append(token)

            if separator:
                tokens.append(separator)
        elif i % 2 == 1:
            token = Token(
                TokenType.RANGE,
                raw_token,
                column,
            )
            tokens.append(token)
        elif i >= 2 and i != len(raw_tokens) - 1:
            if not raw_token:
                raise ParseError(
                    seq,
                    column + 1,
                    column + 2,
                    "Expected a non-empty inter-range separator",
                )
            if raw_token == ".":
                raise ParseError(
                    seq,
                    column + 1,
                    column + 2,
                    "Cannot use '.' as an inter-range separator",
                )
            token = Token(
                TokenType.INTER_RANGE,
                raw_token,
                column,
            )
            tokens.append(token)
        elif i == len(raw_tokens) - 1:
            if raw_token.startswith("."):
                token = Token(
                    TokenType.SUFFIXES,
                    raw_token,
                    column,
                )
                tokens.append(token)
            else:
                raise ParseError(
                    seq,
                    column + 1,
                    column + 2,
                    "Expected a '.' to begin file suffixes",
                )
        else:
            assert False, "Found a token that should be impossible"

        column += len(raw_token)

    assert all(isinstance(token, Token) for token in tokens)
    if not any(token.type == TokenType.RANGE for token in tokens):
        raise NotASequenceError(seq)

    if __debug__:
        type_counts = collections.Counter(token.type for token in tokens)
        assert type_counts[TokenType.STEM] <= 1
        num_pre_seps = type_counts[TokenType.PREFIX]
        assert num_pre_seps <= 1
        num_ranges = type_counts[TokenType.RANGE]
        num_inter_ranges = type_counts[TokenType.INTER_RANGE]
        assert num_inter_ranges == num_ranges - 1
        assert type_counts[TokenType.SUFFIXES] <= 1

    return tokens


class _SeqParser(StateMachine):
    init = State(initial=True)
    stem = State()

    in_prefix = State()
    range_in_name = State()
    in_inter_range = State()
    in_suffixes = State()

    parsed = State(final=True)

    pump = (
        init.to(stem, validators="expect_stem")
        | stem.to(in_prefix, cond="is_prefix")
        | stem.to(range_in_name, validators="expect_prefix_or_range")
        | in_prefix.to(range_in_name, validators="expect_range")
        | range_in_name.to(in_inter_range, cond="is_inter_range")
        | in_inter_range.to(range_in_name, validators="expect_range")
        | range_in_name.to(in_suffixes, validators="expect_inter_range_or_suffixes")
    )

    finalise = in_suffixes.to(parsed)

    def __init__(self, seq: str) -> None:
        super().__init__()

        self._seq = seq
        self._stem: str = ""
        self._prefix = ""
        self._ranges: list[PaddedRange[int] | PaddedRange[Decimal]] = []
        self._inter_ranges: list[str] = []
        self._suffixes: tuple[str, ...] = ()

    def is_inter_range(self, token: Token) -> bool:
        return token.type == TokenType.INTER_RANGE

    def is_prefix(self, token: Token) -> bool:
        return token.type == TokenType.PREFIX

    def expect_stem(self, token: Token) -> bool:
        return self._validate_stem(token, "Expected a stem")

    def expect_prefix_or_range(self, token: Token) -> bool:
        return self._validate_range(token, "Expected a prefix separator, or the ranges")

    def expect_range(self, token: Token) -> bool:
        return self._validate_range(token, "Expected the ranges")

    def expect_inter_range_or_suffixes(self, token: Token) -> bool:
        return self._validate_suffixes(
            token, "Expected an inter-range string, or file suffixes"
        )

    def _validate_range(self, token: Token, reason: str) -> bool:
        if token.type != TokenType.RANGE:
            raise ParseError(self._seq, token.column, token.end_column, reason=reason)
        return True

    def _validate_stem(self, token: Token, reason: str) -> bool:
        if token.type != TokenType.STEM:
            raise ParseError(self._seq, token.column, token.end_column, reason=reason)
        return True

    def _validate_suffixes(self, token: Token, reason: str) -> bool:
        if token.type != TokenType.SUFFIXES:
            raise ParseError(self._seq, token.column, token.end_column, reason=reason)
        return True

    def on_enter_stem(self, token: Token) -> None:
        self._stem = token.value

    def on_enter_in_prefix(self, token: Token) -> None:
        self._prefix = token.value

    def _parse_padded_range(
        self, token: Token
    ) -> PaddedRange[int] | PaddedRange[Decimal]:
        match = PAD_FORMAT_RE.search(token.value)
        if not match:
            raise ParseError(
                self._seq,
                token.column,
                token.end_column,
                reason=f"Tokenised an invalid range: {token.value}",
            )
        pad_format = match.group(0)
        seq_str = token.value[: -len(pad_format)]
        file_nums = FileNumSequence.from_str(seq_str)
        return PaddedRange(file_nums, pad_format)  # type: ignore[misc]

    def _parse_suffixes(self, token: Token) -> tuple[str, ...]:
        if not token.value:
            return ()

        suffixes = []
        buffer = token.value[0]
        for char in token.value[1:]:
            if char == ".":
                if buffer == ".":
                    column = token.column + len(buffer)
                    raise ParseError(
                        self._seq,
                        column,
                        column + 1,
                        "Cannot have an empty file extension",
                    )
                suffixes.append(buffer)
                buffer = char
            else:
                buffer += char

        suffixes.append(buffer)
        return tuple(suffixes)

    def on_enter_range_in_name(self, token: Token) -> None:
        self._ranges.append(self._parse_padded_range(token))

    def on_enter_in_inter_range(self, token: Token) -> None:
        self._inter_ranges.append(token.value or "")

    def on_enter_in_suffixes(self, token: Token) -> None:
        self._suffixes = self._parse_suffixes(token)

    def on_finalise(self) -> ParsedSequence:
        return ParsedSequence(
            stem=self._stem,
            prefix=self._prefix,
            ranges=Ranges(tuple(self._ranges), tuple(self._inter_ranges)),
            suffixes=self._suffixes,
        )

    @classmethod
    def parse(cls, seq: str) -> ParsedSequence:
        machine = cls(seq)
        tokens = _tokenise_seq(seq)
        for token in tokens:
            machine.pump(token)

        return machine.finalise()  # type: ignore[no-any-return]


def parse_path_sequence(seq: str) -> ParsedSequence:
    return _SeqParser.parse(seq)
