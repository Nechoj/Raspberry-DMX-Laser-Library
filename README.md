#Laser Library

Rasberry Pi and DMX controlled Laser based Library Management System


This is an experimental project with the goal, to manage my (rather large) home library. The first application realised is to use a web interface to control a movable laser that points to the requested book (or DVD or CD).

With this software, you can also control any professional DMX lighting equipment via a web page hosted on a Raspberry Pi. (DMX specification: see http://en.wikipedia.org/wiki/DMX512)

##Hardware

* Raspberry Pi mod. B
* Power supply for Raspberry Pi (5V, 1.2A)
* EDIMAX EW-7811UN Wireless USB Adapter
* USB DMX Interface: ENTTEC DMX USB Pro
* adapter cable XLR 5-pin male to XLR 3-pin female (see e.g. http://www.thomann.de/de/pro_snake_tpa_1003_fm5.htm)
* Laser head: Stairville DJ Lase Performance 150 RGY (see e.g. http://www.thomann.de/de/stairville_dj_lase_performance_150_rgy.htm)

The Laser head is a low cost one (~ 130 Euro) used in small discos. Most important, the laser beam can be controlled in x and y direction, and that is what is needed. Disadvantages of this product are a noisy fan and narrow angle for the beam (approx. 30 degrees). I cannot fully cover my library shelves with one laser head, but the DMX bus would allow to connect as many devices as I would need. If you want to use other laser devices, please check beforehand whether there are DMX channels for moving the laser beam in x and y direction.

The ENTTEC DMX USB Pro interface costs about 170 Euro. There is a cheaper one called ENTTEC Open DMX USB interface (about 60 Euro). I have written a Python driver for that modell as well (see /scripts/DmxFtdi.py). The disadvantage of that modell is, that the software has to control the timing on the DMX bus. Therefore, when clicking a button on the web interface, the web page freezes until all re-transmissions of the DMX messages is finished. Say, you want to point with the laser for about 5 sec, the page freezes for 5 sec. In contrast, the DMX Pro device controls the timing of the DMX bus, and the web page just sends one short command and is available immediately afterwards. Therefore, I currently use the DMX Pro device (Python driver: scripts/DmxPro.py).

(BTW: If you want to use the  ENTTEC Open DMX USB interface together with the Raspberry Pi my advise is to not try installing the Linux driver 'dmx_usb.ko' supplied by ENTTEC, see http://www.erwinrol.com/open-dmx-usb-linux-driver/. This is a nightmare and did cost me 2 days. Instead, just plug in the device and the Linux kernel will automatically assign the standard ftdi_sio driver. And my Python script DmxFtdi.py works with this standard kernel driver.)

Remark: The power supply of 5V / 1.2A is good enough to power the DMX USB interfaces via the USB, so no powered USB hub is needed.

##Software on Raspberry Pi

* Raspbian Linux , kernel version 3.10.25+ (downloaded from the official raspberrypi.org site on February 2014)
* LAMP stack
* Python with extension python-serial (and python-ftdi if you want to use the DmxFtdi.py driver, see above)

Installing the LAMP stack (well, Linux seems to be installed already ;-)):

    > sudo apt-cache update
    > sudo apt-get install apache2 php5 php5-mysql mysql-server

Installing the Python extension (python-ftdi needed only for the ENTTEC Open DMX USB device):

    > sudo apt-get install python-seriel (python-ftdi)

##System configuration

I use directory /home/pi/www/ as a root to the apache web server. This root is set in file /etc/apache2/sites-available/default. Further directories needed are /home/pi/www/scripts, /home/pi/www/modules and /home/pi/www/css.

For security reasons, the scripts directory should not be accessible for all users. Therefore, the apache configuration file gets this entry:

    <Directory /home/pi/www/scripts/>
        Order allow,deny
        deny from all
    </Directory>

The Edimax WLAN device needs some configuration as well: The driver configuration file /etc/modprobe.d/8192cu.conf is created using e.g. 

    sudo nano /etc/modprobe.d/8192cu.conf
    
and the following line should be in this file:

    options 8192cu rtw_power_mgnt=0 rtw_enusbss=0

Next, the file /etc/network/interfaces needs editing. I wanted a static IP address for the Rasberry and therefore added this section:

    auto wlan0
    allow-hotplug wlan0
    iface wlan0 inet static
    address 192.168.178.4
    gateway 192.168.178.1
    wpa-ap-scan 1
    wpa-scan-ssid 1
    wpa-ssid "Repeater2"
    wpa-psk "<your WPA key>"

The address and gateway depends on your home network. Make sure that this address is outside the range of the dynamic DHCP addresses of the gateway/router.

Once the Raspberry is hooked onto the wireless network, you can connect from your PC via ssh to the Raspberry instead of having a monitor and keyboard connected to the Raspberry.

Files (*.html, *.py etc.) are transferred via sftp directly into the www root directory /home/pi/www/.

##Python scripts controlling the laser head

There are two Python scripts controlling the laser head: First script (scripts/laser_xy.py) directs the laser beam to a certain position. The second scripts turns the laser off (scripts/laser_stop.py). Both scripts import the Python DMX driver script DmxPro.py. The scripts can be used directly on the shell command line of the Raspberry Pi as follows

    > cd /home/pi/www/scripts
    > python laser_xy.py -x nx -y ny (nx, ny: allowed numbers 0...127 for my laser head)
    > python laser_stop.py

These scripts will need editing when working with a different laser head product. See the manual of the laser head which DMX channel controls which function.

##mysql database

For accessing the database, the web application uses the 'web_user' user. This user needs to be created in the database first. On the mysgl command line type in:

    mysql> CREATE USER ‘web_user’@’localhost’ IDENTIFIED BY ‘dbwebuserpwd’;

Next, create a database called 'laser' and grant the rights to user web_user:

    mysql> CREATE DATABASE laser;
    mysgl> GRANT ALL ON laser.* TO 'web_user'@'localhost';

Two tables in the database are needed: table books and table parameters. These are created on the mysql command line as follows:

    mysql> USE laser;
    mysql> CREATE TABLE parameters (name CHAR(20), value CHAR(20), datatype CHAR(20));
    mysql> CREATE TABLE books (bookID INT AUTO_INCREMENT UNIQUE KEY, title CHAR(255), author CHAR(255), row INT, position INT);
    

Now the database is prepared.

##Web pages

The web pages are build using html, php and css. The Python scripts are called inside the php functions using the exec() command.

There are 3 pages. Main page is index.php which is the interface for the ordinary user. You can select a book and press the 'find' button. The laser points to that book. The 'stop' button stops the laser. That's all.

The page 'parameters.php' is used for system configuration. When you install the laser head opposite to the book shelf, it can cover a certain range of books. This range needs configuration. Open the parameters.php page in your web browser and create the following parameters:

(Remark: check out the value for the y- and x-coordinates using the Python script laser_xy.py on the Raspberry command line)

    name: y_row_1
    value: <laser y-coordinate for topmost row of books>
    datatype: integer

    name: y_row_2
    value: <laser y-coordinate for second row of books>
    datatype: integer

and so on, depending on how many rows of books you have.

Then create the following parameters:

    name: x_left
    value: <laser x-coordinate for the mostleft position of the laser>
    datatype: integer

    name: x_left_dist
    value: <distance of the mostleft position of the laser to the left border of the bookshelf, in cm>
    datatype: integer

    name: x_right
    value: <laser x-coordinate for the mostright position of the laser>
    datatype: integer

    name: x_right_dist
    value: <distance of the mostright position of the laser to the left border of the bookshelf, in cm>
    datatype: integer

On page books.php, the books are inserted into the database. You need to give the row number and the distance of the book from the left border of the shelf (in cm).

Have fun!

Jochen
