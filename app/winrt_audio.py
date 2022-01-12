from winrt.windows.media.control import \
    GlobalSystemMediaTransportControlsSessionManager as MediaManager

async def get_media_info():
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()

    if current_session:
        info = await current_session.try_get_media_properties_async()

        # song_attr[0] != '_' ignores system attributes
        info_dict = {song_attr: info.__getattribute__(song_attr) for song_attr in dir(info) if song_attr[0] != '_'}
        # Convert WinRT vector to list
        info_dict['genres'] = list(info_dict['genres'])
        return info_dict
    print("No active media")
    return str("No active media")
