# AppDaemon API Reference
Reference guide for useful AppDaemon APIs for use with HomeAssistant

## Callback Triggers
### Quick Reference
All time based callback registrars can use:

`
info_timer(self, handle) -> (time, interval, kwargs, or None)
`

or 

`
cancel_timer(self, handle)
`

to manage the callback asynchronously 

`run_in(self, callback, delay, **kwargs)`
* Run a callback after time (_in sec_) has elapsed.

`run_once(self, callback, start, **kwargs)`
* Run a callback a single time.

`run_at(self, callback, start, **kwargs)`
* Run a callback at a specified start time.

`run_daily(self, callback, start, **kwargs)`
* Run a callback at the same time every day.
* `run_hourly()`
* `run_minutely()`

`run_every(self, callback, start, interval, **kwargs)`
* Run a callback with a configurable delay starting at a specific time.

`run_at_sunset(self, callback, **kwargs)`
&nbsp;
`run_at_sunrise(self, callback, **kwargs)`
* Yup

`listen_state(self, callback, entity=None, **kwargs)`
* Registers a callback to react to state changes
* `info_listen_state(self, handle)`
* `cancel_listen_state(self, handle)`

`run_sequence(self, sequence, **kwargs)`
* Run an AppDaemon Sequence, which are defined in a valid apps.yaml file or inline, and are sequences of service calls.
* `cancel_sequence(self, handle)`

`listen_event(self, callback, event=None, **kwargs)`
* Listens for a specific event on the Hass event bus
* `event=None` will listen to all events
* `info_listen_event(self, handle)`
* `cancel_listen_event(self, handle)`

` listen_log(self, callback, level='INFO', **kwargs)`



# misc notes

state/add_entity(/remove_entity)

### Delay and Timers: run_in

> `run_in(self, callback, delay, **kwargs)`

Runs the callback in a defined number of seconds.

This is used to add a delay. This callback should always be used instead of time.sleep() (unless manually creating threads).

#### Parameters:	

* **`callback`** – Method to be invoked after the speficied delay
* **`delay`** (int) – Delay, in seconds before the callback is invoked.
* **`**kwargs`** (optional) – Zero or more keyword arguments.
  * **`random_start`** (int) – Start of range of the random time.
  * **`random_end`** (int) – End of range of the random time.
  * **`pin`** (bool) – If True, the callback will be pinned to a particular thread.
  * **`pin_thread`** (int) – Specify which thread from the worker pool the callback will be run by (0 - number of threads-1).
  * **`**kwargs`** – Arbitrary keyword parameters to be provided to the callback function when it is invoked.

#### Returns:	
* A handle that can be used to cancel the timer.

#### Handle Methods

##### cancel_timer

> `cancel_timer(self, handle)`

Cancels a previously created timer.

Parameters:	
* **`handle`** – A handle value returned from the original call to create the timer.

Returns: None.

##### info_timer

> `info_timer(self, handle)`

Gets information on a scheduler event from its handle.

Parameters:	
* **`handle`** – The handle returned when the scheduler call was made.
Returns:
* **`time`** - datetime object representing the next time the callback will be fired
* **`interval`** - repeat interval if applicable, 0 otherwise.
* **`kwargs`** - the values supplied when the callback was initially created.
* **`or None`** - if handle is invalid or timer no longer exists.

## State
#### get_state
 
> `get_state(self, entity_id=None, attribute=None, default=None, copy=True, **kwargs)` 

Used to get the state(s) or attributes of an entity

Parameters:
* **`entity_id`** (str, optional) – 
This is the name of an entity or device type. 
  * _If a domain is provided (eg. light) then `get_state` will return a dictionary of all entities_
* **`attribute`** (str, optional) – 
Name of an attribute within the entity state object. 
  * _`attribute="all"`_ will return the entire state dict for the entity 
* **`default*`** (any, optional) –  
Default return value (Default: None).
* **`copy*`** (bool, optional) – 
Deep copy state object. Slight preformance gain, but don't use unless absolutely required 
(_Note: The state object is AppDeamon's representation of the state, so modifying it will not affect Hass_)
* **`**kwargs`** (optional) – 
  * **`namespace`** (str, optional) – Namespace to use for the call. See **namespaces**

Returns:
* (no args) - The entire state of Hass
* (entity_id) - state of entity ("on", "off")
* (entity_id, attribute) - specified attribute of entity
* (entity_id, all) - The entire state of entity

Examples

> Get the state of the entire system.
>
>  `state = self.get_state()`

> Get the state of all switches in the system.
>   
> `state = self.get_state("switch")`

> Get the state attribute of light.office_1.
>   
> `state = self.get_state("light.office_1")`

> Get the brightness attribute of light.office_1.
>   
> `state = self.get_state("light.office_1", attribute="brightness")`

> Get the entire state of light.office_1.
>   
> `state = self.get_state("light.office_1", attribute="all")`


## Time
#### Sun
> `sun_up(self)`
>
> `sun_down(self)`

Returns self-explanatory boolean

> `sunrise(self, aware=False)` 
>
> `sunset(self, aware=False)`

Returns datetime object for when sunrise/sunset will happen
* **aware** - If the datetime object will be _aware_ of the timezone or not