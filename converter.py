import logging
import traceback
from wanakana import to_katakana, is_kana
import random
import zipfile
import json
from collections import defaultdict
from pathlib import Path
import argparse

# Constants
INPUT_FOLDER = Path("dicts")
OUTPUT_FOLDER = Path("output")
LOGS_FOLDER = Path("logs")
LOG_FILE = LOGS_FOLDER / "converter.log"


logger = logging.getLogger("converter")


def setup_logging():
    """Set up basic logging to a file."""
    LOGS_FOLDER.mkdir(exist_ok=True)  # Ensure logs directory exists
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.DEBUG,
        format="%(levelname)s : %(message)s",
    )


def process_term_bank(term_bank, archive):
    """Process a single term bank and return the frequency dictionary."""
    logger.debug(f"Processing term bank: {term_bank}.")
    frequency_dict = defaultdict(list)

    with archive.open(term_bank, "r") as f:
        json_dict = json.load(f)
        for term_list in json_dict:
            word = (
                term_list[0].replace("\ufeff", "").strip()
            )  # Remove the BOM character common in some Chinese frequency lists
            frequency, dict_entry = handle_term_list(term_list, word)
            if dict_entry:
                frequency_dict[frequency].append(dict_entry)

    return frequency_dict


def handle_term_list(term_list, word):
    """Extract frequency and create a dictionary entry from term_list."""
    if isinstance(term_list[2], dict):
        info_dict = term_list[2]
        frequency = info_dict.get("value", None) or info_dict["frequency"]

        if isinstance(frequency, dict):
            frequency = frequency["value"]

        reading = info_dict.get("reading", None)
        if reading:
            reading = to_katakana(info_dict["reading"])
            return frequency, [word, reading]
        else:
            return frequency, [word]
    if isinstance(term_list[2], str):
        frequency = term_list[2].split("/")[0]
        return frequency, [word]
    if isinstance(term_list[2], int):
        frequency = term_list[2]
        return frequency, [word]

    # Unsupported format
    logger.warning(f"Unsupported format in {term_list}: ")
    return None, None


def convert_hiragana_to_katakana(frequency_dict):
    """Convert hiragana readings to katakana if necessary."""
    logger.debug("Converting hiragana readings to katakana.")
    for frequency, words in frequency_dict.items():
        for i, word_and_reading_or_word in enumerate(words):
            if len(word_and_reading_or_word) == 2:
                continue
            word = word_and_reading_or_word[0]
            if is_kana(word):
                frequency_dict[frequency][i].append(to_katakana(word))


def save_frequency_list(frequency_list, output_path):
    """Save the frequency list to a file."""
    logger.debug("Saving the frequency list.")
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(frequency_list, f, ensure_ascii=False)


def print_test_cases(frequency_list, num_tests):
    """Print test cases. Used to manually ensure the conversion was successful."""
    print("Tests:")
    for _ in range(num_tests):
        i = random.randrange(len(frequency_list))
        print(f"Position {i + 1}: {frequency_list[i]}")


def main():
    setup_logging()
    logger.info("Starting conversion process.")

    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Convert dictionary files.")
    parser.add_argument(
        "-t",
        "--tests",
        type=int,
        default=0,
        help="Number of test cases to print after conversion.",
    )
    args = parser.parse_args()

    # Converter code starts
    for archive_path in INPUT_FOLDER.iterdir():
        if archive_path.suffix != ".zip":
            print(
                f"Can't convert {archive_path.name}: {archive_path.suffix} is not a valid dictionary format. Skipping."
            )
            logger.warning(f"Skipped {archive_path.name}: unsupported format.")
            continue
        try:
            logger.info(f"Processing archive: {archive_path.name}.")

            # Loading dictionary files
            archive = zipfile.ZipFile(archive_path)
            term_banks = [
                file_info.filename
                for file_info in archive.filelist
                if file_info.filename.startswith("term_meta_bank_")
            ]
            logger.debug(
                f"Found {len(term_banks)} term bank files in {archive_path.name}."
            )

            # Converting the files to a single dictionary
            frequency_dict = defaultdict(list)
            has_readings = False

            for term_bank in term_banks:
                frequency_dict.update(process_term_bank(term_bank, archive))

            # Convert hiragana readings to katakana if necessary
            if has_readings:
                convert_hiragana_to_katakana(frequency_dict)

            # Create a Migaku format frequency list
            logger.debug("Creating a frequency list.")
            frequency_list = [
                term if has_readings else term[0]
                for frequency, words in sorted(
                    frequency_dict.items(), key=lambda item: item[0]
                )
                for term in words
            ]

            # Ensure the output directory exists
            OUTPUT_FOLDER.mkdir(exist_ok=True)

            # Save the frequency list to a file
            new_name = archive_path.stem + ".json"
            output_path = OUTPUT_FOLDER / new_name
            save_frequency_list(frequency_list, output_path)

            print(f"Successfully converted {archive_path.name} to {new_name}")
            logger.info(f"Conversion of {archive_path.name} successful.")

            # Print test cases if -t flag is provided with a number
            if args.tests > 0:
                print_test_cases(frequency_list, args.tests)

        except Exception as e:
            error_message = (
                f"Unexpected error converting {archive_path.name}. Skipping."
            )
            print(error_message)
            logger.error(f"{error_message}\n{traceback.format_exc()}")

    logger.info("Conversion process complete.")


if __name__ == "__main__":
    main()
