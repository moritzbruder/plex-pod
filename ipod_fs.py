import os
import re

class IpodDevice:

    def __init__(self, filename, main_drive):
        self.filename = filename
        self.main_drive = main_drive


class IpodManager:

    #'/dev/plex_pod_mountpoint'
    def __init__(self, mountpoint):
        self.mountpoint = mountpoint

    def get_ipods(self):
        ipods_result = []
        fdisk_devices = re.split('\n\nDisk ', os.popen('fdisk -l').read())

        def parse_device_params(params):
            lines = params.strip().split('\n')
            lines.pop(0)
            result = {}
            for line in lines:
                split = line.split(': ', 1)
                result[split[0].strip()] = split[1].strip()
            return result

        def parse_device_devices(devices):
            if not devices:
                return devices
            lines = devices.strip().split('\n')
            lines.pop(0)
            devs_list = []
            for line in lines:
                split = line.strip().split(' ', 1)
                devs_list.append({
                    'name': split[0].strip(),
                    'props': split[1].strip()
                })
            return devs_list

        def parse_device(dev):
            filename = dev.split(': ')[0]
            split_data = dev.split('\nDevice')
            params_str = split_data[0]
            devices_str = split_data[1] if len(split_data) > 1 else None

            device = {}

            device['filename'] = filename
            device['params'] = parse_device_params(params_str)
            device['devices'] = parse_device_devices(devices_str)

            return device

        parsed_devices = []

        for device in fdisk_devices:
            unprefixed = device[device.startswith('Disk /') and len('Disk '):]
            parsed_devices.append(parse_device(unprefixed))

        ipods = [device for device in parsed_devices if device['params'].get('Disk model') == 'iPod']

        for ipod in ipods:
            devs = ipod['devices']
            main_part = next((part for part in devs if 'fat32' in part['props'].lower()), None)
            ipods_result.append(IpodDevice(ipod['filename'], main_part))

        return ipods_result

    def mount_ipod(self, ipod):
        if not isinstance(ipod, IpodDevice):
            raise ValueError('value passed for parameter ipod is not an instance of IpodDevice')
        os.system('mkdir -p ' + self.mountpoint)
        os.system('mount -t vfat ' + ipod.main_drive + ' ' + self.mountpoint)
        print('mounted ' + ipod.main_drive + ' at ' + self.mountpoint)

    def unmount_ipod(self):
        os.system('umount ' + self.mountpoint)
        print('unmounted ipod')
