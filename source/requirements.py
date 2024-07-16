# Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import os
import platform
import subprocess
from pathlib import Path

PLATFORM_SYSTEM = platform.system().lower()
PLATFORM_MACHINE = platform.machine()

if PLATFORM_MACHINE == "i686" or PLATFORM_MACHINE == "AMD64":
    PLATFORM_MACHINE = "x86_64"

SCRIPT_DIR = Path(os.path.dirname(os.path.realpath(__file__))).resolve()
ROOT_DIR = SCRIPT_DIR.parents[0]
DEPS_DIR = ROOT_DIR.joinpath("_build", "target-deps")

if PLATFORM_SYSTEM == "windows":
    PYTHON_EXE = DEPS_DIR.joinpath("python", "python")
else:
    PYTHON_EXE = DEPS_DIR.joinpath("python", "bin", "python3")
REQ_FILE = SCRIPT_DIR.joinpath("requirements.txt")
subprocess.run(f"{PYTHON_EXE} -m pip install -r {REQ_FILE}", shell=True)
