from conans import ConanFile, CMake, tools
import os

class CurlConan(ConanFile):
    name = "curl"
    version = "7.65.3"
    author = "Ralph-Gordon Paul (gordon@rgpaul.com)"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "with_ldap":[True, False], "android_ndk": "ANY", 
        "android_stl_type":["c++_static", "c++_shared"]}
    default_options = "shared=False", "with_ldap=False", "android_ndk=None", "android_stl_type=c++_static"
    description = "Command line tool and library for transferring data with URLs"
    url = "https://github.com/Manromen/conan-curl-scripts"
    license = "curl"
    exports_sources = "cmake-modules/*"
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
        variants = []

        if self.settings.os == "Android":
            android_toolchain = os.environ["ANDROID_NDK_PATH"] + "/build/cmake/android.toolchain.cmake"
            cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = android_toolchain
            cmake.definitions["ANDROID_NDK"] = os.environ["ANDROID_NDK_PATH"]
            cmake.definitions["ANDROID_ABI"] = tools.to_android_abi(self.settings.arch)
            cmake.definitions["ANDROID_STL"] = self.options.android_stl_type
            cmake.definitions["ANDROID_NATIVE_API_LEVEL"] = self.settings.os.api_level
            cmake.definitions["ANDROID_TOOLCHAIN"] = "clang"
            cmake.definitions["BUILD_TESTING"] = "OFF"
            cmake.definitions["BUILD_CURL_EXE"] = "OFF"
            tools.replace_in_file("%s/curl-%s/CMakeLists.txt" % (self.source_folder, self.version),
                "find_package(OpenSSL", "find_host_package(OpenSSL")
            self.addFindHostPackage()

        if self.settings.os == "iOS":
            ios_toolchain = "cmake-modules/Toolchains/ios.toolchain.cmake"
            cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = ios_toolchain
            cmake.definitions["BUILD_TESTING"] = "OFF"
            cmake.definitions["BUILD_CURL_EXE"] = "OFF"
            cmake.definitions["CMAKE_OSX_ARCHITECTURES"] = tools.to_apple_arch(self.settings.arch)
            tools.replace_in_file("%s/curl-%s/CMakeLists.txt" % (self.source_folder, self.version),
                "find_package(OpenSSL", "find_host_package(OpenSSL")
            
            # define all architectures for ios fat library
            if "arm" in self.settings.arch:
                variants = ["armv7", "armv7s", "armv8"]

            # apply build config for all defined architectures
            if len(variants) > 0:
                archs = ""
                for i in range(0, len(variants)):
                    if i == 0:
                        archs = tools.to_apple_arch(variants[i])
                    else:
                        archs += ";" + tools.to_apple_arch(variants[i])
                cmake.definitions["CMAKE_OSX_ARCHITECTURES"] = archs

            if self.settings.arch == "x86":
                cmake.definitions["IOS_PLATFORM"] = "SIMULATOR"
            elif self.settings.arch == "x86_64":
                cmake.definitions["IOS_PLATFORM"] = "SIMULATOR64"
            else:
                cmake.definitions["IOS_PLATFORM"] = "OS"

        if self.settings.os == "Macos":
            cmake.definitions["CMAKE_OSX_ARCHITECTURES"] = tools.to_apple_arch(self.settings.arch)

        cmake.definitions["CURL_DISABLE_LDAP"] = not self.options.with_ldap
        cmake.definitions["BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"

        cmake.configure(source_folder=library_folder)
        cmake.build()
        cmake.install()

        # we don't need package because the cmake.install() will direkly install all files into the package folder
    # def package(self):
    #     self.copy("*", dst="include", src='include')
    #     self.copy("*.lib", dst="lib", src='lib', keep_path=False)
    #     self.copy("*.dll", dst="bin", src='bin', keep_path=False)
    #     self.copy("*.so", dst="lib", src='lib', keep_path=False)
    #     self.copy("*.dylib", dst="lib", src='lib', keep_path=False)
    #     self.copy("*.a", dst="lib", src='lib', keep_path=False)

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
        self.requires("libressl/2.9.2@%s/%s" % (self.user, self.channel))

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
