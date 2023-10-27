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
from pxr import Usd, Sdf, Gf, UsdGeom
from pathlib import Path
import time
import random

OMNI_HOST = os.environ.get("OMNI_HOST", "localhost")
BASE_URL = "omniverse://" + OMNI_HOST + "/Projects/IoT/Samples/HeadlessApp"
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONTENT_DIR = Path(SCRIPT_DIR).resolve().parents[1].joinpath("content")

messages = []


class LivePrim:
    def __init__(self, stage: Usd.Stage):
        points = [
            (50, 50, 50),
            (-50, 50, 50),
            (-50, -50, 50),
            (50, -50, 50),
            (-50, -50, -50),
            (-50, 50, -50),
            (50, 50, -50),
            (50, -50, -50),
        ]
        faceVertexIndices = [0, 1, 2, 3, 4, 5, 6, 7, 0, 6, 5, 1, 4, 7, 3, 2, 0, 3, 7, 6, 4, 2, 1, 5]
        faceVertexCounts = [4, 4, 4, 4, 4, 4]

        cube = stage.GetPrimAtPath("/World/cube")
        if not cube:
            cube = stage.DefinePrim("/World/cube", "Cube")

        if not cube:
            raise Exception("Could load the cube: /World/cube.")

        # cube.GetAttribute("size").Set(2.0)

        mesh = stage.GetPrimAtPath("/World/cube/mesh")
        if not mesh:
            mesh = UsdGeom.Mesh.Define(stage, "/World/cube/mesh")
            mesh.CreatePointsAttr().Set(points)
            mesh.CreateFaceVertexIndicesAttr().Set(faceVertexIndices)
            mesh.CreateFaceVertexCountsAttr().Set(faceVertexCounts)
            mesh.CreateDoubleSidedAttr().Set(False)
            mesh.CreateSubdivisionSchemeAttr("bilinear")
            mesh.CreateDisplayColorAttr().Set([(0.463, 0.725, 0.0)])
            mesh.AddTranslateOp().Set(Gf.Vec3d(0.0))
            mesh.AddScaleOp().Set(Gf.Vec3f(0.8535))
            mesh.AddTransformOp().Set(Gf.Matrix4d(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1))

        self._rotation_increment = Gf.Vec3f(
            random.uniform(-1.0, 1.0) * 10.0, random.uniform(-1.0, 1.0) * 10.0, random.uniform(-1.0, 1.0) * 10.0
        )

        self._rotateXYZOp = None
        xformable = UsdGeom.Xformable(cube)
        for op in xformable.GetOrderedXformOps():
            if op.GetOpType() == UsdGeom.XformOp.TypeRotateXYZ:
                self._rotateXYZOp = op

        if self._rotateXYZOp is None:
            self._rotateXYZOp = xformable.AddRotateXYZOp()
        self._rotation = Gf.Vec3f(0.0, 0.0, 0.0)
        self._rotateXYZOp.Set(self._rotation)

    def _increment(self):
        if abs(self._rotation[0] + self._rotation_increment[0]) > 360.0:
            self._rotation_increment[0] *= -1.0
        if abs(self._rotation[1] + self._rotation_increment[1]) > 360.0:
            self._rotation_increment[1] *= -1.0
        if abs(self._rotation[2] + self._rotation_increment[2]) > 360.0:
            self._rotation_increment[2] *= -1.0

        self._rotation[0] += self._rotation_increment[0]
        self._rotation[1] += self._rotation_increment[1]
        self._rotation[2] += self._rotation_increment[2]

    def write_to_live(self, live_layer):
        # write the transformation the usd prim attributes
        self._increment()
        self._rotateXYZOp.Set(self._rotation)


def log_handler(thread, component, level, message):
    # print(message)
    messages.append((thread, component, level, message))


async def initialize_async():
    # copy a the Conveyor Belt to the target nucleus server
    IOT_TOPIC = "Dancing_Cubes"
    STAGE_URL = f"{BASE_URL}/{IOT_TOPIC}.usd"
    LIVE_URL = f"{BASE_URL}/{IOT_TOPIC}.live"

    try:
        stage = Usd.Stage.Open(STAGE_URL)
    except:
        stage = Usd.Stage.CreateNew(STAGE_URL)

    if not stage:
        raise Exception(f"Could load the stage {STAGE_URL}.")

    root_layer = stage.GetRootLayer()
    live_layer = Sdf.Layer.FindOrOpen(LIVE_URL)
    if not live_layer:
        live_layer = Sdf.Layer.CreateNew(LIVE_URL)

    if not live_layer:
        raise Exception(f"Could load the live layer {LIVE_URL}.")

    found = False
    subLayerPaths = root_layer.subLayerPaths
    for subLayerPath in subLayerPaths:
        if subLayerPath == live_layer.identifier:
            found = True

    if not found:
        root_layer.subLayerPaths.append(live_layer.identifier)
        root_layer.Save()

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
    live_prim = LivePrim(stage)
    omni.client.live_process()

    for x in range(iterations):
        with Sdf.ChangeBlock():
            live_prim.write_to_live(live_layer)
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
        print('---- LOG MESSAGES ---')
        print(*messages, sep='\n')
        print('----')
    finally:
        omni.client.shutdown()
