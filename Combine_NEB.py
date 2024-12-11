# Import OS module
import os

# Specify the correct path
VNA_path = r"G:\R&D\MechProdDev\Projects\Concept Development\2306 NT2\Testing\Electrical\VNA"

while True:
    # Prompt the user for the ES number
    ES_number = input("What is the ES number of the NEB to analyze? ")

    # List to store matching files
    # Look into orderd list!!!!
    matching_files = []

    # Traverse the directory and subdirectories
    for root, dirs, files in os.walk(VNA_path):
        for file in files:
            # Check if the file starts with the ES number and ends with '.csv'
            if file.startswith(ES_number) and file.endswith('.csv'):
                # Construct full file path
                full_path = os.path.join(root, file)
                matching_files.append(full_path)

    # Display the matching files
    if matching_files:
        print("\nMatching CSV files:")
        for file in matching_files:
            print(file)
    else:
        print(f"\nNo matching CSV files found for ES number '{ES_number}'.")

    # Ask if the user wants to search again
    repeat = input("\nWould you like to analyze another NEB? (yes/no): ")
    if repeat.lower() in ['no', 'n']:
        break

print("\nYour big Excel file is saved!")
