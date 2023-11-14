import os

from .nucleus_client_error import NucleusClientError
from .nucleus_server_config import nucleus_server_config
import omni.client
from pxr import Sdf


class LiveEditSession:
    """
    Class used to create a live edit session (unless already exists) on
    the Nucleus server, by writing a session toml file and
    creating a .live stage

    Session name: {org_id}_{simulation_id}_iot_session
    Root folder: .live/{usd-file-name}.live/{session-name}/root.live
    session_folder_url: {root_folder}/.live/{usd-file-name}.live
    live_session_url: {session_folder_url}/{session-name}/root.live
    toml_url: {session_folder_url}/{session-name}/__session__.toml
    """

    def __init__(self, stage_url):
        self.session_name = "iot_session"
        self.stage_url = stage_url
        self.omni_url = omni.client.break_url(self.stage_url)

        root_folder = self._make_root_folder_path()
        self.session_folder_url = self._make_url(root_folder)
        live_session_folder = f"{root_folder}/{self.session_name}.live"
        self.live_session_url = self._make_url(f"{live_session_folder}/root.live")
        self.toml_url = self._make_url(f"{live_session_folder}/__session__.toml")

    async def ensure_exists(self):
        """Either find an existing live edit session or create a new one"""
        # get the folder contains the sessions and list the available sessions
        _result, sessions = await omni.client.list_async(self.session_folder_url)

        for entry in sessions:
            session_name = os.path.splitext(entry.relative_path)[0]
            if session_name == self.session_name:
                # session exists so exit
                return self._ensure_live_layer()

        # create new session
        # first create the toml file
        self._write_session_toml()
        return self._ensure_live_layer()

    def _ensure_live_layer(self):
        # create a new root.live session file
        live_layer = Sdf.Layer.FindOrOpen(self.live_session_url)
        if not live_layer:
            live_layer = Sdf.Layer.CreateNew(self.live_session_url)
            if not live_layer:
                raise Exception(f"Could load the live layer {self.live_session_url}.")

            Sdf.PrimSpec(live_layer, "iot", Sdf.SpecifierDef, "IoT Root")
            live_layer.Save()

        return live_layer

    def _make_url(self, path):
        return omni.client.make_url(
            self.omni_url.scheme,
            self.omni_url.user,
            self.omni_url.host,
            self.omni_url.port,
            path,
        )

    def _make_root_folder_path(self):
        """
        construct the folder that would contain sessions:
            {.live}/{usd-file-name.live}/{session_name}/root.live
        """
        stage_file_name = os.path.splitext(os.path.basename(self.omni_url.path))[0]

        return f"{os.path.dirname(self.omni_url.path)}/.live/{stage_file_name}.live"

    def _write_session_toml(self):
        """
        writes the session toml to Nucleus
            OWNER_KEY = "user_name"
            STAGE_URL_KEY = "stage_url"
            MODE_KEY = "mode" (possible modes - "default" = "root_authoring",
                                "auto_authoring", "project_authoring")
            SESSION_NAME_KEY = "session_name"
        """
        session_config = nucleus_server_config(self)

        toml_string = "".join([f'{key} = "{value}"\n' for (key, value) in session_config.items()])

        result = omni.client.write_file(self.toml_url, self._toml_bytes(toml_string))

        if result != omni.client.Result.OK:
            raise NucleusClientError(
                f"Error writing live session toml file {self.toml_url}, " f"with configuration {session_config}"
            )

    @staticmethod
    def _toml_bytes(toml_string):
        return bytes(toml_string, "utf-8")
