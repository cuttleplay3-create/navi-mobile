[app]
title = N.A.V.I
package.name = navi
package.domain = org.cuttle

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 1.0

requirements = python3==3.11.15,kivy==2.3.0,groq,requests,urllib3,certifi,charset-normalizer,idna,psutil

orientation = portrait
fullscreen = 0

android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

android.allow_backup = True

icon.filename = Icon.png

[buildozer]
log_level = 2
warn_on_root = 1
