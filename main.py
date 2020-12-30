from collections import defaultdict
from typing import List

from guitars import (
    filter_out_hand_positions_with_repeated_notes,
    filter_out_solutions_without_the_right_open_strings,
    generate_all_hand_positions,
    PairOfHandPositions,
    String,
    work_out_successful_pairs_of_hand_positions,
)

NUMBER_OF_FRETS_TO_CONSIDER = 8


def main():
    all_hand_positions = generate_all_hand_positions(NUMBER_OF_FRETS_TO_CONSIDER)
    print(f"Found {len(all_hand_positions)} hand-positions.")
    if not all_hand_positions:
        print("That seems odd. Terminating.")
        return

    hand_positions_with_no_repeated_notes = (
        filter_out_hand_positions_with_repeated_notes(all_hand_positions)
    )
    print(
        f"Found {len(hand_positions_with_no_repeated_notes)}"
        " hand-positions which lead to no repeated notes."
    )

    solutions = work_out_successful_pairs_of_hand_positions(
        hand_positions_with_no_repeated_notes
    )

    solutions_with_five_open_strings_including_bottom_e = (
        filter_out_solutions_without_the_right_open_strings(
            solutions,
            {String(i) for i in range(2, 7)},
        )
    )

    solutions_with_five_open_strings_including_top_e = (
        filter_out_solutions_without_the_right_open_strings(
            solutions,
            {String(i) for i in range(1, 6)},
        )
    )

    all_good_solutions = (
        solutions_with_five_open_strings_including_bottom_e
        + solutions_with_five_open_strings_including_top_e
    )

    organised_solutions = organise_pairs_and_order_them(all_good_solutions)

    print(f"Found {len(organised_solutions)} solution-pairs.")

    successful_hand_positions = set()
    for solution in organised_solutions:
        successful_hand_positions.add(solution.first_hand_position)
        successful_hand_positions.add(solution.second_hand_position)

    instances = defaultdict(int)
    for hand_position in successful_hand_positions:
        count = 0
        for solution in organised_solutions:
            if hand_position in solution:
                count += 1
        instances[count] += 1

    print(instances)

    with open("solutions-open-strings.txt", "w") as f:
        for solution in organised_solutions:
            f.write(f"{str(solution)}\n")


def organise_pairs_and_order_them(
    pairs_of_hand_positions: List[PairOfHandPositions],
) -> List[PairOfHandPositions]:
    pairs_with_the_lowest_always_first = [
        pair.organise_with_lowest_hand_first() for pair in pairs_of_hand_positions
    ]

    for pair in pairs_with_the_lowest_always_first:
        print(pair)

    return pairs_with_the_lowest_always_first


if __name__ == "__main__":
    main()
