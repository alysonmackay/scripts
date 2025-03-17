import csv
import re
import os
import glob

import plotnine as p9
import pandas as pd


_NUM_PRELUDE_LINES = 78


if __name__ == "__main__":
    parent_dir = os.path.basename(os.getcwd())

    input_files = glob.glob("*.csv")
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
        raise ValueError(f"Each file name in the directory must contain a number.")

    with open(f"{parent_dir}.csv", "w") as f:
        writer = csv.writer(f)

        writer.writerow(["Wavelength"] + sorted_keys)
        for step, wavelength in enumerate(wavelengths):
            row = [wavelength]
            for key in sorted_keys:
                row.append(AoA[key][step])
            writer.writerow(row)

    print(f"Output written to {parent_dir}.csv")

# Plotting the data from the output file

    with open(f"{parent_dir}.csv", "r") as f:
        rows = [row[:-1] for row in csv.reader(f)]

        # Skip header.
        header = rows[0]
        rows = rows[1:]

        for row in rows:
            records.extend(
                {
                    "wavelength": float(row[0]),
                    "absorbances": float(a),
                    "category": int(i),
                }
                for i, a in enumerate(row[1:])
            )

    df = pd.DataFrame.from_records(records)

    p = (
        p9.ggplot(df, p9.aes(x="wavelength", y="absorbances"))
        + p9.geom_line(p9.aes(color="factor(category)"))
        + p9.xlab("Wavelength (nm)")
        + p9.ylab("Absorbance")
	+ p9.labs(color="Volumes")
	+ p9.theme_bw()
        + p9.scale_x_continuous(limits=(500, 1100))
        + p9.scale_y_continuous(limits=(0, 1))
        + p9.ggtitle(f"{parent_dir}.csv")
    )

    filename = os.path.splitext(os.path.basename("plot.csv"))[0]
    directory = os.path.dirname("plot.csv")
    output_path = os.path.join(directory, f"{filename}.png")

    print(f"Writing plot to: {output_path}")
    p.save(output_path, width=8, height=6, dpi=600)
