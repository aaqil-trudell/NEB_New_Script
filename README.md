# Electrical Test Data Collection & Processing

## Data Storage Locations

- **Oscilloscope**  
  `G:\R&D\MechProdDev\Projects\Concept Development\2306 NT2\Testing\Electrical\Oscilliscope`

- **UC Logger**  
  `G:\R&D\MechProdDev\Projects\Concept Development\2306 NT2\Testing\Electrical\UClogger`

- **VNA**  
  `G:\R&D\MechProdDev\Projects\Concept Development\2306 NT2\Testing\Electrical\VNA`

---

## Script Workflow

### Part 1: File Selection & Validation

1. **Enter ES Number**  
   The user enters the **ES Number** of the NEB.

2. **Search for Oscilloscope Data**  
   The script searches the **Oscilloscope directory** on the G: drive for all `.csv` files starting with that ES number.  
   - If multiple matches are found, the script will prompt the user to select the correct file.  
   - If only one match is found, the script will confirm with the user that it is correct.

3. **Repeat for UC Logger Data**  
   The same process is repeated for the **UC Logger** directory using the same ES number.

4. **Repeat for VNA Data**  
   The same process is repeated for the **VNA** directory using the same ES number.

---

### Part 2: Data Analysis & Output

Once all three `.csv` files are identified:

- The script performs **calculations** and **data analysis**.
- A **master CSV file** is generated with:
  - **Column:** ES Number  
  - **Rows:**  
    1. Oscilloscope (3 metrics)  
    2. UC Logger (3 metrics)  
    3. VNA metrics

---

## Summary

This script automates:
- Locating test data from **Oscilloscope**, **UC Logger**, and **VNA** sources  
- Confirming correct files  
- Performing calculations  
- Generating a single unified **master CSV** for analysis
