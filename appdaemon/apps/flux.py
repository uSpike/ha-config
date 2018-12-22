
import appdaemon.plugins.hass.hassapi as hass

wall_scene_map = {
    'up_1': dict(scene_id=2, scene_data=0),
    'up_2': dict(scene_id=2, scene_data=3),
    'up_3': dict(scene_id=2, scene_data=4),
    'up_4': dict(scene_id=2, scene_data=5),
    'down_1': dict(scene_id=1, scene_data=0),
    'down_2': dict(scene_id=1, scene_data=3),
    'down_3': dict(scene_id=1, scene_data=4),
    'down_4': dict(scene_id=1, scene_data=5),
}

button_scene_map = {
    'moon_tap': dict(scene_id=1, scene_data=0),
    'moon_release': dict(scene_id=1, scene_data=1),
    'moon_hold': dict(scene_id=1, scene_data=2),
    'people_tap': dict(scene_id=2, scene_data=0),
    'people_release': dict(scene_id=2, scene_data=1),
    'people_hold': dict(scene_id=2, scene_data=2),
    'circle_tap': dict(scene_id=3, scene_data=0),
    'circle_release': dict(scene_id=3, scene_data=1),
    'circle_hold': dict(scene_id=3, scene_data=2),
    'circle_line_tap': dict(scene_id=4, scene_data=0),
    'circle_line_release': dict(scene_id=4, scene_data=1),
    'circle_line_hold': dict(scene_id=4, scene_data=2),
}


class Lights(hass.Hass):
    def _all_on(self):
        for entity_id in self.all_entity_id:
            self.turn_on(entity_id)

    def _all_off(self):
        for entity_id in self.all_entity_id:
            self.turn_off(entity_id)

    def _scene_bright(self):
        self.turn_off(self.flux_entity_id)
        self.turn_on(
            self.light_entity_id,
            brightness_pct=self.args['bright']['brightness'],
            kelvin=self.args['bright']['kelvin'],
            transition=1,
        )

    def _scene_dim(self):
        self.turn_off(self.flux_entity_id)
        self.turn_on(
            self.light_entity_id,
            brightness_pct=self.args['dim']['brightness'],
            kelvin=self.args['dim']['kelvin'],
            transition=1,
        )

    def wall_scene_activated(self, event, data, kwargs):
        is_scene = lambda name: wall_scene_map[name].items() <= data.items()
        if is_scene('up_1'):
            state = self.get_state(self.light_entity_id)
            update_service = 'switch/{}_update'.format(self.args['flux_entity'])
            cb = lambda *args, **kwargs: self.call_service(update_service)
            if state == 'on':
                cb()
            else:
                self.turn_on(self.light_entity_id, brightness_pct=50, kelvin=2500)
                self.turn_on(self.flux_entity_id)
                self.run_in(cb, 1)
        if is_scene('down_1'):
            self.turn_off(self.light_entity_id, transition=1)
            self.turn_off(self.flux_entity_id)
        if is_scene('up_2'):
            self._scene_bright()
        if is_scene('down_2'):
            self._scene_dim()
    
    def button_scene_activated(self, event, data, kwargs):
        is_scene = lambda name: button_scene_map[name].items() <= data.items()
        if is_scene('circle_tap'):
            self.toggle(self.light_entity_id)
        if is_scene('circle_hold'):
            self._all_on()
        if is_scene('moon_tap'):
            self._all_off()
        if is_scene('circle_line_tap'):
            self._scene_bright()
        if is_scene('circle_line_hold'):
            self._scene_dim()
        
    def initialize(self):
        self.light_entity_id = 'light.{}'.format(self.args['light_entity'])
        self.flux_entity_id = 'switch.{}'.format(self.args['flux_entity'])
        self.all_entity_id = self.args['all_entity']

        for switch in self.args['zwave_switch']:
            self.listen_event(
                self.wall_scene_activated,
                'zwave.scene_activated',
                entity_id=switch,
            )
        for button in self.args['zwave_button']:
            self.listen_event(
                self.button_scene_activated,
                'zwave.scene_activated',
                entity_id=button,
            )
