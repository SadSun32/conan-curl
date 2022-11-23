from conans import ConanFile, CMake, tools
import os

class CurlConan(ConanFile):
    name = "curl"
    author = "Ralph-Gordon Paul (gordon@rgpaul.com)"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "with_ldap":[True, False], "android_ndk": "ANY", 
        "android_stl_type":["c++_static", "c++_shared"]}
    default_options = "shared=False", "with_ldap=False", "android_ndk=None", "android_stl_type=c++_static"
    description = "Command line tool and library for transferring data with URLs"
    url = "https://github.com/RGPaul/conan-curl-scripts"
    license = "curl"
    generators = "cmake_paths"

    # download sources
    def source(self):
        url = "https://curl.haxx.se/download/curl-%s.tar.gz" % self.version
        tools.get(url)

        tools.replace_in_file("%s/curl-%s/CMakeLists.txt" % (self.source_folder, self.version),
            "project(CURL C)",
            '''project(CURL C)
include(${CMAKE_BINARY_DIR}/conan_paths.cmake) 
set(OPENSSL_ROOT_DIR ${CONAN_LIBRESSL_ROOT}) 
message(STATUS "OPENSSL_ROOT_DIR: ${OPENSSL_ROOT_DIR}") 
''')

    # compile using cmake
    def build(self):
        cmake = CMake(self)
        library_folder = "%s/curl-%s" % (self.source_folder, self.version)
        cmake.verbose = True

        if self.settings.os == "Android":
            self.applyCmakeSettingsForAndroid(cmake)

        if self.settings.os == "iOS":
            self.applyCmakeSettingsForiOS(cmake)

        if self.settings.os == "Macos":
            self.applyCmakeSettingsFormacOS(cmake)

        if self.settings.os == "Windows":
            self.applyCmakeSettingsForWindows(cmake)

        cmake.definitions["CURL_DISABLE_LDAP"] = not self.options.with_ldap
        cmake.definitions["BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"

        cmake.configure(source_folder=library_folder)
        cmake.build()
        cmake.install()

    def applyCmakeSettingsForAndroid(self, cmake):
        android_toolchain = os.environ["ANDROID_NDK_PATH"] + "/build/cmake/android.toolchain.cmake"
        cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = android_toolchain
        cmake.definitions["ANDROID_NDK"] = os.environ["ANDROID_NDK_PATH"]
        cmake.definitions["ANDROID_ABI"] = tools.to_android_abi(self.settings.arch)
        cmake.definitions["ANDROID_STL"] = self.options.android_stl_type
        cmake.definitions["ANDROID_NATIVE_API_LEVEL"] = self.settings.os.api_level
        cmake.definitions["ANDROID_TOOLCHAIN"] = "clang"
        cmake.definitions["BUILD_TESTING"] = "OFF"
        cmake.definitions["BUILD_CURL_EXE"] = "OFF"
        cmake.definitions["CMAKE_USE_LIBSSH2"] = "OFF"
        tools.replace_in_file("%s/curl-%s/CMakeLists.txt" % (self.source_folder, self.version),
            "find_package(OpenSSL", "find_host_package(OpenSSL")
        self.addFindHostPackage()

    def applyCmakeSettingsForiOS(self, cmake):
        cmake.definitions["CMAKE_SYSTEM_NAME"] = "iOS"
        cmake.definitions["DEPLOYMENT_TARGET"] = "10.0"
        cmake.definitions["CMAKE_OSX_DEPLOYMENT_TARGET"] = "10.0"
        cmake.definitions["CMAKE_XCODE_ATTRIBUTE_ONLY_ACTIVE_ARCH"] = "NO"
        cmake.definitions["CMAKE_IOS_INSTALL_COMBINED"] = "YES"

        cmake.definitions["BUILD_TESTING"] = "OFF"
        cmake.definitions["BUILD_CURL_EXE"] = "OFF"
        cmake.definitions["CMAKE_USE_LIBSSH2"] = "OFF"
        #cmake.definitions["PICKY_COMPILER"] = "OFF"
        
        # CMAKE_TOOLCHAIN_FILE needs to be defined, so that the scripts of curl know that we are cross compiling
        cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = ""

        tools.replace_in_file("%s/curl-%s/CMakeLists.txt" % (self.source_folder, self.version),
            "find_package(OpenSSL", "find_host_package(OpenSSL")
        self.addFindHostPackage()
        
        # define all architectures for ios fat library
        if "arm" in self.settings.arch:
            cmake.definitions["CMAKE_OSX_ARCHITECTURES"] = "armv7;armv7s;arm64;arm64e"
        else:
            cmake.definitions["CMAKE_OSX_ARCHITECTURES"] = tools.to_apple_arch(self.settings.arch)

    def applyCmakeSettingsFormacOS(self, cmake):
        cmake.definitions["CMAKE_OSX_ARCHITECTURES"] = tools.to_apple_arch(self.settings.arch)
        cmake.definitions["CMAKE_USE_LIBSSH2"] = "OFF"

    def applyCmakeSettingsForWindows(self, cmake):
        cmake.definitions["CMAKE_BUILD_TYPE"] = self.settings.build_type
        cmake.definitions["CMAKE_USE_LIBSSH2"] = "OFF"
        if self.settings.compiler == "Visual Studio":
            # check that runtime flags and build_type correspond (consistency check)
            if "d" not in self.settings.compiler.runtime and self.settings.build_type == "Debug":
                raise Exception("Compiling for Debug mode but compiler runtime does not contain 'd' flag.")

            if self.settings.build_type == "Debug":
                cmake.definitions["CMAKE_CXX_FLAGS_DEBUG"] = "/%s" % self.settings.compiler.runtime
            elif self.settings.build_type == "Release":
                cmake.definitions["CMAKE_CXX_FLAGS_RELEASE"] = "/%s" % self.settings.compiler.runtime

    def addFindHostPackage(self):
        tools.replace_in_file("%s/curl-%s/CMakeLists.txt" % (self.source_folder, self.version),
            "project(CURL C)",
            '''project(CURL C)
# This macro lets you find executable programs on the host system
macro (find_host_package)
    set (CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
    set (CMAKE_FIND_ROOT_PATH_MODE_LIBRARY NEVER)
    set (CMAKE_FIND_ROOT_PATH_MODE_INCLUDE NEVER)

    find_package(${ARGN})

    set (CMAKE_FIND_ROOT_PATH_MODE_PROGRAM ONLY)
    set (CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
    set (CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
endmacro (find_host_package)
''')

    def requirements(self):
        self.requires("libressl/3.5.2")

    def configure(self):
        if self.settings.os == "Android":
            self.options["libressl"].shared = self.options.shared
            self.options["libressl"].android_stl_type = self.options.android_stl_type
            self.options["libressl"].android_ndk = self.options.android_ndk

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ['include']

    def package_id(self):
        if "arm" in self.settings.arch and self.settings.os == "iOS":
            self.info.settings.arch = "AnyARM"

    def config_options(self):
        # remove android specific option for all other platforms
        if self.settings.os != "Android":
            del self.options.android_ndk
            del self.options.android_stl_type
