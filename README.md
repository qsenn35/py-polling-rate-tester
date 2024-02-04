# Python Mouse Polling Rate Tester

## DISCLAIMER
This was written on MacOS, this may not work for Linux and WSL.

## Motivations
Most polling rate testers (other than MouseTester) don't accurately show Polling Rates past 4000Hz.
MouseTester is great if you need a graph to show Polling Rate variability, but if all you want to do is check the minimum, average, and maximum polling rates of a mouse, a simple command-line tool will do the trick.

## How It Works
This script uses the `pyusb` python package to interact with `libusb` to get inputs directly from the Mouse USB device.

## Requirements
You'll need python3 for this script.

Then you'll need to install the dependencies:
```
pip install -r requirements.txt
```

For MacOS or Windows you'll need to install `libusb` for `pyusb` to work.
Follow the [`pyusb` documentation](https://github.com/pyusb/pyusb?tab=readme-ov-file#requirements-and-platform-support) to install `libusb`. 



## Find Your Vendor ID and Product ID
To find your Vendor ID and Product ID for your Mouse USB Device, pass the `list` option to the script.

Like so:
```
python main.py list
```
Then look for your device, and identify the `idVendor` and `idProduct` properties. Copy the **entire** hex code for each.

## Test Mouse Polling Rate
To run a polling rate test simply pass the `test` option, the mouse's name, the vendor id, and the product id of your mouse.

Like so:
```
sudo python main.py test MOUSE_NAME USB_VENDOR_ID USB_PRODUCT_ID
```

If your Vendor ID or Product ID is not already in `mice.csv`, it will be added. This is to help build a database of vendor and product ids people can copy and paste easily. If the script adds to the `mice.csv` file you'll be prompted to open a Pull-Request for this github repo. Contributions are greatly appreciated!
