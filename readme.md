# Hospital timetabling
Hospital timetabling implementation with genetic algorithm

# Constraints
 - All nurses that come from input must be present in the output.
 - Each nurse just can work in a specific section.
 - A nurse must not be in two continuous shifts.
 - Output should be with preferences of nurses, i.e., nurse A wants to come in Monday and Tuesday, and Saturday and just in a second and third shift.
 - All nurses must be in equal attendance in a week (as possible).

# How to run
1. Install all dependencies: `pip install -r requirements.txt`

2. Add desired inputs in template.xlsx file (inputs sheet)

3. Run main.py: `python3 main.py`

 output will save in output.xlsx file.
