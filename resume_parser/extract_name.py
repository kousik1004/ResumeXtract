import os
import re

def extract_name(filename):
    base_name = os.path.splitext(os.path.basename(filename))[0]
    base_name = re.sub(r'\(\d+\)', '', base_name)
    name_parts = base_name.split('_')
    name_without_numbers = ' '.join(part for part in name_parts if not part.isdigit())
    return name_without_numbers.title().strip()
