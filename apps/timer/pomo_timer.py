import appdaemon.plugins.hass.hassapi as hass
from enum import Enum

EVENT_NAME = "APP_TIMER"
EVENT_DATA_START = "START"
'''
"event_type": "APP_TIMER",
"data": {
    "event_type": "START",
    "time": {
        "work": [0,10,0],  # [h,m,s]
        "short": [0,2,0]  # [h,m,s]
    }
}
'''
# Declare Class
class PomoTimer(hass.Hass):
    # Don't know which schema is better
    default_work_light_light_config = {
        "brightness": 50,
        "rgb_color": (255,205,75)  # yellow-orange
    }

    default_brightness = 50
    default_work_color = (255,205,75)
    default_short_break_color = (100,255,100)

    def initialize(self):
        # read params from yaml config
        self.work_time = self.args["work_time"]
        self.short_break_time = self.args["short_break_time"]
        self.num_short_breaks = self.args["num_short_breaks"]
        self.lights = self.args["lights"]
        # init short break count
        self.cur_rep_count = 0

        # register start_session with state/event listener
        # based off state change of input boolean(or binary sensor)
        # to initiate the callback method
        self.state = self.State.OFF
        self.handle = self.listen_event(self.cb_start_timer, event=EVENT_NAME, event_type=EVENT_DATA_START)

    def cb_start_timer(self, event_name, event_data, kwargs):
        # self.original_state = []
        # for light in self.lights:
        #     self.original_state.append(self.get_state(light))
        try:
            self._process_event_data(event_data)
        except Exception as e:
            self.log("Error while processing event data. Using values specified in app config.")

        # can probably call synchronously but it doesn't really matter here
        self.run_in(self.cb_start_work_time, 1)

    # kwargs are necessary due to the way the function is called
    def cb_run_timer(self, kwargs):
        # Just doing work time and short breaks now
        # Can implement long breaks later
        if self.cur_rep_count == self.num_short_breaks:
            self.run_in(self.cb_start_work_time, 1)
            self.cur_rep_count += 1
        else:
            # Set lights back to their original state
            return

    # process any event data and replace any default values
    def _process_event_data(self, event_data):
        set_work = False
        set_short = False
        time_obj = event_data["time"]
        if time_obj:
            work_obj = time_obj["work"]
            short_obj = time_obj["short"]
            if work_obj:
                set_work = True
                h, m, s = work_obj
                work_time_data = self._time_to_sec(h, m, s)
            if short_obj:
                set_short = True
                h, m, s = short_obj
                short_time_data = self._time_to_sec(h, m, s)

        # Only set after data has been processed in case of exception
        if set_work: self.work_time = work_time_data
        if set_short: self.short_break_time = short_time_data

    def cb_start_work_time(self, kwargs):
        # set lights as needed
        # schedule callback for short break
        for entity in self.lights:
            self.turn_on(entity, brightness=self.default_brightness, rgb_color=self.default_work_color)
        self.state = self.State.WORK
        self.handle = self.run_in(self.cb_start_short_break, self.work_time)

    def cb_start_short_break(self, kwargs):
        # set lights as needed
        # schedule callback for session runner
        for entity in self.lights:
            self.turn_on(entity, brightness=self.default_brightness, rgb_color=self.default_short_break_color)
        self.state = self.State.SHORT_BREAK
        self.handle = self.run_in(self.cb_run_timer, self.short_break_time)

    def _time_to_sec(self, h, m, s):
        return s + 60 * m + 3600 * h

    class State(Enum):
        OFF = 0,
        WORK = 1,
        SHORT_BREAK = 2,
        LONG_BREAK = 3,


