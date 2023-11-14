import omni.client

def nucleus_server_config(live_edit_session):
    _, server_info = omni.client.get_server_info(live_edit_session.stage_url)

    return {
        "user_name": server_info.username,
        "stage_url": live_edit_session.stage_url,
        "mode": "default",
        "name": live_edit_session.session_name,
        "version": "1.0",
    }
