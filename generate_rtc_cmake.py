# very dumb script to find all .c/.h files and create a dumb CMakeLists.txt to import in CLion
import os
src_dir="src"
excludes = [
  'webrtc/src/webrtc/sdk/objc/',
  'webrtc/src/webrtc/examples'
]

headers_only=[
  "webrtc/common_audio",
  "webrtc/voice_engine",
  "webrtc/media",
  "webrtc/modules",
  "webrtc/test",
]
header = """
cmake_minimum_required(VERSION 3.6)
project(cpp)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES

"""
footer = """
)

include_directories(%s)
include_directories(%s/third_party/googletest/src/googlemock/include)
include_directories(%s/third_party/googletest/src/googletest/include)
include_directories(%s/third_party/android_tools/ndk/platforms/android-22/arch-arm/usr/include)
add_definitions(-DWEBRTC_POSIX)
add_definitions(-DGTEST_RELATIVE_PATH)
add_definitions(-DWEBRTC_ANDROID)

add_executable(cpp ${SOURCE_FILES})
"""

manifest = """<?xml version="1.0" encoding="utf-8"?>
<manifest package="webrtc.project.stub">
</manifest>
"""

build_gradle = """
buildscript {
    repositories {
        jcenter()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:2.3.2'
    }
}

apply plugin: 'com.android.library'

android {
    compileSdkVersion 26
    buildToolsVersion "26.0.1"
    defaultConfig {

        minSdkVersion 16
        targetSdkVersion 26
        externalNativeBuild {
            cmake {
                cppFlags ""
            }
        }
    }
    externalNativeBuild {
        cmake {
            path "CMakeLists.txt"
        }
    }
}

repositories {
    jcenter()
}

dependencies {

    androidTestCompile('com.android.support.test.espresso:espresso-core:2.2.2', {
        exclude group: 'com.android.support', module: 'support-annotations'
    })
    testCompile 'junit:junit:4.12'
}

"""
footer = footer % (src_dir, src_dir, src_dir, src_dir)
print header
for root, directory, fs  in os.walk(src_dir + '/webrtc'):
  for f in fs:
    if f.endswith('.c') or f.endswith('.h') or f.endswith('.cpp') or f.endswith('.cc'):
      skip = False
      for e in excludes:
        if root.startswith(e):
	  skip = True
      for e in headers_only:
        if e in root and f.endswith(".cc"):
	  skip = True
      if skip:
        break
      print "    " + root + "/" + f

print footer

manifest_file = open('AndroidManifest.xml', 'w')
manifest_file.write(manifest)
manifest_file.close()

build_gradle_file = open('build.gradle', 'w')
build_gradle_file.write(build_gradle)
build_gradle_file.close()
