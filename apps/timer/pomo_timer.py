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

        self.brightness = self.default_brightness

        # register start_session with state/event listener
        # based off state change of input boolean(or binary sensor)
        # to initiate the callback method
        self.state = self.State.OFF
        self.handle = self.listen_event(self.cb_start_timer, event=EVENT_NAME, event_type=EVENT_DATA_START)
        self.log("pomo_timer initialized")

    def cb_start_timer(self, event_name, event_data, kwargs):
        self.log("starting timer")
        self.original_state = []
        for light in self.lights:
            self.original_state.append(self.get_state(light, "all"))
        self.log([str(x)+"\n" for x in self.original_state])
        return
        self.log("data recv'd: {}".format(event_data))
        try:
            self._process_event_data(event_data)
        except Exception as e:
            self.log("Error while processing event data: {}".format(e))
            self.log("Using values specified in app config.")

        # init short break count
        self.cur_rep_count = 0
        self.log("time: work: {} seconds; short: {} seconds".format(self.work_time, self.short_break_time))

        # can probably call synchronously but it doesn't really matter here
        self.run_in(self.cb_run_timer, 1)

    # kwargs are necessary due to the way the function is called
    def cb_run_timer(self, kwargs):
        # Just doing work time and short breaks now
        # Can implement long breaks later
        self.log("running timer: {} out of {} reps remaining".format(self.num_short_breaks-self.cur_rep_count, self.num_short_breaks))
        if self.cur_rep_count < self.num_short_breaks:
            self.cur_rep_count += 1
            self.run_in(self.cb_start_work_time, 1)
        else:
            # Set lights back to their original state
            self.log("stopping timer")
            return

    # process any event data and replace any default values
    def _process_event_data(self, event_data):
        set_work = False
        set_short = False
        set_reps = False

        if "time" in event_data:
            time_obj = event_data["time"]
            if "work" in time_obj:
                work_arr = time_obj["work"]
                set_work = True
                h, m, s = [int(n) for n in work_arr]
                work_time_data = self._time_to_sec(h, m, s)
            if "short" in time_obj:
                short_arr = time_obj["short"]
                set_short = True
                h, m, s = [int(n) for n in short_arr]
                short_time_data = self._time_to_sec(h, m, s)
        if "cycles" in event_data:
            set_reps = True
            cycle_data = int(event_data["cycles"])

        # No need to wait for all configs since brightness is independent of time (and its last anyways)
        if "brightness" in event_data:
            self.brightness = int(event_data["brightness"])

        # Only set after data has been processed in case of exception
        if set_work: self.work_time = work_time_data
        if set_short: self.short_break_time = short_time_data
        if set_reps: self.num_short_breaks = cycle_data

    def cb_start_work_time(self, kwargs):
        # set lights as needed
        # schedule callback for short break
        self.log("begin work for {} seconds".format(self.work_time))
        for entity in self.lights:
            self.turn_on(entity, brightness=self.brightness, rgb_color=self.default_work_color)
        self.state = self.State.WORK
        self.handle = self.run_in(self.cb_start_short_break, self.work_time)

    def cb_start_short_break(self, kwargs):
        # set lights as needed
        # schedule callback for session runner
        self.log("begin short break for {} seconds".format(self.short_break_time))
        for entity in self.lights:
            self.turn_on(entity, brightness=self.brightness, rgb_color=self.default_short_break_color)
        self.state = self.State.SHORT_BREAK
        self.handle = self.run_in(self.cb_run_timer, self.short_break_time)

    def _time_to_sec(self, h, m, s):
        return int(s) + 60 * int(m) + 3600 * int(h)

    class State(Enum):
        OFF = 0,
        WORK = 1,
        SHORT_BREAK = 2,
        LONG_BREAK = 3,


