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

import omni.ext
import omni.ui as ui
import omni.kit.usd.layers as layers
from pxr import Usd, Sdf, Tf, UsdGeom
import omni.ui.color_utils as cl

TRANSLATE_OFFSET = "xformOp:translate:offset"
ROTATE_SPIN = "xformOp:rotateX:spin"


class uiTextStyles:
    title = {"margin": 10, "color": 0xFFFFFFFF, "font_size": 18, "alignment": ui.Alignment.LEFT_CENTER}
    title2 = {"margin": 10, "color": 0xFFFFFFFF, "font_size": 18, "alignment": ui.Alignment.LEFT_CENTER}


class uiElementStyles:
    mainWindow = {"Window": {"background_color": cl.color(32, 42, 87, 100), "width": 350}}


class uiButtonStyles:
    mainButton = {
        "Button": {"background_color": cl.color(32, 42, 87, 125), "width": 175, "height": 80},
        "Button:hovered": {"background_color": cl.color(32, 42, 87, 200)},
    }

    # geometry manipulation


class LiveCube:
    def __init__(self, stage: Usd.Stage, path: str):
        self._prim = stage.GetPrimAtPath(path)
        self._op = self._prim.HasProperty(TRANSLATE_OFFSET)
        if self._prim:
            self._xform = UsdGeom.Xformable(self._prim)

    def resume(self):
        if self._xform and not self._op:
            op = self._xform.AddTranslateOp(opSuffix="offset")
            op.Set(time=1, value=(0, -20.0, 0))
            op.Set(time=192, value=(0, -440, 0))
            self._op = True

    def pause(self):
        if self._xform and self._op:
            default_ops = []
            for op in self._xform.GetOrderedXformOps():
                if op.GetOpName() != TRANSLATE_OFFSET:
                    default_ops.append(op)
            self._xform.SetXformOpOrder(default_ops)
            self._prim.RemoveProperty(TRANSLATE_OFFSET)
            self._op = False


