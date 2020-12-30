from collections import defaultdict

from guitars import (
    filter_out_hand_positions_with_repeated_notes,
    generate_all_hand_positions,
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

    print(f"Found {len(solutions)} solution-pairs.")

    open_string_counts = defaultdict(int)
    for solution in solutions:
        number_of_open_strings = len(
            solution.first_hand_position.get_open_strings()
        ) + len(solution.second_hand_position.get_open_strings())
        open_string_counts[number_of_open_strings] += 1

    if len(solutions) > 0:
        print(
            f"{open_string_counts[5]} of them have 5"
            " open strings across both guitars;"
            f" the rest ({open_string_counts[4]}) have 4."
        )

    with open("solutions.txt", "w") as f:
        for solution in solutions:
            f.write(f"{str(solution)} {solution.display_open_strings()}.\n")


if __name__ == "__main__":
    main()
