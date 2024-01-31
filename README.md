# Logiciel de contrôle et d'interface pour le scanneur 3D

3DScanner contient tout le logiciel nécessaire au fonctionnement du scanneur 3D de Hublot.



# Setup Raspberry Pi (RPi) from scratch

# 1. Flash the RPi OS

1. [Flash OS with Raspberry Pi Imager](https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up/2). For this step, you need admin privilege each time you run Raspberry Pi Imager, so maybe use your own laptop. Use the latest version of Bullseye (See screenshot for the one I used). You should check the parameters before installation, especially:
    1. Set the hostname (I used scanner3D-RD, but you can put anything you want)
    2. Set username and password. You will have to enter the password to SSH to the RPi, so remember it.
    3. Configure wirless LAN with the wifi RD (don’t forget to check hidden SSID)
    4. Enable SSH 
    
    ![Older version may not support the camera, newer version may have different networking architectures. You can try with bookworm but I have not tested it.](Setup%20Raspberry%20Pi%20(RPi)%20from%20scratch%201f80b3a442da41e68c0a6b4bdd5e0f8a/Untitled.png)
    
    Older version may not support the camera, newer version may have different networking architectures. You can try with bookworm but I have not tested it.
    
2. Insert the SD card into the RPi, connect ethernet and power.
3. Connect to RPi from a computer with SSH. The two devices must be connected to the same network (I used the desktop computer connected with ethernet, but you can do the same over the RD wifi). For that, I used Visual Studio Code with *Remote - SSH* extension, but there are other options. 
If you wish to use VS Code (which I recommend), follow the guide:
    
    [VS Code Remote SSH basics](https://www.notion.so/VS-Code-Remote-SSH-basics-a6a9117110b44238848eb22012522cfb?pvs=21)
    

# 2. Configure network for installation

Due to my situation, I had to connect to the RPi by SSH over ethernet. However, this ethernet connection could not provide internet acces to the RPi. So I had to use a wifi network and change the priority in the RPi. If your setup is different (for example, if you only use wifi), you can skip this step.

1. Open terminal
2. `sudo nano /etc/dhcpcd.conf`
3. Add these lines at the end:
    
    ```bash
    interface eth0
    static_routers=10.88.141.250
    static domain_name_servers=10.88.140.12
    request ip_address=10.88.141.53
    #metric 350
    
    interface wlan0
    request ip_address=172.23.9.208
    metric 200
    
    #interface wlan0
    #nohook wpa_supplicant
    #static ip_address=192.168.50.10/24
    #static routers=192.168.50.1
    
    # fallback to static profile on eth0
    #interface eth0
    #fallback static_eth0
    ```
    
4. Save and exit nano using *ctrl+X* then *Y*
5. Reboot the RPi (`sudo reboot`)
6. Check that it worked using: 
    1. `ifconfig` should show the two interfaces
    2. `ping google.com` should not time out

# 3. Check for updates

Open a terminal and update everthing (enter line per line)

```bash
sudo apt update
sudo apt full-upgrade
sudo apt install raspberrypi-kernel-headers
sudo reboot
```

# 4. Clone GitHub repository

[https://github.com/GuillaumeChpn/3DScanner.git](https://github.com/GuillaumeChpn/3DScanner.git)

1. Go to the GitHub repo and copy the link
    
    ![Untitled](Setup%20Raspberry%20Pi%20(RPi)%20from%20scratch%201f80b3a442da41e68c0a6b4bdd5e0f8a/Untitled%201.png)
    
2. In source control, click *Clone Repository* button, then paste the link in the dialog box
    
    ![Untitled](Setup%20Raspberry%20Pi%20(RPi)%20from%20scratch%201f80b3a442da41e68c0a6b4bdd5e0f8a/Untitled%202.png)
    
3. Accept the default location and open the location as suggested.
    
    ![Untitled](Setup%20Raspberry%20Pi%20(RPi)%20from%20scratch%201f80b3a442da41e68c0a6b4bdd5e0f8a/Untitled%203.png)
    

# 5. Create virtual environment and install dependencies

1. From the folder where you have cloned the repo, create a python virtual environment: `python3 -m venv scan_venv --system-site-packages`
2. Activate the virtual environment: `source ./scan_venv/bin/activate`
3. Install all required libraries: `pip3 install -r ./requirements.txt -vvv`. Don’t worry, it takes a lot of time, for me 1h30 approx.
4. Install NGINX: `sudo apt install nginx`
5. Install ExifTool: [Installing ExifTool](https://exiftool.org/install.html#Unix). For simplicity, you can download the .tar archive on your computer then drag and drop it to a folder of the RPi using VS Code.

# 6. Configure server and reverse proxy

**Server:** 

1. Create a new daemon dedicated to the server: `sudo nano /etc/systemd/system/3DScanner.service`
    
    ```bash
    [Unit]
    Description=Server for my Flask application
    After=network.target
    
    [Service]
    User=pi  
    Group=www-data
    WorkingDirectory=/home/pi/3DScanner
    ExecStart=/home/pi/3DScanner/scan_venv/bin/python wsgi.py
    
    [Install]
    WantedBy=multi-user.target
    ```
    
2. Change file permissions: `sudo chmod u+rwx /etc/systemd/system/3DScanner.service`
3. Reload daemons: `sudo systemctl daemon-reload`
4. Start the server: `sudo systemctl start 3DScanner.service`
5. Make the server start at boot: `sudo systemctl enable 3DScanner.service`

**Reverse proxy (NGINX):**

1. Create a new configuration file: `sudo nano /etc/nginx/sites-available/3DScanner`
    
    ```bash
    server {
        listen 80;
        server_name _;
    
        location / {
            include proxy_params;
            proxy_pass http://127.0.0.1:5000;
        }
    }
    ```
    
2. Enable the new configuration: `sudo ln -s /etc/nginx/sites-available/3DScanner /etc/nginx/sites-enabled`
3. Disable default configuration: `sudo rm /etc/nginx/sites-enabled/default`
4. Reload daemons: `sudo systemctl daemon-reload`
5. Restart NGINX: `sudo systemctl restart nginx.service`
6. Make NGINX start at boot: `sudo systemctl enable nginx.service`

# 7. Configure network for standalone access point

The goal is that the RPi creates a wireless network when booting. Be careful, a lot of tutorials do not work for RPi OS Bullseye. I followed this one: [RPi Access Point dhcpcd method](https://www.raspberryconnect.com/projects/65-raspberrypi-hotspot-accesspoints/168-raspberry-pi-hotspot-access-point-dhcpcd-method)

1. Install required software: `sudo apt install hostapd` and `sudo apt install dnsmasq`
2. Stop the daemons during configuration: `sudo systemctl stop hostapd` then `sudo systemctl stop dnsmasq`
3. Create a config file: `sudo nano /etc/hostapd/hostapd.conf`
    
    ```bash
    interface=wlan0
    driver=nl80211
    ssid=Scanner3D RD
    hw_mode=g
    channel=6
    wmm_enabled=0
    macaddr_acl=0
    auth_algs=1
    ignore_broadcast_ssid=0
    wpa=2
    wpa_passphrase=bubblot4ever
    wpa_key_mgmt=WPA-PSK
    rsn_pairwise=CCMP
    ```
    
4. Make hostapd start at boot: `sudo systemctl unmask hostapd` then `sudo systemctl enable hostapd`
5. Open config file: `sudo nano /etc/dnsmasq.conf`
Add the following content to the bottom of the file:
    
    ```bash
    #RPiHotspot config - No Intenet
    interface=wlan0
    domain-needed
    bogus-priv
    dhcp-range=192.168.50.150,192.168.50.200,255.255.255.0,12h
    ```
    
6. Edit config file: `sudo nano /etc/dhcpcd.conf`
At bottom fo file, comment the old wlan0 config (if any) and add:
    
    ```bash
    #interface wlan0
    #request ip_address=172.23.9.208
    #metric 200
    
    interface wlan0
    nohook wpa_supplicant
    static ip_address=192.168.50.10/24
    static routers=192.168.50.1
    ```
    

# 8. Test

1. Reboot the RPi: `sudo reboot`
2. The LEDs should play the startup sequence (ON continuous, then blink, then OFF) (There may be a bug and it plays twice, but I did not find that it affect any functionnality.)
3. After a few seconds, the RPi wireless network is active. Connect your device to it.
4. Connect to the application by entering the RPi IP adress in any web browser (You set it at step 7.6, it should be `192.168.50.10`).
5. Check functionnalities and scan an object.