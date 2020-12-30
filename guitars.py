from __future__ import annotations

from dataclasses import dataclass
from typing import Any, FrozenSet, Generator, List, Optional, Set

NUMBER_OF_FINGERS_TO_CONSIDER = 4
MAXIMUM_SPAN_OF_FRETS = 3


@dataclass(frozen=True)
class Note:
    NOTE_TO_NAME = {
        0: "C",
        1: "C#",
        2: "D",
        3: "E♭",
        4: "E",
        5: "F",
        6: "F#",
        7: "G",
        8: "G#",
        9: "A",
        10: "B♭",
        11: "B",
    }

    number: int

    @classmethod
    def from_number_not_modded_out(cls, number_not_modded_out: int) -> Note:
        return Note(number_not_modded_out % 12)

    @property
    def name(self) -> str:
        return self.NOTE_TO_NAME[self.number]

    def transpose_upwards_by(self, semitones: int) -> Note:
        return Note.from_number_not_modded_out(self.number + semitones)

    def __repr__(self) -> str:
        return self.name


@dataclass(frozen=True)
class String:
    STRING_TO_NOTE = {
        1: Note(4),
        2: Note(11),
        3: Note(7),
        4: Note(2),
        5: Note(9),
        6: Note(4),
    }
    number: int

    @property
    def _open_string_note(self) -> Note:
        return self.STRING_TO_NOTE[self.number]

    def note(self, fret: Optional[Fret] = None) -> Note:
        if fret is None:
            return self._open_string_note

        return self._open_string_note.transpose_upwards_by(fret.number + 1)

    def __repr__(self) -> str:
        return f"string {self.number}"


@dataclass(frozen=True)
class Fret:
    number: int

    def __repr__(self) -> str:
        return f"fret {self.number + 1}"


@dataclass(frozen=True)
class Placement:
    string: String
    fret: Fret

    def __repr__(self) -> str:
        return f"{self.string} - {self.fret}"


@dataclass(frozen=True)
class HandPosition:
    placements: FrozenSet[Placement]

    def is_valid(self) -> bool:
        if self._involves_too_many_fingers():
            return False

        if self._a_string_is_touched_twice():
            return False

        if self._the_span_is_too_wide():
            return False

        return True

    def _involves_too_many_fingers(self) -> bool:
        return len(self.placements) > NUMBER_OF_FINGERS_TO_CONSIDER

    def _a_string_is_touched_twice(self) -> bool:
        touched_strings = [placement.string for placement in self.placements]
        return len(set(touched_strings)) < len(touched_strings)

    def _the_span_is_too_wide(self) -> bool:
        if not self.placements:
            return False
        fret_numbers = [placement.fret.number for placement in self.placements]
        return max(fret_numbers) - min(fret_numbers) > MAXIMUM_SPAN_OF_FRETS - 1

    def __iter__(self) -> Generator[Placement, None, None]:
        for p in self.placements:
            yield p

    def __contains__(self, placement: Placement) -> bool:
        return placement in self.placements

    def __repr__(self) -> str:
        return str(set(self.placements))

    def get_notes(self) -> List[Note]:
        self._ensure_is_valid()
        return Guitar.get_notes(self)

    def _ensure_is_valid(self) -> None:
        if not self.is_valid():
            raise Exception("This isn't a valid hand-position.")

    def get_number_of_distinct_notes(self) -> int:
        note_names = [note.name for note in self.get_notes()]
        return len(set(note_names))

    def touches(self, string: String) -> bool:
        for placement in self.placements:
            if placement.string == string:
                return True
        return False

    def get_fret_on(self, string: String) -> Fret:
        for placement in self.placements:
            if placement.string == string:
                return placement.fret
        raise Exception(f"{string} isn't touched by this hand-position.")

    def get_open_strings(self) -> List[String]:
        self._ensure_is_valid()
        return Guitar.get_open_strings(self)


class Guitar:
    STRINGS = [String(6), String(5), String(4), String(3), String(2), String(1)]

    @classmethod
    def get_notes(cls, hand_position: HandPosition) -> List[Note]:
        notes = []
        for string in cls.STRINGS:
            if hand_position.touches(string):
                notes.append(string.note(hand_position.get_fret_on(string)))
            else:
                notes.append(string.note())
        return notes

    @classmethod
    def get_open_strings(cls, hand_position: HandPosition) -> List[String]:
        return sorted(
            [string for string in cls.STRINGS if not hand_position.touches(string)],
            key=lambda s: s.number,
        )


