# TODO: Add more comments
import obspython as obs

last_switched_scene=None
# Hack to fix studio bug and crash when having event callback
def set_current_scene(scene):
	obs.obs_frontend_remove_event_callback(on_event)
	if obs.obs_frontend_preview_program_mode_active():
		obs.obs_frontend_set_current_preview_scene(scene)
	else:
		obs.obs_frontend_set_current_scene(scene)
	obs.obs_frontend_add_event_callback(on_event)

# Creates key press callback
def _handle_key(toggle_scene, toggle_scene_id):
	def _on_press(pressed):
		if pressed: return
		global last_switched_scene

		scene = obs.obs_frontend_get_current_preview_scene()
		scene_id = obs.obs_source_get_name(scene)

		if scene_id == toggle_scene_id:
			obs.obs_source_release(scene)
			if last_switched_scene: set_current_scene(last_switched_scene)
		else:
			if last_switched_scene: obs.obs_source_release(last_switched_scene)
			last_switched_scene = scene
			set_current_scene(toggle_scene)

	return _on_press


loaded = False

def on_event(event):
	if event == obs.OBS_FRONTEND_EVENT_FINISHED_LOADING or event == obs.OBS_FRONTEND_EVENT_SCENE_LIST_CHANGED:
		global loaded
		if not loaded:
			loaded = True
			_register_hot_keys(settngs)



hot_keys = []
scenes = []

def _register_hot_keys(settings):
	global scenes

	scenes = obs.obs_frontend_get_scenes()
	for i in range(len(scenes)):
		scene = scenes[i]
		scene_id = obs.obs_source_get_name(scene)
		callback = _handle_key(scene, scene_id)
		name = 'toggle.' + scene_id
		hot_key_id = obs.obs_hotkey_register_frontend(name, "Toggle '" + scene_id + "'", callback)
		save_array = obs.obs_data_get_array(settings, name)
		obs.obs_hotkey_load(hot_key_id, save_array)
		obs.obs_data_array_release(save_array)
		hot_keys.append({'callback': callback, 'scene_id': hot_key_id, 'name': name})

settngs = None

def script_load(settings):
	global settngs
	settngs = settings
	print('toggle script loaded')
	scenes = obs.obs_frontend_get_scenes()
	if len(scenes) > 0:
		global loaded
		loaded = True
		_register_hot_keys(settings)
	obs.source_list_release(scenes)
	obs.obs_frontend_add_event_callback(on_event)

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