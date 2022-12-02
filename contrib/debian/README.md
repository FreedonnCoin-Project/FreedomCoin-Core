
Debian
====================
This directory contains files used to package freedomcoind/freedomcoin-qt
for Debian-based Linux systems. If you compile freedomcoind/freedomcoin-qt yourself, there are some useful files here.

## freedomcoin: URI support ##


freedomcoin-qt.desktop  (Gnome / Open Desktop)
To install:

	sudo desktop-file-install freedomcoin-qt.desktop
	sudo update-desktop-database

If you build yourself, you will either need to modify the paths in
the .desktop file or copy or symlink your freedomcoin-qt binary to `/usr/bin`
and the `../../share/pixmaps/freedomcoin128.png` to `/usr/share/pixmaps`

freedomcoin-qt.protocol (KDE)

