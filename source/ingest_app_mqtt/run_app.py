# Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import os
import argparse
import platform
import subprocess
from pathlib import Path

PLATFORM_SYSTEM = platform.system().lower()
PLATFORM_MACHINE = platform.machine()

if PLATFORM_MACHINE == "i686" or PLATFORM_MACHINE == "AMD64":
    PLATFORM_MACHINE = "x86_64"

CURRENT_PLATFORM = f"{PLATFORM_SYSTEM}-{PLATFORM_MACHINE}"

default_username = os.environ.get("OMNI_USER")
default_password = os.environ.get("OMNI_PASS")
default_server = os.environ.get("OMNI_HOST", "localhost")

parser = argparse.ArgumentParser()
parser.add_argument("--server", "-s", default=default_server)
parser.add_argument("--username", "-u", default=default_username)
parser.add_argument("--password", "-p", default=default_password)
parser.add_argument("--config", "-c", choices=["debug", "release"], default="release")
parser.add_argument("--platform", default=CURRENT_PLATFORM)
args = parser.parse_args()

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = Path(SCRIPT_DIR).resolve().parents[1]

BUILD_DIR = ROOT_DIR.joinpath("_build", args.platform, args.config)
DEPS_DIR = ROOT_DIR.joinpath("_build", "target-deps")
USD_BIN_DIR = DEPS_DIR.joinpath("usd", args.config, "bin")
USD_LIB_DIR = DEPS_DIR.joinpath("usd", args.config, "lib")
CLIENT_LIB_DIR = DEPS_DIR.joinpath("omni_client_library", args.config)
RESOLVER_DIR = DEPS_DIR.joinpath("omni_usd_resolver", args.config)

EXTRA_PATHS = [str(CLIENT_LIB_DIR), str(USD_BIN_DIR), str(USD_LIB_DIR), str(BUILD_DIR), str(RESOLVER_DIR)]
EXTRA_PYTHON_PATHS = [
    str(Path(SCRIPT_DIR).resolve().parents[0]),
    str(USD_LIB_DIR.joinpath("python")),
    str(CLIENT_LIB_DIR.joinpath("bindings-python")),
    str(BUILD_DIR.joinpath("bindings-python")),
]

if PLATFORM_SYSTEM == "windows":
    os.environ["PATH"] += os.pathsep + os.pathsep.join(EXTRA_PATHS)
    ot_bin = "carb.omnitrace.plugin.dll"
else:
    p = os.environ.get("LD_LIBRARY_PATH", "")
    p += os.pathsep + os.pathsep.join(EXTRA_PATHS)
    os.environ["LD_LIBRARY_PATH"] = p
    ot_bin = "libcarb.omnitrace.plugin.so"

os.environ["OMNI_TRACE_LIB"] = os.path.join(str(DEPS_DIR), "omni-trace", "bin", ot_bin)
os.environ["PYTHONPATH"] = os.pathsep + os.pathsep.join(EXTRA_PYTHON_PATHS)
os.environ["OMNI_USER"] = args.username
os.environ["OMNI_PASS"] = args.password
os.environ["OMNI_HOST"] = args.server

if PLATFORM_SYSTEM == "windows":
    PYTHON_EXE = DEPS_DIR.joinpath("python", "python")
else:
    PYTHON_EXE = DEPS_DIR.joinpath("python", "bin", "python3")

plugin_paths = DEPS_DIR.joinpath("omni_usd_resolver", args.config, "usd", "omniverse", "resources")
os.environ["PXR_PLUGINPATH_NAME"] = str(plugin_paths)
REQ_FILE = ROOT_DIR.joinpath("requirements.txt")
subprocess.run(f"{PYTHON_EXE} -m pip install -r {REQ_FILE}", shell=True)
result = subprocess.run(
    [PYTHON_EXE, os.path.join(SCRIPT_DIR, "app.py")],
    stderr=subprocess.STDOUT,
)
