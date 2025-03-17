import argparse
import csv
import re
import os
import glob

parser = argparse.ArgumentParser()
parser.add_argument(
    "--input_dir",
    type=str,
    required=True,
    help="Path to the directory containing the input CSV files",
)
parser.add_argument(
    "--output_file",
    type=str,
    required=True,
    help="Path to the output CSV file.",
)


_INTERVAL = 1
_STEP = 1
_NUM_PRELUDE_LINES = 78


if __name__ == "__main__":
    args = parser.parse_args()

    input_files = glob.glob(f"{args.input_dir}/*.csv")
    print(f"Found {len(input_files)} CSV files.")

    sorted_input_files = sorted(input_files)

    AoA = {}
    for input_file in sorted_input_files:
        input_file_name = os.path.splitext(os.path.basename(input_file))[0]

        with open(input_file, "r") as f:
            # Skip start of file.
            for _ in range(_NUM_PRELUDE_LINES):
                next(f)

            reader = csv.DictReader(f)
            records = list(reader)

            # We only need the absorbance values.
            absorbance = [r["Absorbance #1"] for r in records]
            # Store the wavelengths for later.
            wavelengths = [float(r["Wavelength"]) for r in records]

            AoA[input_file_name] = absorbance

    try:
        sorted_keys = sorted(
            AoA.keys(), key=lambda x: int(re.search(r"(\d+)", x).group(0))
        )
    except AttributeError:
        raise ValueError(f"Each file name in {args.input_dir} must contain a number.")

    with open(args.output_file, "w") as f:
        writer = csv.writer(f)

        writer.writerow(["Wavelength"] + sorted_keys)
        for step, wavelength in enumerate(wavelengths):
            row = [wavelength]
            for key in sorted_keys:
                row.append(AoA[key][step])
            writer.writerow(row)

    print(f"Output written to {args.output_file}.")
