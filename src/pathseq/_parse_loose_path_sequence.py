from __future__ import annotations

import collections
from dataclasses import dataclass
from decimal import Decimal
import enum
import re
from typing import TypeAlias, Union

from statemachine import StateMachine, State

from ._error import NotASequenceError, ParseError
from ._file_num_seq import FileNumSequence
from ._ast import (
    PaddedRange,
    RangesEndName,
    RangesInName,
    RangesStartName,
)

_POSTFIX_SEPARATORS = {"_"}
_PREFIX_SEPARATORS = _POSTFIX_SEPARATORS | {"."}
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

ParsedLooseSequence: TypeAlias = Union[RangesStartName, RangesInName, RangesEndName]


class TokenType(enum.Enum):
    RANGE = enum.auto()
    INTER_RANGE = enum.auto()
    STEM = enum.auto()
    PREFIX = enum.auto()
    POSTFIX = enum.auto()
    SUFFIXES = enum.auto()


@dataclass
class Token:
    type: TokenType
    value: str
    column: int

    @property
    def end_column(self) -> int:
        return self.column + len(self.value)


def _tokenise(seq: str) -> list[Token]:
    raw_tokens = re.split(RANGES_RE, seq)

    starts_with_range = not bool(raw_tokens[0])
    ends_with_range = not bool(raw_tokens[-1])
    if ends_with_range:
        raw_tokens.pop()

    column = 0
    tokens = []
    for i, raw_token in enumerate(raw_tokens):
        if i == 0:
            if not raw_token:
                pass
            elif not ends_with_range:
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
            else:
                separator = None
                if any(raw_token.endswith(sep) for sep in _PREFIX_SEPARATORS):
                    separator = Token(
                        TokenType.PREFIX,
                        raw_token[-1],
                        column + len(raw_token) - 1,
                    )
                    raw_token = raw_token[:-1]

                try:
                    suffix_dot = 0
                    if raw_token.startswith("."):
                        suffix_dot = 1
                    suffix_i = raw_token.index(".", suffix_dot)
                except ValueError:
                    suffix_i = len(raw_token)

                token = Token(
                    TokenType.STEM,
                    raw_token[:suffix_i],
                    column,
                )
                tokens.append(token)

                if raw_token[suffix_i:]:
                    token = Token(
                        TokenType.SUFFIXES,
                        raw_token[suffix_i:],
                        column + suffix_i,
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
            token = Token(
                TokenType.INTER_RANGE,
                raw_token,
                column,
            )
            tokens.append(token)
        elif i == len(raw_tokens) - 1:
            if raw_token.startswith(".") and not raw_token.endswith("."):
                token = Token(
                    TokenType.SUFFIXES,
                    raw_token,
                    column,
                )
                tokens.append(token)
            elif starts_with_range:
                if any(raw_token.startswith(sep) for sep in _POSTFIX_SEPARATORS):
                    token = Token(
                        TokenType.POSTFIX,
                        raw_token[0],
                        column,
                    )
                    tokens.append(token)
                    raw_token = raw_token[1:]
                    column += 1

                if raw_token.endswith("."):
                    suffix_i = len(raw_token)
                elif raw_token.startswith("."):
                    suffix_i = 0
                else:
                    try:
                        suffix_i = raw_token.index(".")
                    except ValueError:
                        suffix_i = len(raw_token)

                if raw_token[:suffix_i]:
                    token = Token(
                        TokenType.STEM,
                        raw_token[:suffix_i],
                        column,
                    )
                    tokens.append(token)

                if raw_token[suffix_i:]:
                    token = Token(
                        TokenType.SUFFIXES,
                        raw_token[suffix_i:],
                        column + suffix_i,
                    )
                    tokens.append(token)
            else:
                if raw_token.endswith("."):
                    suffix_i = len(raw_token)
                elif raw_token.startswith("."):
                    suffix_i = 0
                else:
                    try:
                        suffix_i = raw_token.index(".")
                    except ValueError:
                        suffix_i = len(raw_token)

                if raw_token[:suffix_i]:
                    token = Token(
                        TokenType.POSTFIX,
                        raw_token[:suffix_i],
                        column,
                    )
                    tokens.append(token)

                if raw_token[suffix_i:]:
                    token = Token(
                        TokenType.SUFFIXES,
                        raw_token[suffix_i:],
                        column + suffix_i,
                    )
                    tokens.append(token)

        column += len(raw_token)

    assert all(isinstance(token, Token) for token in tokens)
    if not any(token.type == TokenType.RANGE for token in tokens):
        raise NotASequenceError(seq)

    if __debug__:
        type_counts = collections.Counter(token.type for token in tokens)
        assert type_counts[TokenType.STEM] <= 1
        num_pre_seps = type_counts[TokenType.PREFIX]
        assert num_pre_seps <= 1
        num_postfixes = type_counts[TokenType.POSTFIX]
        assert num_postfixes <= 1
        num_ranges = type_counts[TokenType.RANGE]
        num_inter_ranges = type_counts[TokenType.INTER_RANGE]
        assert num_inter_ranges == num_ranges - 1
        assert type_counts[TokenType.SUFFIXES] <= 1

    return tokens


class SeqParser(StateMachine):
    init = State(initial=True)
    range_starts_name = State()
    starts_inter_range = State()
    starts_postfix = State()
    starts_stem = State()
    starts_suffixes = State()

    range_later = State()  # stem

    in_prefix = State()
    range_in_name = State()
    in_inter_range = State()
    in_postfix = State()
    in_suffixes = State()

    range_ends_name = State()  # suffixes
    ends_prefix = State()
    ends_range = State()
    ends_inter_range = State()

    parsed = State(final=True)

    pump = (
        init.to(range_starts_name, cond="is_range")
        | init.to(range_later, validators="expect_range_or_stem")
        | range_starts_name.to(starts_inter_range, cond="is_inter_range")
        | starts_inter_range.to(range_starts_name, cond="expect_range")
        | range_starts_name.to.itself(on="on_blank_inter_range", cond="is_range")  # type: ignore[no-untyped-call]
        | range_starts_name.to(in_suffixes, cond="is_suffixes", on="switch_to_in_range")
        | range_starts_name.to(starts_postfix, cond="is_postfix")
        | range_starts_name.to(
            starts_stem, validators="expect_inter_or_pre_sep_or_stem"
        )
        | starts_postfix.to(starts_stem, validators="expect_stem")
        | starts_stem.to(starts_suffixes, validators="expect_suffixes")
        | range_later.to(in_prefix, cond="is_prefix")
        | range_later.to(range_in_name, cond="is_range")
        | in_prefix.to(range_in_name, validators="expect_range")
        | range_in_name.to(in_inter_range, cond="is_inter_range")
        | in_inter_range.to(range_in_name, validators="expect_range")
        | range_in_name.to(in_postfix, cond="is_postfix")
        | in_postfix.to(in_suffixes, validators="expect_suffixes")
        | range_in_name.to(
            in_suffixes, validators="expect_inter_or_post_sep_or_suffixes"
        )
        | range_later.to(
            range_ends_name, validators="expect_pre_sep_or_range_or_suffixes"
        )
        | range_ends_name.to(ends_prefix, cond="is_prefix")
        | range_ends_name.to(ends_range, validators="expect_pre_sep_or_range")
        | ends_prefix.to(ends_range, validators="expect_range")
        | ends_range.to(ends_inter_range, validators="expect_inter_range")
        | ends_inter_range.to(ends_range, validators="expect_range")
    )

    finalise = (
        range_starts_name.to(parsed)
        | starts_stem.to(parsed)
        | starts_suffixes.to(parsed)
        | range_in_name.to(parsed)
        | in_postfix.to(parsed)
        | in_suffixes.to(parsed)
        | ends_range.to(parsed)
    )

    def __init__(self, seq: str) -> None:
        super().__init__()

        self._seq = seq
        self._range_type: type[ParsedLooseSequence] | None = None
        self._stem = ""
        self._prefix = ""
        self._ranges: list[PaddedRange[int] | PaddedRange[Decimal]] = []
        self._inter_ranges: list[str] = []
        self._postfix = ""
        self._suffixes: tuple[str, ...] = ()

    def is_range(self, token: Token) -> bool:
        return token.type == TokenType.RANGE

    def is_inter_range(self, token: Token) -> bool:
        return token.type == TokenType.INTER_RANGE

    def is_stem(self, token: Token) -> bool:
        return token.type == TokenType.STEM

    def is_prefix(self, token: Token) -> bool:
        return token.type == TokenType.PREFIX

    def is_postfix(self, token: Token) -> bool:
        return token.type == TokenType.POSTFIX

    def is_suffixes(self, token: Token) -> bool:
        return token.type == TokenType.SUFFIXES

    def expect_range_or_stem(self, token: Token) -> bool:
        return self._validate_stem(token, "Expected a range or a stem")

    def expect_inter_or_pre_sep_or_stem(self, token: Token) -> bool:
        return self._validate_stem(
            token, "Expected an inter-range string, a prefix separator, or a stem"
        )

    def expect_inter_or_post_sep_or_suffixes(self, token: Token) -> bool:
        return self._validate_suffixes(
            token, "Expected an inter-range string, a postfix, or file suffixes"
        )

    def expect_stem(self, token: Token) -> bool:
        return self._validate_stem(token, "Expected a stem")

    def expect_suffixes(self, token: Token) -> bool:
        return self._validate_suffixes(token, "Expected the file suffixes")

    def expect_range(self, token: Token) -> bool:
        return self._validate_range(token, "Expected the ranges")

    def expect_pre_sep_or_range(self, token: Token) -> bool:
        return self._validate_range(token, "Expected a prefix separator, or a range")

    def expect_inter_range(self, token: Token) -> bool:
        return self._validate_inter_range(token, "Expected an inter-range string")

    def expect_pre_sep_or_range_or_suffixes(self, token: Token) -> bool:
        return self._validate_suffixes(
            token, "Expected a prefix separator, a ranges, or file suffixes"
        )

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

    def _validate_suffixes(self, token: Token, reason: str) -> bool:
        if token.type != TokenType.SUFFIXES:
            raise ParseError(self._seq, token.column, token.end_column, reason=reason)
        return True

    def switch_to_in_range(self) -> None:
        self._range_type = RangesInName

    def on_enter_range_starts_name(self, token: Token) -> None:
        self._range_type = RangesStartName

        self._ranges.append(self._parse_padded_range(token))

    def on_enter_starts_inter_range(self, token: Token) -> None:
        self._inter_ranges.append(token.value)

    def on_enter_in_inter_range(self, token: Token) -> None:
        self._inter_ranges.append(token.value)

    def on_enter_ends_inter_range(self, token: Token) -> None:
        self._inter_ranges.append(token.value)

    def on_blank_inter_range(self) -> None:
        self._inter_ranges.append("")

    def on_enter_starts_postfix(self, token: Token) -> None:
        self._postfix = token.value

    def on_enter_starts_stem(self, token: Token) -> None:
        self._stem = token.value

    def on_enter_starts_suffixes(self, token: Token) -> None:
        self._suffixes = self._parse_suffixes(token)

    def on_enter_range_later(self, token: Token) -> None:
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
                suffixes.append(buffer)
                buffer = char
            else:
                buffer += char

        suffixes.append(buffer)
        return tuple(suffixes)

    def on_enter_range_in_name(self, token: Token) -> None:
        self._range_type = RangesInName

        self._ranges.append(self._parse_padded_range(token))

    def on_enter_in_postfix(self, token: Token) -> None:
        self._postfix = token.value

    def on_enter_in_suffixes(self, token: Token) -> None:
        self._suffixes = self._parse_suffixes(token)

    def on_enter_range_ends_name(self, token: Token) -> None:
        self._range_type = RangesEndName

        self._suffixes = self._parse_suffixes(token)

    def on_enter_ends_range(self, token: Token) -> None:
        self._ranges.append(self._parse_padded_range(token))

    def on_enter_ends_prefix(self, token: Token) -> None:
        self._prefix = token.value

    def on_finalise(self, source: State) -> ParsedLooseSequence:
        if source == self.range_starts_name:
            self._range_type = RangesInName

        assert self._range_type is not None, "Failed to establish a range type"
        assert self._range_type is not RangesStartName or self._prefix == ""
        assert self._range_type is not RangesEndName or self._postfix == ""

        return self._range_type(
            stem=self._stem,
            prefix=self._prefix,  # type: ignore[arg-type]
            ranges=tuple(self._ranges),
            inter_ranges=tuple(self._inter_ranges),
            postfix=self._postfix,  # type: ignore[arg-type]
            suffixes=self._suffixes,
        )

    @classmethod
    def parse(cls, seq: str) -> ParsedLooseSequence:
        machine = cls(seq)
        tokens = collections.deque(_tokenise(seq))
        while True:
            try:
                token = tokens.popleft()
            except IndexError:
                break
            else:
                machine.pump(token)

        return machine.finalise()  # type: ignore[no-any-return]


def parse_path_sequence(seq: str) -> ParsedLooseSequence:
    return SeqParser.parse(seq)
