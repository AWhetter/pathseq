from __future__ import annotations

import collections
from dataclasses import dataclass
import enum
import pathlib
import re
from typing import Literal, NamedTuple

from statemachine import StateMachine, State

from ._error import NotASequenceError, ParseError
from ._file_num_set import RANGE_RE
from .._file_num_set import FileNumSet

_SEPARATORS = {".", "_"}
RANGES_RE = re.compile(
    f"""
    (
        (?P<ranges>{RANGE_RE.pattern} (, {RANGE_RE.pattern})*)?
        (?P<pad_format>(
            #+(\.#+)?
            | <UDIM>
            | <UVTILE>
        ))
    )
    """,
    flags=RANGE_RE.flags | re.VERBOSE,
)


class TokenType(enum.Enum):
    RANGE = enum.auto()
    INTER_RANGE = enum.auto()
    STEM = enum.auto()
    SEPARATOR = enum.auto()
    SUFFIXES = enum.auto()


@dataclass
class Token:
    type: TokenType
    value: str
    column: int

    @property
    def end_column(self) -> int:
        return self.column + len(self.value)


def _tokenise(seq: str) -> list[str | Token]:
    raw_tokens = re.split(RANGES_RE, seq)

    seq_type: type[RangeStartsName | RangeInName | RangeEndsName]
    if not raw_tokens[-1]:
        raw_tokens.pop()
        seq_type = RangeEndsName
        if not raw_tokens[0]:
            raise ParseError(
                seq, len(seq), reason="Expected a stem and file suffixes"
            )
    elif not raw_tokens[0]:
        seq_type = RangeStartsName
    else:
        seq_type = RangeInName

    column = 0
    tokens = []
    for i, raw_token in enumerate(raw_tokens):
        if i == 0:
            if not raw_token:
                pass
            elif raw_token == ".":
                token = Token(
                    TokenType.STEM,
                    raw_token,
                    column,
                )
                tokens.append(token)
                if seq_type is not RangeInName:
                    raise ParseError(
                        seq, len(seq), reason="Expected file suffixes"
                    )
            elif seq_type is RangeEndsName:
                separator = None
                if any(raw_token.endswith(sep) for sep in _SEPARATORS):
                    separator = Token(
                        TokenType.SEPARATOR,
                        raw_token[-1],
                        column + len(raw_token) - 1,
                    )
                    path = pathlib.Path(raw_token[:-1])
                else:
                    path = pathlib.Path(raw_token)

                token = Token(
                    TokenType.STEM,
                    path.stem,
                    column,
                )
                tokens.append(token)
                token = Token(
                    TokenType.SUFFIXES,
                    "".join(path.suffixes),
                    token.end_column,
                )
                tokens.append(token)

                if separator:
                    tokens.append(separator)
            else:
                assert seq_type is RangeInName
                if any(raw_token.endswith(sep) for sep in _SEPARATORS):
                    token = Token(
                        TokenType.STEM,
                        raw_token[:-1],
                        column,
                    )
                    tokens.append(token)
                    token = Token(
                        TokenType.SEPARATOR,
                        raw_token[-1],
                        token.end_column,
                    )
                    tokens.append(token)
                else:
                    token = Token(
                        TokenType.STEM,
                        raw_token,
                        column,
                    )
                    tokens.append(token)
        elif i % 2 == 1:
            token = Token(
                TokenType.RANGE,
                raw_token,
                column,
            )
            tokens.append(token)
        elif i >= 2 and i != len(raw_tokens) - 1:
            token = Token(
                TokenType.INTER_RANGE,
                raw_token,
                column,
            )
            tokens.append(token)
        elif i == len(raw_tokens):
            assert seq_type is RangeInName
            if any(raw_token.startswith(sep) for sep in _SEPARATORS if sep != "."):
                token = Token(
                    TokenType.SEPARATOR,
                    raw_token[0],
                    column,
                )
                tokens.append(token)
                raw_token = raw_token[1:]
                column += 1

            token = Token(
                TokenType.SUFFIXES,
                raw_token,
                column,
            )
            tokens.append(token)

        column += len(raw_token)

    assert all(isinstance(token, Token) for token in tokens)
    if not any(token.type == TokenType.RANGES):
        raise NotASequenceError(seq)

    num_stems = sum(1 for token in tokens if token.type == TokenType.STEM)
    assert num_stems == 1
    num_suffixes = sum(1 for token in tokens if token.type == TokenType.SUFFIXES)
    assert num_suffixes == 1
    num_separators = sum(1 for token in tokens if token.type == TokenType.SEPARATOR)
    assert (num_separators <= 2) if seq_type is RangeInName else (num_separators <= 1)
    assert sum(1 for token in tokens if token.type == TokenType.PAD_FORMAT) % 2 == 1
    assert sum(1 for token in tokens if token.type == TokenType.INTER_RANGE) % 2 == 1
    assert all(token.value for token in tokens)

    return tokens


