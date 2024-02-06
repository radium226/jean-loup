# Jean-Loup

## 🚧 TODO
### High Priority
- [ ] Fix the way we tell the PiSugar board to shutdown (by using the `&` as specified in the documentation)
- [ ] Cleanup files that are presents (pictures, `journald`, etc.)
- [ ] Fix the time lapse generation
- [ ] Add the other WiFi configuration
- [ ] Put back the `systemd.volatile=overlay` kernel flag
- [x] Set the auto wake up after 1 day
### Low Priority
- [ ] Rename `timelapse` packages to `jean_loup` (and the `timelapse-*` CLI to `jl-*`)
- [ ] Add WireGuard to debug remotely
- [ ] Write documentation
- [ ] Auto sync RTC & web time
- [ ] Connect to Bluetooth and emit status
- [ ] Allow Wifi configuration
- [ ] Disable unneeded services when time lapse mode (using `ExecCond`)
- [ ] Add a power off button


https://www.raspberrypi.com/documentation/computers/camera_software.html#building-rpicam-apps

http://os.archlinuxarm.org/os/ArchLinuxARM-armv7-latest.tar.gz


https://github.com/andrewboring/alarm-images

http://cdn.pisugar.com/release/pisugar-power-manager.sh

echo "get battery" | nc -q 0 -U /tmp/pisugar-server.sock

openbsd-netcat

i2c --> config.txt
i2c-tools --> i2cdetect
i2c-dev /etc/module-load.d

https://raspberrypi.stackexchange.com/questions/141106/how-to-fix-the-libcamera-error-could-not-open-any-dmaheap-device

https://lexruee.ch/setting-i2c-permissions-for-non-root-users.html

https://www.paulligocki.com/wireless-access-point-raspberry-pi-zero-w/