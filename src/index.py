import obspython as obs

last_switched_scene=None
last_switched_scene_id=None

last_scene=None
last_scene_id=None

def set_current_scene(scene):
	obs.obs_frontend_remove_event_callback(on_event)
	obs.obs_frontend_set_current_scene(scene)
	obs.obs_frontend_add_event_callback(on_event)

def _handle_key(toggle_scene, toggle_scene_id):
	def _on_press(pressed):
		if pressed: return

		global last_switched_scene
		global last_switched_scene_id

		global last_scene
		global last_scene_id

		scene = obs.obs_frontend_get_current_scene()
		scene_id = obs.obs_source_get_name(scene)

		if scene_id == toggle_scene_id and last_switched_scene != None:
			set_current_scene(last_switched_scene)
		else:
			set_current_scene(obs.obs_get_source_by_name(toggle_scene_id))

		obs.obs_source_release(scene)
		
	return _on_press

def on_event(event):
	if event == obs.OBS_FRONTEND_EVENT_SCENE_CHANGED:
		global last_switched_scene
		global last_switched_scene_id

		global last_scene
		global last_scene_id

		scene = obs.obs_frontend_get_current_scene()
		scene_id = obs.obs_source_get_name(scene)
		if scene_id != last_scene_id:
			if last_switched_scene != None:
				obs.obs_source_release(last_switched_scene)

			last_switched_scene = last_scene
			last_switched_scene_id = last_scene_id

			last_scene = scene
			last_scene_id = scene_id
		else:
			obs.obs_source_release(scene)

hot_keys = []
scenes = []

def _register_hot_keys(settings):
	global scenes

	scenes = obs.obs_frontend_get_scenes()
	print(scenes)
	for scene in scenes:
		scene_id = obs.obs_source_get_name(scene)
		callback = _handle_key(scene, scene_id)
		proxy_callback = lambda pressed: callback(pressed)
		name = 'toggle.' + scene_id
		hot_key_id = obs.obs_hotkey_register_frontend(name, "Toggle '" + scene_id + "'", proxy_callback)
		save_array = obs.obs_data_get_array(settings, name)
		obs.obs_hotkey_load(hot_key_id, save_array)
		obs.obs_data_array_release(save_array)
		hot_keys.append({'callback': proxy_callback, 'scene_id': hot_key_id, 'name': name})

def script_load(settings):
	print('toggle script loaded')
	obs.obs_frontend_add_event_callback(on_event)
	_register_hot_keys(settings)

def script_unload():
	obs.obs_frontend_remove_event_callback(on_event)
	for hot_key in hot_keys:
		obs.obs_hotkey_unregister(hot_key['callback'])

def script_save(settings):
	for hot_key in hot_keys:
		save_key = obs.obs_hotkey_save(hot_key['scene_id'])
		obs.obs_data_set_array(settings, hot_key['name'], save_key)

def script_description():
	return "Toggle a certain scene"