class SeqParser(StateMachine):
    init = State(initial=True)
    range_starts_name = State()
    starts_inter_range = State()
    starts_prefix_separator = State()
    starts_stem = State()
    starts_suffixes = State()

    range_later = State()  # stem

    in_prefix_separator = State()
    range_in_name = State()
    in_inter_range = State()
    in_postfix_separator = State()
    in_suffixes = State()

    range_ends_name = State()  # suffixes
    ends_prefix_separator = State()
    ends_range = State()
    ends_inter_range = State()

    parsed = State(final=True)

    pump = (
        init.to(range_starts_name, cond="is_range")
        | init.to(range_later, validators="expect_range_or_stem")
        | range_starts_name.to(starts_inter_range, cond="is_inter_range")
        | starts_inter_range.to(range_starts_name, cond="expect_range")
        | range_starts_name.to.itself(on="on_blank_inter_range")
        | range_starts_name.to(starts_prefix_separator, cond="is_separator")
        | range_starts_name.to(starts_stem, validators="expect_inter_or_sep_or_stem")
        | starts_prefix_separator.to(starts_stem, validators="expect_stem")
        | starts_stem.to(starts_suffixes, validators="expect_suffixes")
        | range_later.to(in_prefix_separator, cond="is_separator")
        | range_later.to(range_in_name, cond="is_range")
        | in_prefix_separator.to(range_in_name, validators="expect_range")
        | range_in_name.to(in_inter_range, cond="is_inter_range")
        | in_inter_range.to(range_in_name, validators="expect_range")
        | range_in_name.to(in_postfix_separator, cond="is_separator")
        | in_postfix_separator.to(in_suffixes, validators="expect_suffixes")
        | range_in_name.to(in_suffixes, validators="expect_inter_or_sep_or_suffixes")
        | range_later.to(range_ends_name, validators="expect_sep_or_range_or_suffixes")
        | range_ends_name.to(ends_prefix_separator, cond="is_separator")
        | range_ends_name.to(ends_range, validators="expect_separator_or_range")
        | ends_range.to(ends_inter_range, validators="expect_inter_range")
    )

    finalise = (
        starts_suffixes.to(parsed)
        | in_suffixes.to(parsed)
        | ends_range.to(parsed)
    )

    def __init__(self):
        super().__init__()

        self._tokens = collections.deque()

        self._seq = ""
        self._range_type: type[RangeStartsName] | type[RangeInName] | type[RangeEndsName] | None = None
        self._stem = None
        self._prefix_separator = ""
        self._ranges: PathRanges = []
        self._postfix_separator = ""
        self._suffixes = []

    def is_range(self, token: Token) -> bool:
        return token.type == TokenType.RANGE

    def is_inter_range(self, token: Token) -> bool:
        return token.type == TokenType.INTER_RANGE

    def is_stem(self, token: Token) -> bool:
        return token.type == TokenType.STEM

    def is_separator(self, token: Token) -> bool:
        return token.type == TokenType.SEPARATOR

    def is_suffixes(self, token: Token) -> bool:
        return token.type == TokenType.SUFFIXES

    def expect_range_or_stem(self, token: Token) -> bool:
        return self._validate_stem(token, "Expected a range or a stem")

    def expect_inter_or_sep_or_stem(self, token: Token) -> bool:
        return self._validate_stem(token, "Expected an inter-range string, a range separator, or a stem")

    def expect_inter_or_sep_or_suffixes(self, token: Token) -> bool:
        return self._validate_stem(token, "Expected an inter-range string, a range separator, or file suffixes")

    def expect_stem(self, token: Token) -> bool:
        return self._validate_stem(token, "Expected a stem")

    def expect_suffixes(self, token: Token) -> bool:
        return self._validate_suffixes(token, "Expected the file suffixes")

    def expect_range(self, token: Token) -> bool:
        return self._validate_range(token, "Expected the ranges")

    def expect_separator_or_range(self, token: Token) -> bool:
        return self._validate_range(token, "Expected a range separator or the ranges")

    def expect_inter_range(self, token: Token) -> bool:
        return self._validate_inter_range(token, "Expected an inter-range string")

    def _validate_range(self, token: Token, reason: str) -> bool:
        if token.type != TokenType.RANGE:
            raise ParseError(self._seq, token.column, token.end_column, reason=reason)
        return True

    def _validate_inter_range(self, token: Token, reason: str) -> bool:
        if token.type != TokenType.INTER_RANGE:
            raise ParseError(self._seq, token.column, token.end_column, reason=reason)
        return True

    def _validate_stem(self, token: Token, reason: str) -> bool:
        if token.type != TokenType.STEM:
            raise ParseError(self._seq, token.column, token.end_column, reason=reason)
        return True

    def validate_separator(self, token: Token) -> bool:
        if token.type != TokenType.SEPARATOR:
            raise ParseError(self._seq, token.column, token.end_column, reason="Expected a range separator")
        return True

    def _validate_suffixes(self, token: Token, reason: str) -> bool:
        if token.type != TokenType.SUFFIXES:
            raise ParseError(self._seq, token.column, token.end_column, reason=reason)
        return True

    def on_enter_range_starts_name(self, token):
        self._range_type = RangeStartsName

        file_num_set = FileNumSet.from_str(token.value)
        self._ranges.append(file_num_set)

    def on_enter_starts_inter_range(self, token):
        self._ranges.append(token.value)

    def on_blank_inter_range(self):
        self._ranges.append("")

    def on_enter_starts_prefix_separator(self, token):
        self._prefix_separator = token.value

    def on_enter_starts_stem(self, token):
        self._stem = token.value

    def on_enter_in_prefix_separator(self, token):
        self._prefix_separator = token.value

    def on_enter_range_in_name(self, token):
        self._range_type = RangeInName

        match = RANGES_RE.fullmatch(token.value)
        file_num_set = ""
        if match.group("ranges"):
            file_num_set = FileNumSet.from_str(token.value)
        pad_format = match.group("pad_format")
        range_ = PaddedRange(file_num_set, pad_format)
        self._ranges.append(range_)

    def on_enter_in_postfix_separator(self, token):
        self._postfix_separator = token.value

    def on_enter_in_suffixes(self, token):
        self._suffixes = token.value

    def on_enter_range_ends_name(self, token):
        self._range_type = RangeEndsName

        self._suffixes = token.value

    def on_enter_ends_prefix_separator(self, token):
        self._prefix_separator = token.value

    def on_enter_finalise(self) -> RangeStartsName | RangeInName | RangeEndsName:
        kwargs = {
            "stem": self._stem,
            "prefix_separator": self._prefix_separator,
            "ranges": self._ranges,
            "postfix_separator": self._postfix_separator,
            "suffixes": self._suffixes,
        }
        return self._range_type(**kwargs)

    def parse(self, seq: str) -> RangeStartsName | RangeInName | RangeEndsName:
        self._seq = seq
        self._tokens = collections.deque(_tokenise(seq))
        while True:
            try:
                token = self._tokens.popleft()
            except IndexError:
                break
            else:
                self.pump(token)

        return self.finalise()


class RangeStartsName(NamedTuple):
    prefix_separator: Literal[""]
    ranges: PathRanges
    postfix_separator: str
    stem: str
    suffixes: list[str]


class RangeInName(NamedTuple):
    stem: str
    prefix_separator: str
    ranges: PathRanges
    postfix_separator: str
    suffixes: list[str]


class RangeEndsName(NamedTuple):
    stem: str
    suffixes: list[str]
    prefix_separator: str
    ranges: PathRanges
    postfix_separator: Literal[""]


@dataclass
class PaddedRange:
    file_num_set: FileNumSet | Literal[""]
    pad_format: str


class PathRanges(list[PaddedRange | str]):
    pass


def parse_path_sequence(seq: str) -> RangeStartsName | RangeInName | RangeEndsName:
    return SeqParser().parse(seq)