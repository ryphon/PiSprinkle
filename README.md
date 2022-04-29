# PiSprinkle
Raspberry Pi based irrigation control app

This project is in its infancy, much work to do!

# Current features
  - Add/configure zones with a name and what GPIO pin controls it
  - Manually turn on/off zones in app
  - Schedule irrigation by zone, weekday, and time
  - Docker and Kubernetes support
  - Kustomize preferred, Helm chart available
  - Persistent volume capabilities

# Work to do
  - There are some bugs to do with resource management (GPIO pins, apscheduler) that need fixing
  - Build socket.io connection for realtime updates to zone status from server-side
  - Move GPIO pin configuring to run_zone function and manual control rather than app-wide
  - User accounts / login authentication
  - Allow for multi-process deployment options - function currently depends on there only being ONE app instance running
  - Installation script
  - Documentation of how to build circuit
  - Make it pretty!
