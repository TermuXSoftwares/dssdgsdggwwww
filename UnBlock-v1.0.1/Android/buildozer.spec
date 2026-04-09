[app]
title = UnBlock
package.name = unblock
package.domain = org.unblock
source.dir = .
source.include_exts = py,png,jpg
version = 1.0.1

requirements = python3,kivy,cryptography

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE
android.arch = arm64-v8a
android.minapi = 21

[buildozer]
log_level = 2