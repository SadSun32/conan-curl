from conans import ConanFile, CMake, tools
import os

class CurlConan(ConanFile):
    name = "curl"
    version = "7.65.0"
    author = "Ralph-Gordon Paul (gordon@rgpaul.com)"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "with_ldap":[True, False], "android_ndk": "ANY", 
        "android_stl_type":["c++_static", "c++_shared"]}
    default_options = "shared=False", "with_ldap=False", "android_ndk=None", "android_stl_type=c++_static"
    description = "command line tool and library for transferring data with URLs"
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
            '''include(${CMAKE_BINARY_DIR}/conan_paths.cmake) 
            set(OPENSSL_ROOT_DIR ${CONAN_LIBRESSL_ROOT}) 
            set(OPENSSL_USE_STATIC_LIBS TRUE) 
            message(STATUS "OPENSSL_ROOT_DIR: ${OPENSSL_ROOT_DIR}") 
            project(CURL C)''')

    # compile using cmake
    def build(self):
        cmake = CMake(self)
        library_folder = "%s/curl-%s" % (self.source_folder, self.version)
        cmake.verbose = True

        if self.settings.os == "Android":
            android_toolchain = os.environ["ANDROID_NDK_PATH"] + "/build/cmake/android.toolchain.cmake"
            cmake.definitions["CMAKE_SYSTEM_NAME"] = "Android"
            cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = android_toolchain
            cmake.definitions["ANDROID_NDK"] = os.environ["ANDROID_NDK_PATH"]
            cmake.definitions["ANDROID_ABI"] = tools.to_android_abi(self.settings.arch)
            cmake.definitions["ANDROID_STL"] = self.options.android_stl_type
            cmake.definitions["ANDROID_NATIVE_API_LEVEL"] = self.settings.os.api_level
            cmake.definitions["ANDROID_TOOLCHAIN"] = "clang"

        if self.settings.os == "iOS":
            ios_toolchain = "cmake-modules/Toolchains/ios.toolchain.cmake"
            cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = ios_toolchain
            cmake.definitions["BUILD_TESTING"] = "OFF"
            cmake.definitions["BUILD_CURL_EXE"] = "OFF"
            cmake.definitions["CMAKE_OSX_ARCHITECTURES"] = tools.to_apple_arch(self.settings.arch)
            if self.settings.arch == "x86" or self.settings.arch == "x86_64":
                cmake.definitions["IOS_PLATFORM"] = "SIMULATOR"
            else:
                cmake.definitions["IOS_PLATFORM"] = "OS"

        if self.settings.os == "Macos":
            cmake.definitions["CMAKE_OSX_ARCHITECTURES"] = tools.to_apple_arch(self.settings.arch)

        cmake.definitions["CURL_DISABLE_LDAP"] = not self.options.with_ldap

        cmake.configure(source_folder=library_folder)
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("*", dst="include", src='include')
        self.copy("*.lib", dst="lib", src='lib', keep_path=False)
        self.copy("*.dll", dst="bin", src='bin', keep_path=False)
        self.copy("*.so", dst="lib", src='lib', keep_path=False)
        self.copy("*.dylib", dst="lib", src='lib', keep_path=False)
        self.copy("*.a", dst="lib", src='lib', keep_path=False)
        
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

    def config_options(self):
        # remove android specific option for all other platforms
        if self.settings.os != "Android":
            del self.options.android_ndk
            del self.options.android_stl_type
