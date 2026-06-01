import json
import os
import numpy as np
from tkinter import filedialog, Tk

def import_preset():
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    file_path = filedialog.askopenfilename(
        initialdir=os.path.join(os.getcwd(), 'preset'),
        title="Pilih preset kamera",
        filetypes=[('JSON Files', '*.json')]
    )
    root.destroy()

    if file_path:
        with open(file_path, 'r') as f:
            data = json.load(f)
            preset_name = os.path.splitext(os.path.basename(file_path))[0]
            return np.array(data['lower']), np.array(data['upper']), preset_name
    
    # kalau di cancel
    return None, None, None