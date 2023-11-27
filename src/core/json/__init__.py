from pathlib import Path
from ..raspifmsettings import serialization_directory

if not Path(serialization_directory).is_dir():
    Path(serialization_directory).mkdir(parents=True, exist_ok=True)

if not Path(serialization_directory, "cache/").is_dir():    
    Path(serialization_directory, "cache/").mkdir(parents=True, exist_ok=True)