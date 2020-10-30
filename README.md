# shower-heating-temp-domoticz-plugin
Domoticz (https://www.domoticz.com/) Plugin(https://www.domoticz.com/wiki/Developing_a_Python_plugin#Devices)  for enabling thermostat setting override 

## Functionality
First attempt to describe the functionality:
This plugin creates 1 virtual device, a switch
When toggling the switch from OFF to ON, the following things happen:
  1. The Main Thermostat set-point is increased with 2 degrees (configurable)
  2. The Bath-Room Thermostat set-point is increased with 8 degrees (configurable)
  3. The timer starts a countdown (30 minutes)
  4. When the timer has elapsed, the Thermostats are restored to the stored setpoints (prior to increasing)
     1. Switch is switched back to OFF automatically
  5. System idles and awaits user interaction (Switch pressing)

## WishList:
 - smarter and more efficient temperature behaviour; 
   - e.g.: if certain temperature in bath-room is maintained, stop the system (or pause) and keep an eye on it
   - better tuning of the current temperature and set-point to determine more efficient Ovverride setpoint
 - Better monitoring on actual temperatures, set-points (and outside themperature)
 - include Outside temperature

# Issues:
- What if plugin is enabled twice, not restored? investigate!!