class LiveRoller:
    def __init__(self, stage: Usd.Stage, path: str):
        self._prim = stage.GetPrimAtPath(path)
        self._op = self._prim.HasProperty(ROTATE_SPIN)
        if self._prim:
            self._xform = UsdGeom.Xformable(self._prim)

    def resume(self):
        if self._xform and not self._op:
            op = self._xform.AddRotateXOp(opSuffix="spin")
            op.Set(time=1, value=0)
            op.Set(time=192, value=1440)
            self._op = True

    def pause(self):
        if self._xform and self._op:
            default_ops = []
            for op in self._xform.GetOrderedXformOps():
                if op.GetOpName() != ROTATE_SPIN:
                    default_ops.append(op)
            self._xform.SetXformOpOrder(default_ops)
            self._prim.RemoveProperty(ROTATE_SPIN)
            self._op = False


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class OmniIotSamplePanelExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[omni.iot.sample.panel] startup")

        self._iot_prim = None
        self.listener = None
        self._stage_event_sub = None
        self._window = None
        self._usd_context = omni.usd.get_context()
        self._stage = self._usd_context.get_stage()
        self._live_syncing = layers.get_live_syncing(self._usd_context)
        self._layers = layers.get_layers(self._usd_context)

        self._selected_prim = None

        self._layers_event_subscription = self._layers.get_event_stream().create_subscription_to_pop_by_type(
            layers.LayerEventType.LIVE_SESSION_STATE_CHANGED,
            self._on_layers_event,
            name=f"omni.iot.sample.panel {str(layers.LayerEventType.LIVE_SESSION_STATE_CHANGED)}",
        )

        self._update_ui()

    def on_shutdown(self):
        self._iot_prim = None
        self.listener = None
        self._stage_event_sub = None
        self._window = None
        self._layers_event_subscription = None
        print("[omni.iot.sample.panel] shutdown")

    def _on_velocity_changed(self, speed):
        print(f"[omni.iot.sample.panel] _on_velocity_changed: {speed}")
        if speed is not None and speed > 0.0:
            with Sdf.ChangeBlock():
                self._cube.resume()
                for roller in self._rollers:
                    roller.resume()
        else:
            with Sdf.ChangeBlock():
                self._cube.pause()
                for roller in self._rollers:
                    roller.pause()

    def _update_frame(self):
        if self._selected_prim is not None:
            self._property_stack.clear()
            properties = self._selected_prim.GetProperties()
            button_height = uiButtonStyles.mainButton["Button"]["height"]
            self._property_stack.height.value = (round(len(properties) / 2) + 1) * button_height
            x = 0
            hStack = ui.HStack()
            self._property_stack.add_child(hStack)
            # repopulate the VStack with the IoT data attributes
            for prop in properties:
                if x > 0 and x % 2 == 0:
                    hStack = ui.HStack()
                    self._property_stack.add_child(hStack)
                prop_name = prop.GetName()
                prop_value = prop.Get()
                ui_button = ui.Button(f"{prop_name}\n{str(prop_value)}", style=uiButtonStyles.mainButton)
                hStack.add_child(ui_button)
                if prop_name == "Velocity":
                    self._on_velocity_changed(prop_value)
                x += 1

            if x % 2 != 0:
                with hStack:
                    ui.Button("", style=uiButtonStyles.mainButton)

    def _on_selected_prim_changed(self):
        print("[omni.iot.sample.panel] _on_selected_prim_changed")
        selected_prim = self._usd_context.get_selection()
        selected_paths = selected_prim.get_selected_prim_paths()
        if selected_paths and len(selected_paths):
            sdf_path = Sdf.Path(selected_paths[0])

            # only handle data that resides under the /iot prim
            if (
                sdf_path.IsPrimPath()
                and sdf_path.HasPrefix(self._iot_prim.GetPath())
                and sdf_path != self._iot_prim.GetPath()
            ):
                self._selected_prim = self._stage.GetPrimAtPath(sdf_path)
                self._selected_iot_prim_label.text = str(sdf_path)
                self._update_frame()

    # ===================== stage events START =======================
    def _on_selection_changed(self):
        print("[omni.iot.sample.panel] _on_selection_changed")
        if self._iot_prim:
            self._on_selected_prim_changed()

    def _on_asset_opened(self):
        print("[omni.iot.sample.panel] on_asset_opened")

    def _on_stage_event(self, event):
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            self._on_selection_changed()
        elif event.type == int(omni.usd.StageEventType.OPENED):
            self._on_asset_opened()

    def _on_objects_changed(self, notice, stage):
        updated_objects = []
        for p in notice.GetChangedInfoOnlyPaths():
            if p.IsPropertyPath() and p.GetParentPath() == self._selected_prim.GetPath():
                updated_objects.append(p)

        if len(updated_objects) > 0:
            self._update_frame()

    # ===================== stage events END =======================

    def _on_layers_event(self, event):
        payload = layers.get_layer_event_payload(event)
        if not payload:
            return

        if payload.event_type == layers.LayerEventType.LIVE_SESSION_STATE_CHANGED:
            if not payload.is_layer_influenced(self._usd_context.get_stage_url()):
                return

        self._update_ui()

    def _update_ui(self):
        if self._live_syncing.is_stage_in_live_session():
            print("[omni.iot.sample.panel] joining live session")
            if self._iot_prim is None:
                self._window = ui.Window("Sample IoT Data", width=350, height=390)
                self._window.frame.set_style(uiElementStyles.mainWindow)

                sessionLayer = self._stage.GetSessionLayer()
                sessionLayer.startTimeCode = 1
                sessionLayer.endTimeCode = 192
                self._iot_prim = self._stage.GetPrimAtPath("/iot")
                self._cube = LiveCube(self._stage, "/World/cube")
                self._rollers = []

                for x in range(38):
                    self._rollers.append(
                        LiveRoller(self._stage, f"/World/Geometry/SM_ConveyorBelt_A08_Roller{x+1:02d}_01")
                    )

                # this will capture when the select changes in the stage_selected_iot_prim_label
                self._stage_event_sub = self._usd_context.get_stage_event_stream().create_subscription_to_pop(
                    self._on_stage_event, name="Stage Update"
                )

                # this will capture changes to the IoT data
                self.listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_objects_changed, self._stage)

                # create an simple window with empty VStack for the IoT data
                with self._window.frame:
                    with ui.VStack():
                        with ui.HStack(height=22):
                            ui.Label("IoT Prim:", style=uiTextStyles.title, width=75)
                            self._selected_iot_prim_label = ui.Label(" ", style=uiTextStyles.title)
                        self._property_stack = ui.VStack(height=22)

                if self._iot_prim:
                    self._on_selected_prim_changed()

        else:
            print("[omni.iot.sample.panel] leaving live session")
            self._iot_prim = None
            self.listener = None
            self._stage_event_sub = None
            self._property_stack = None
            self._window = None
            self._window = ui.Window("Sample IoT Data", width=350, height=390)
            self._window.frame.set_style(uiElementStyles.mainWindow)
            with self._window.frame:
                with ui.VStack(height =50):
                    ui.Label("Please enter a live session to begin", style= uiTextStyles.title2)
