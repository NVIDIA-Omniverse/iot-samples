# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import sys

import carb.settings
import omni.kit.app
import omni.kit.actions.core
from omni.kit.core.tests import validate_extensions_load, validate_extensions_tests
from omni.kit.test import AsyncTestCase
from pxr import Usd, UsdGeom, Gf


class TestUSDExplorerExtensions(AsyncTestCase):
    async def test_l1_extensions_load(self):
        """Loop all enabled extensions to see if they loaded correctly"""
        self.assertEqual(validate_extensions_load(), 0)

    async def test_regression_omfp_2304(self):
        loaded_omni_kit_collaboration_selection_outline = False
        manager = omni.kit.app.get_app().get_extension_manager()
        for ext in manager.get_extensions():
            if ext["name"] == "omni.kit.collaboration.selection_outline":
                loaded_omni_kit_collaboration_selection_outline = True
                break
        self.assertTrue(loaded_omni_kit_collaboration_selection_outline)

    async def _wait(self, frames: int = 10):
        for _ in range(frames):
            await omni.kit.app.get_app().next_update_async()

    async def wait_stage_loading(self):
        while True:
            _, files_loaded, total_files = omni.usd.get_context().get_stage_loading_status()
            if files_loaded or total_files:
                await self._wait()
                continue
            break
        await self._wait(100)

    async def _get_1_1_1_rotation(self) -> Gf.Vec3d:
        """Loads a stage and returns the transformation of the (1,1,1) vector by the directional light's rotation"""
        await self._wait()
        omni.kit.actions.core.execute_action("omni.kit.window.file", "new")
        await self.wait_stage_loading()
        context = omni.usd.get_context()
        self.assertIsNotNone(context)
        stage = context.get_stage()
        self.assertIsNotNone(stage)

        prim_path = '/Environment/DistantLight'
        prim = stage.GetPrimAtPath(prim_path)
        self.assertTrue(prim.IsValid())

        # Extract the prim's transformation matrix in world space
        xformAPI = UsdGeom.XformCache()
        transform_matrix_world = xformAPI.GetLocalToWorldTransform(prim)

        unit_point = Gf.Vec3d(1, 1, 1)
        transformed_point = transform_matrix_world.Transform(unit_point)
        return transformed_point