@dataclass(frozen=True)
class PairOfHandPositions:
    first_hand_position: HandPosition
    second_hand_position: HandPosition

    def produces_all_the_notes(self) -> bool:
        all_notes = (
            self.first_hand_position.get_notes() + self.second_hand_position.get_notes()
        )
        return len(set(all_notes)) == 12

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, PairOfHandPositions):
            return NotImplemented

        return {self.first_hand_position, self.second_hand_position} == {
            other.first_hand_position,
            other.second_hand_position,
        }

    def __repr__(self) -> str:
        return (
            f"{str(self.first_hand_position.get_notes())},"
            f" {str(self.second_hand_position.get_notes())}"
        )

    def display_open_strings(self) -> str:
        open_strings_from_first_guitar = ", ".join(
            [str(string) for string in self.first_hand_position.get_open_strings()]
        )
        open_strings_from_second_guitar = ", ".join(
            [str(string) for string in self.second_hand_position.get_open_strings()]
        )
        return (
            f"Open strings: {open_strings_from_first_guitar}"
            f" and {open_strings_from_second_guitar}"
        )


def generate_all_placements(number_of_frets_to_consider: int) -> List[Placement]:
    placements = []
    for string in Guitar.STRINGS:
        for fret in [Fret(i) for i in range(number_of_frets_to_consider)]:
            placements.append(Placement(string, fret))
    return placements


def filter_placements_given_lowest_fret(
    placements: List[Placement], fret: Fret, maximum_span: int
) -> List[Placement]:
    return [
        p
        for p in placements
        if p.fret.number >= fret.number
        and p.fret.number <= fret.number + maximum_span - 1
    ]


def all_hand_positions_with_n_fingers(
    placements: List[Placement], n: int
) -> Set[HandPosition]:
    if n == 0:
        return {HandPosition(frozenset())}

    all_hand_positions = set()
    for p in placements:
        for hand_position in all_hand_positions_with_n_fingers(placements, n - 1):
            if p not in hand_position:
                new_hand_position = HandPosition(
                    frozenset((*hand_position.placements, p))
                )
                all_hand_positions.add(new_hand_position)

    return all_hand_positions


def generate_hand_positions_for_a_set_of_placements(
    placements: List[Placement],
) -> Set[HandPosition]:
    hand_positions = set()
    for i in range(NUMBER_OF_FINGERS_TO_CONSIDER + 1):
        for hand_position in all_hand_positions_with_n_fingers(placements, i):
            hand_positions.add(hand_position)
    return hand_positions


def generate_all_potential_hand_positions(
    number_of_frets_to_consider: int,
) -> Set[HandPosition]:
    all_placements = generate_all_placements(number_of_frets_to_consider)
    all_hand_positions: Set[HandPosition] = set()
    highest_fret = max(
        number_of_frets_to_consider - MAXIMUM_SPAN_OF_FRETS + 1, MAXIMUM_SPAN_OF_FRETS
    )
    frets_to_consider_as_lowest_fret = [Fret(i) for i in range(0, highest_fret)]
    for lowest_fret in frets_to_consider_as_lowest_fret:
        placements_starting_on_this_fret = filter_placements_given_lowest_fret(
            all_placements, lowest_fret, MAXIMUM_SPAN_OF_FRETS
        )
        hand_positions_starting_on_this_fret = (
            generate_hand_positions_for_a_set_of_placements(
                placements_starting_on_this_fret
            )
        )
        all_hand_positions = all_hand_positions.union(
            hand_positions_starting_on_this_fret
        )
    return all_hand_positions


def filter_out_unreasonable_hand_positions(
    hand_positions: Set[HandPosition],
) -> Set[HandPosition]:
    return {hp for hp in hand_positions if hp.is_valid()}


def generate_all_hand_positions(number_of_frets_to_consider: int) -> Set[HandPosition]:
    return filter_out_unreasonable_hand_positions(
        generate_all_potential_hand_positions(number_of_frets_to_consider)
    )


def filter_out_hand_positions_with_repeated_notes(
    hand_positions: Set[HandPosition],
) -> Set[HandPosition]:
    return {
        hand_position
        for hand_position in hand_positions
        if hand_position.get_number_of_distinct_notes() == 6
    }


def work_out_successful_pairs_of_hand_positions(
    hand_positions: Set[HandPosition],
) -> Set[PairOfHandPositions]:
    successful_hand_positions: Set[PairOfHandPositions] = set()
    number_of_cases = len(hand_positions) ** 2
    print(f"Looking through {number_of_cases:,} pairs...")

    count = 0
    for x in hand_positions:
        for y in hand_positions:
            count += 1
            if count % 250_000 == 0:
                print(f"Done {count:,}")
            pair = PairOfHandPositions(x, y)
            if pair.produces_all_the_notes():
                already_found = False
                for existing_pair in successful_hand_positions:
                    if existing_pair == pair:
                        already_found = True
                if not already_found:
                    successful_hand_positions.add(pair)
    return successful_hand_positions
