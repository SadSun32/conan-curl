# Conan curl

![Android status](https://github.com/rgpaul/conan-curl-scripts/workflows/Android/badge.svg)
![iOS status](https://github.com/rgpaul/conan-curl-scripts/workflows/iOS/badge.svg)
![Linux status](https://github.com/rgpaul/conan-curl-scripts/workflows/Linux/badge.svg)
![macOS status](https://github.com/rgpaul/conan-curl-scripts/workflows/macOS/badge.svg)
![Windows status](https://github.com/rgpaul/conan-curl-scripts/workflows/Windows/badge.svg)

This repository contains the conan receipe that is used to build the curl packages at [rgpaul bintray](https://bintray.com/manromen/rgpaul).

For Infos about curl please visit [curl.haxx.se](https://curl.haxx.se/).  
The library is licensed under the [curl License](https://curl.haxx.se/docs/copyright.html).  
This repository is licensed under the [MIT License](LICENSE).

## Android

The environmental `ANDROID_NDK_PATH` must be set to the path of the android ndk.

To create a package for Android you can run the following commands like:

`export ANDROID_NDK_PATH='/opt/android-ndks/android-ndk-r19c'`
`conan create . curl/7.65.0@rgpaul/stable -s os=Android -s os.api_level=21 -s compiler=clang -s compiler.version=8.0 -s compiler.libcxx=libc++ -s build_type=Release -o android_ndk=r19c -o android_stl_type=c++_static -s arch=x86_64`

### Requirements

* [CMake](https://cmake.org/)
* [Conan](https://conan.io/)
* [Android NDK r19c](https://developer.android.com/ndk/downloads/)

## Debian 9 (Stretch)

To create a package for Debian you can run the conan command like this:

`conan create . curl/7.65.0@rgpaul/stable -s os=Linux -s arch=x86_64 -s build_type=Release -o shared=False`

### Requirements

* [CMake](https://cmake.org/)
* [Conan](https://conan.io/)
* build-essential, make, curl, git, unzip and zip (`apt-get install build-essential cmake curl git unzip zip`)

## iOS

To create a package for iOS you can run the conan command like this:

`conan create . curl/7.65.0@rgpaul/stable -s os=iOS -s os.version=12.1 -s arch=armv7 -s build_type=Release -o shared=False`

### Requirements

* [CMake](https://cmake.org/)
* [Conan](https://conan.io/)
* [Xcode](https://developer.apple.com/xcode/)

## macOS

To create a package for macOS you can run the conan command like this:

`conan create . curl/7.65.0@rgpaul/stable -s os=Macos -s os.version=10.14 -s arch=x86_64 -s build_type=Release -o shared=False`

### Requirements

* [CMake](https://cmake.org/)
* [Conan](https://conan.io/)
* [Xcode](https://developer.apple.com/xcode/)

## Windows 10

To create a package for Windows 10 you can run the conan command like this:

`conan create . curl/7.65.0@rgpaul/stable -s os=Windows -s compiler="Visual Studio" -s compiler.runtime=MT -s arch=x86 -s build_type=Release -o shared=False`

### Requirements

* [CMake](https://cmake.org/)
* [Conan](https://conan.io/)
* [Visual Studio 2017](https://visualstudio.microsoft.com/de/downloads/)
