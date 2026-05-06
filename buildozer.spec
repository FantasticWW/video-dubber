[app]

# (str) Title of your application
title = 视频配音工具

# (str) Package name
package.name = videodubber

# (str) Package domain (needed for android/ios packaging)
package.domain = org.video

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,wav,mp3,mp4,avi,mov,mkv

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,plyer,android

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/icon.png

# (str) Supported orientation (landscape, portrait or all)
orientation = sensor

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
# See https://python-for-android.readthedocs.io/en/latest/buildoptions/#buildoptions-advanced-options
# for more information about android permissions
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,RECORD_AUDIO,CAMERA,INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package locally.
# android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when first running
# buildozer.
android.accept_sdk_license = True

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# In past, `android.arch` was `armeabi` (ARMv5TE), but this is deprecated and
# no longer supported by NDK.
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) xml.etree.ElementTree tag name for the activity containing the
# main python code. Default is 'org.kivy.android.PythonActivity'
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Android's
# activity component.
#android.activity_class_name = org.kivy.android.PythonActivity

# (str) Extra xml to write directly inside the <manifest> element of AndroidManifest.xml
# use that parameter to provide a filename from where to load your custom XML code
#android.extra_manifest_xml = ./src/android/extra_manifest.xml

# (str) Extra xml to write directly inside tag <manifest><application> tag of AndroidManifest.xml
# use that parameter to provide a filename from where to load your custom XML code
#android.extra_manifest_application_xml = ./src/android/extra_manifest_application.xml

# (str) Full name including package path of the Java class that implements Android's
# service component.
#android.service_class_name = org.kivy.android.PythonService

# (str) Full name including package path of the Java class that implements Android's
# broadcast receiver component.
#android.broadcast_receiver_class_name = org.kivy.android.PythonBroadcastReceiver

# (str) The name that should be displayed in the Android system settings for this
# activity. Default is the application title.
#android.settings_title = My App Settings

# (str) The scheme to use in the Android Manifest's Intent Filter. Default is 'https'
#android.scheme = https

# (bool) enable debug mode for android apk
#android.debug = False

# (str) The path to a custom.keystore file that should be included in the APK.
# Can be used to override the default keystore used to sign the APK.
#android.keystore = /path/to/custom.keystore

# (str) The alias of the key in the keystore to use.
#android.keyalias = my_alias

# (str) The password for the keystore and the key (if different).
#android.keypassword = password

# (str) The password for the keystore.
#android.storepassword = password

# (str) Path to the file containing the Google Services JSON file.
#android.google_services_json = /path/to/google-services.json

# (str) Gradle dependencies to add to the Android build.
#android.gradle_dependencies = androidx.appcompat:appcompat:1.3.1

# (str) Java compiler version
#android.javac_version = 1.8

# (str) The build target for Android Studio
#android.build_target = android-30

# (str) Path to a Gradle extra properties file.
#android.gradle_extra_properties = /path/to/extra.properties

# [buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage, absolute or relative to spec file
# bin_dir = ./bin

#    -----------------------------------------------------------------------------
#    List as sections
#
#    You can define all the "list" as [section:key].
#    For example, for a custom activity launcher:
#
#    [app:android.launcher]
#    android.launcher_class_name = org.kivy.android.PythonActivity

#    -----------------------------------------------------------------------------
#    Buildozer specific warnings
#
#    Warnings can be set to be displayed with --warn-on-configuration.
#    For example:
#
#    [buildozer:warn-on-configuration]
#    warn_on_android_newer_target_api = True

#    -----------------------------------------------------------------------------
#    Kivy launcher specific configuration
#
#    Note: This section is only useful if you are using the Kivy Launcher.
#    See https://github.com/kivy/kivy-launcher for more information.
#
#    [kivy.launcher]
#    version = 1.0.0

#    -----------------------------------------------------------------------------
#    iOS specific
#
#    See https://kivy.org/doc/stable/guide/packaging-ios.html for more information.

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
