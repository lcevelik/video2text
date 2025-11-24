import os
import sys
from app.fonixflow_qt import main

if __name__ == "__main__":
    # Set the edition flag to FREE
    os.environ["FONIXFLOW_EDITION"] = "FREE"
    # Force CPU only for free version
    os.environ["FONIXFLOW_DEVICE"] = "cpu"
    main()
