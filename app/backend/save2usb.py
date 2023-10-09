import subprocess


def get_usb_drives() -> list:
    listdrives = subprocess.Popen('mount', shell=True, stdout=subprocess.PIPE)
    listdrivesout, _ = listdrives.communicate()
    listdrivesout = str(listdrivesout)[2:]
    listdrivesout = listdrivesout.split('\\n')
    listdrivesout = listdrivesout[:-1]

    usb_drives = []
    for line in listdrivesout:
        if (line.find('/sys') == -1 and 
            line.find('/run') == -1 and 
            line.find('on /dev') == -1 and 
            line.find('/boot') == -1 and 
            line.find('/proc') == -1 and
            line.find('on / type')) == -1:
            path = line.split()[2]
            device_name = path.split('/')[-1]
            
            usb_drives.append(device_name)
    return usb_drives


if __name__ == '__main__':
    usb_drives = get_usb_drives()
    for l in usb_drives:
        print(l)


