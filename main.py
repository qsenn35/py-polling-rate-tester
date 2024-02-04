#!/usr/bin/python
import sys
import signal
import time
import usb.core
import usb.util
import pandas

# logitech mini optical
# vid = 0x046d
# pid = 0xc016

# razer viper v2 pro
# vid = 0x1532
# pid = 0x00b3

# razer viper mini signature edition
#vid = 0x1532
#pid = 0x009f

# hyperx pulsefire haste
# vid = 0x03f0
# pid = 0x0f8f

option = sys.argv[1]
name = None
vid = None
pid = None

dev = None
interface = None

mice_df = pandas.read_csv("./mice.csv")

# source: https://stackoverflow.com/a/69715287
def hexify(n):
    nbits = 16
    '0x{:0{}X}'.format(n & ((1 << nbits)-1), int((nbits+3)/4))

def add_mouse():
    mice_df.loc[len(mice_df)] = [name, vid, pid]
    mice_df.index = mice_df.index + 1 
    mice_df.to_csv('mice.csv', header=True)

    print("Added mouse to ./mouse.csv!")
    print("Consider opening a pull request to update to our Github Repo: https://github.com/qsenn35/py-polling-rate-tester")

def check_for_mouse(hex_vid, hex_pid):
    found = True

    if vid not in mice_df.values:
        found = False
        print("Your Vendor Id was not found in ./mice.csv...");
    elif pid not in mice_df.values:
        found = False
        print("Your Product Id was not found in ./mice.csv...");
    
    if not found:
        print("Adding your mouse information now!")
        add_mouse()

def on_force_close():
    # release the device
    usb.util.release_interface(dev, interface)
    # reattach the device to the OS kernel
    dev.attach_kernel_driver(interface)

def main():
    global name
    global vid
    global pid
    global dev
    global interface

    if option == "list":
        for device in usb.core.find(find_all=True):
            print(device)
        return 0

    name = sys.argv[2]
    vid  = sys.argv[3]
    pid = sys.argv[4]

    hex_vid = hexify(int(vid, 16))
    hex_pid = hexify(int(pid, 16))

    print("Finding Mouse USB Device: Vendor ID:", hex_vid, "Product ID:", hex_pid)
    # decimal vendor and product values
    dev = usb.core.find(idVendor=0x1532, idProduct=0x009f)

    if not dev:
        print("Mouse USB not found. :(")
        return -1

   # check if we have the mouse info in mice.csv, if not add it and suggest to do a github PR
    check_for_mouse(hex_vid, hex_pid)

    print("\nTest Directions: Draw small circles with your mouse quickly. The test lasts 5 seconds.")
    while True:
        user_input = input("Press any key to begin the test...")
        if len(user_input) or user_input == "":
            break

    # first endpoint
    interface = 0
    endpoint = dev[0][(0,0)][0]
    # if the OS kernel already claimed the device, which is most likely true
    # thanks to http://stackoverflow.com/questions/8218683/pyusb-cannot-set-configuration
    if dev.is_kernel_driver_active(interface) is True:
        # tell the kernel to detach
        print("Detatching mouse from Kernel Driver. It will not be usable until after this program ends.")
        dev.detach_kernel_driver(interface)
        # claim the device
        print("Claiming Mouse USB Device...")
        usb.util.claim_interface(dev, interface)

    collected = 0
    total_collected = 0
    polling_rate = 0
    polling_rates = []
    total_polling_rate = 0
    polling_rate_avg = 0
    max_polling_rate = 0
    low_polling_rate = 0
    it1 = time.time()
    it2 = time.time()
    tt1 = time.time()
    tt2 = time.time()

    print("Testing Polling Rate...")
    while True:
        it2 = time.time()
        ips_dt = int(it2 - it1) * 1000
        tt2 = time.time()
        tt_dt = int(tt2 - tt1) * 1000

        if (tt_dt != 0 and tt_dt >= 5000):
            break

        if (ips_dt != 0 and ips_dt % 1000 == 0):
            polling_rate = collected
            polling_rates.append(polling_rate)
            total_polling_rate += polling_rate
            polling_rate_avg = total_polling_rate / len(polling_rates)
            it1 = it2
            collected = 0

            if polling_rate > max_polling_rate:
                max_polling_rate = polling_rate
            elif low_polling_rate == 0 or polling_rate < low_polling_rate:
                low_polling_rate = polling_rate

        try:
            data = dev.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)
            #print(data)
            collected += 1
            total_collected += 1
        except usb.core.USBError as e:
            data = None
            print(e)
            if e.args == ('Operation timed out',):
                continue

    print("\nFinal Results:")
    print(f"Polling Rate: {polling_rate}hz")
    print(f"Average Polling Rate: {int(polling_rate_avg)}hz")
    print(f"Max Polling Rate: {max_polling_rate}hz")
    print(f"Lowest Polling Rate: {low_polling_rate}hz")
    # release the device
    usb.util.release_interface(dev, interface)
    # reattach the device to the OS kernel
    dev.attach_kernel_driver(interface)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            on_force_close()
            sys.exit(130)
        except SystemExit:
            on_force_close()
            os._exit(130)

signal.signal(signal.SIGINT, on_force_close)
signal.signal(signal.SIGHUP, on_force_close)
signal.signal(signal.SIGTERM, on_force_close)
