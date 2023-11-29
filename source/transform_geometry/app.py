# SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

# pip install openpyxl
# pip install pandas

import asyncio
import os
import omni.client
from pxr import Usd, Sdf
from pathlib import Path
import time
from omni.live import LiveEditSession, LiveCube, getUserNameFromToken

OMNI_HOST = os.environ.get("OMNI_HOST", "localhost")
OMNI_USER = os.environ.get("OMNI_USER", "ov")
if OMNI_USER.lower() == "omniverse":
    OMNI_USER = "ov"
elif OMNI_USER.lower() == "$omni-api-token":
    OMNI_USER = getUserNameFromToken(os.environ.get("OMNI_PASS"))

BASE_FOLDER = "omniverse://" + OMNI_HOST + "/Users/" + OMNI_USER + "/iot-samples"
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONTENT_DIR = Path(SCRIPT_DIR).resolve().parents[1].joinpath("content")

messages = []


def log_handler(thread, component, level, message):
    # print(message)
    messages.append((thread, component, level, message))


async def initialize_async():
    # copy a the Conveyor Belt to the target nucleus server
    stage_name = "Dancing_Cubes"
    stage_folder = f"{BASE_FOLDER}/{stage_name}"
    stage_url = f"{stage_folder}/{stage_name}.usd"

    try:
        stage = Usd.Stage.Open(stage_url)
    except:
        stage = Usd.Stage.CreateNew(stage_url)

    if not stage:
        raise Exception(f"Could load the stage {stage_url}.")

    live_session = LiveEditSession(stage_url)
    live_layer = await live_session.ensure_exists()

    session_layer = stage.GetSessionLayer()
    session_layer.subLayerPaths.append(live_layer.identifier)

    # set the live layer as the edit target
    stage.SetEditTarget(live_layer)
    stage.DefinePrim("/World", "Xform")
    omni.client.live_process()
    return stage, live_layer


def run(stage, live_layer):
    # we assume that the file contains the data for single device

    # play back the data in at 30fps for 20 seconds
    delay = 0.033
    iterations = 600
    live_cube = LiveCube(stage)
    omni.client.live_process()

    for x in range(iterations):
        with Sdf.ChangeBlock():
            live_cube.rotate()
        omni.client.live_process()
        time.sleep(delay)


if __name__ == "__main__":
    omni.client.initialize()
    omni.client.set_log_level(omni.client.LogLevel.DEBUG)
    omni.client.set_log_callback(log_handler)
    try:
        stage, live_layer = asyncio.run(initialize_async())
        run(stage, live_layer)
    except:
        print("---- LOG MESSAGES ---")
        print(*messages, sep="\n")
        print("----")
    finally:
        omni.client.shutdown()
