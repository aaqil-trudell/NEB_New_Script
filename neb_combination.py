import os
import csv
import numpy as np
import pandas as pd
from settings import main
from settings import fmt_hz
from settings import default_settings
from datetime import datetime

# Specify the correct paths
Scope_path = r"C:\Users\aaqil.murji\OneDrive - TRUDELL MEDICAL LIMITED\Desktop\NEB Script\Scope"
logger_path = r"C:\Users\aaqil.murji\OneDrive - TRUDELL MEDICAL LIMITED\Desktop\NEB Script\UClogger"
VNA_path = r"C:\Users\aaqil.murji\OneDrive - TRUDELL MEDICAL LIMITED\Desktop\NEB Script\VNA"

# Calling the main function from settings which reads values from the JSON file
SEARCHBAND_SCALE = main()

while True:
    # Prompt the user for the ES number
    ES_number = input("What is the ES number of the NEB to analyze? ")

    # Directories to search
    directories = {
        "Scope": Scope_path,
        "Logger": logger_path,
        "VNA": VNA_path
    }

    selected_files = {}

    # Search for matching files in each directory
    for name, path in directories.items():
        matching_files = []
        for root, _, files in os.walk(path):
            for file in files:
                if file.startswith(ES_number) and file.endswith('.csv'):
                    matching_files.append(os.path.join(root, file))

        # Auto-select if only one file is found, otherwise ask user
        if len(matching_files) == 1:
            selected_files[name] = matching_files[0]
            print(f"Automatically selected {matching_files[0]} for {name}.")
        elif len(matching_files) > 1:
            print(f"\nMatching CSV files in {name}:")
            for idx, file in enumerate(matching_files, 1):
                print(f"{idx}: {file}")

            choice = int(input(f"Select the {name} file (1-{len(matching_files)}): ")) - 1
            selected_files[name] = matching_files[choice]
        else:
            print(f"No matching CSV file found in {name} directory.")
            break
    else:
        # If all three files are found, proceed
        print("\nMaking the big CSV based on:")
        for key, file in selected_files.items():
            print(f"{key}: {file}")

        # Prepare the output data structure
        output_data = [["ES_Number", ES_number],
                       ["Scope Frequency"], ["Scope Phase"], ["Scope Z"], ["Scope Power"],
                       ["Logger Neb Efficiency"], ["Logger Neb Freq"], ["Logger Neb Phase"],
                       ["Logger Neb Voltage"], ["Logger Neb Current"], ["Logger Neb Impedance"],
                       ["Logger Neb Power"], ["VNA_Fs"], ["VNA_Fr"], ["VNA_k_squared"], ["VNA_Z_r"],
                       ["VNA_Z_s"]]

        # Extract Scope CSV data
        with open(selected_files["Scope"], 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            if len(rows) > 4 and len(rows[3]) >= 4:
                B4 = float(rows[3][1]) / 1000
                G4 = float(rows[3][6])
                D4 = float(rows[3][3])
                C4 = float(rows[3][2])
                Z_r1 = ((C4 / (2 * (2 ** 0.5))) ** 2) / D4
                output_data[1].append(B4)
                output_data[2].append(G4)
                output_data[3].append(Z_r1)
                output_data[4].append(D4)
            else:
                print(f"File {selected_files['Scope']} does not have sufficient data.")

        # Extract Logger CSV data
        with open(selected_files["Logger"], 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            if len(rows) == 27 and len(rows[0]) == 5:
                D2 = float(rows[1][3])
                D3 = float(rows[2][3])
                D4 = float(rows[3][3])
                D5 = float(rows[4][3])
                D6 = float(rows[5][3])
                D7 = float(rows[6][3])
                D8 = float(rows[7][3])
                output_data[5].append(D2)
                output_data[6].append(D3)
                output_data[7].append(D4)
                output_data[8].append(D5)
                output_data[9].append(D6)
                output_data[10].append(D7)
                output_data[11].append(D8)
            else:
                print(f"File {selected_files['Logger']} does not have sufficient data.")

        # Extract VNA CSV data

        peak_num = 0
        valid_freq_indices = []
        df = pd.read_csv(selected_files["VNA"], encoding='cp1252', comment='#')
        length = df.shape[0]
        freq = df['freq[Hz]']
        phase = df[df.columns[5]]
        zero_crossings = np.where(np.diff(np.signbit(phase)))[0]
        phase_diff = np.diff(phase)
        expected_sign = 1
        for zero_index in zero_crossings:

            this_diff = phase_diff[zero_index]

            if (expected_sign * this_diff) > 0:
                # Zero crossing is in the expected direction.

                # zero_index identifies the point to the left of the zero crossing.
                # Check the point to the right as well (as long as this doesn't go
                # out of bounds), and choose the frequency with phase closer to 
                # zero as Fs or Fp.
                if (zero_index + 1) <= (length - 1):
                    phase_left = phase.loc[zero_index]
                    phase_right = phase.loc[zero_index + 1]

                    # If phase to the right of the zero crossing is closer to zero,
                    # use that frequency as Fs or Fp.
                    if (abs(phase_right) < abs(phase_left)):
                        zero_index += 1

                if this_diff > 0:
                    Fs_index = zero_index
                    Fs = freq[Fs_index]
                elif this_diff < 0:
                    Fp_index = zero_index
                    Fp = freq[Fp_index]

                    print(f"Fs: {fmt_hz(Fs)}\nFp: {fmt_hz(Fp)}")

                    if (Fp - Fs) >= default_settings["peak_threshold"]:
                        valid_freq_indices.append([Fs_index, Fp_index])
                    else:
                        print(f"Skipped: (Fp - Fs) = {fmt_hz(Fp - Fs)} is less than {fmt_hz(PEAK_THRESHOLD)}.")
                    print()

                # Flip expected sign of zero crossing slope.
                expected_sign *= -1
            elif (expected_sign * this_diff) < 0:
                print("Phase derivative found to be in the wrong direction.")
            else:
                print("Phase derivative found to be zero at zero crossing.")

        phase_diff = np.diff(phase)
        Fp_index = zero_index

        for valid_index_pair in valid_freq_indices:
            peak_num += 1

            Fs = freq.loc[Fs_index]

            search_index_range = Fp_index - Fs_index
            index_extension = int(search_index_range * (SEARCHBAND_SCALE - 1) / 2)
            search_index_L = Fs_index - index_extension
            search_index_R = Fp_index + index_extension

            if search_index_L < 0:
                search_index_L = 0
            if search_index_R > (len(freq) - 1):
                search_index_R = len(freq) - 1

            chopped = df.loc[search_index_L:search_index_R]
            Z_chopped = chopped['Trc2_Z<-S11[Ohm]']

            Fr_index = chopped['Trc1_S11[dB]'].idxmin()
            Fr = freq.loc[Fr_index]

            k_squared = (Fp**2 - Fs**2) / Fp**2
            Z_r = df['Trc2_Z<-S11[Ohm]'].loc[Fr_index]
            phase_r = phase.loc[Fr_index]
            Z_s = Z_chopped[Fs_index]

        output_data[12].append(Fs)
        output_data[13].append(Fr)
        output_data[14].append(k_squared)
        output_data[15].append(Z_r)
        output_data[16].append(Z_s)

        # Convert to DataFrame and save
        output_df = pd.DataFrame(output_data)
        output_df.columns = output_df.iloc[0]
        output_df = output_df[1:]

        # Save the final CSV
        output_file = datetime.today().strftime('%Y-%m-%d_%H-%M') + "_combined.csv"
        output_df.to_csv(output_file, index=False)
        print(f"Big CSV created: {output_file}")
        break
