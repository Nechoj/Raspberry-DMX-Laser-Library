#! /bin/sh
### BEGIN INIT INFO
# Provides:          laser_daemon.sh
# Required-Start:    $remote_fs $syslog mysql
# Required-Stop:     $remote_fs $syslog mysql
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts and stops the laser_daemon.py
# Description:       starts and stops the laser_daemon.py
### END INIT INFO

# Author: Jochen Hertle

# Activate the python virtual environment
    . /usr/venv/bin/activate

case "$1" in
  start)
    echo "Starting server"
    # Start the daemon
    #sudo -u pi /home/pi/www/scripts/laser_daemon.py start
    sudo /home/pi/www/scripts/laser_daemon.py > /dev/null 2> /dev/null &
    ;;
  stop)
    echo "Stopping server"
    # Stop the daemon using the source file written by laser_daemon.py
    sudo /tmp/laser_daemon_stop
    deactivate
    ;;
  restart)
    echo "Restarting server"
    #sudo -u pi /home/pi/www/scripts/laser_daemon.py restart
    ;;
  *)
    # Refuse to do other stuff
    echo "Usage: /etc/init.d/laser_daemon.sh {start|stop|restart}"
    exit 1
    ;;
esac

exit 0