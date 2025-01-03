
Potential future resources:

https://www.instructables.com/USB-Barcode-Scanner-Raspberry-Pi/
https://piddlerintheroot.com/barcode-scanner/
https://www.raspberrypi.com/products/raspberry-pi-pico/?variant=raspberry-pi-pico-w
https://www.amazon.com/Raspberry-Quad-core-Bluetooth-onboard-Antenna/dp/B0CCRP85TR?dib=eyJ2IjoiMSJ9.gER6ai2B6BUf_1KSPtGdItDbEGkml4gNmPur2l4bvUcKwJ3QnkBK4ADb5Fs-kUHYcABF8DRxq8lpc83641Sw265VBh-EW4VpPVcpiNPactVvbkR5aGfmVy-hhs_Klb3DWr6KHi4boihikJRQTTqeUJeB2L0ooGJvpkMbBblmNrn5ra4V2_eV2mm5lBIz5Z6LTd5O5px7nN1kahRAaNPrWI420EyixOl2mksPUtuFNHU.JcQUYlXrVvH8Kpf66EHAt8ot80Au-Mb46aBRR5bUlS0&dib_tag=se&keywords=raspberry%2Bpi&qid=1734389441&sr=8-15&th=1
https://www.amazon.com/RS-Components-Raspberry-Pi-Motherboard/dp/B07BFH96M3?source=ps-sl-shoppingads-lpcontext&ref_=fplfs&psc=1&smid=A1JX327N91FZPX&gQT=2

### running scripts in the background
Use systemmd
https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/

### Display resources
https://learn.adafruit.com/monochrome-oled-breakouts/python-usage-2

### systemmd file

Edit file
`sudo vim /etc/systemd/system/inventory-runner.service`

```
[Unit]
Description=Grocery Inventory Runner
After=network.target

[Service]
ExecStart=/home/knab-server/grocery-inventory/inventory-runner.sh
WorkingDirectory=/home/knab-server/grocery-inventory
User=knab-server
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Reload and enable the service
```
sudo systemctl daemon-reload
sudo systemctl enable inventory-runner.service
```
Start the service
```
sudo systemctl start inventory-runner.service
```
Verify the service is running
```
sudo systemctl status inventory-runner.service
```
Check journal
```
journalctl -u inventory-runner.service
```
Stop service
```
sudo systemctl stop inventory-runner.service
```
Disable service
```
sudo systemctl disable inventory-runner.service
```
Restart Service
```
sudo systemctl restart inventory-runner.service
```