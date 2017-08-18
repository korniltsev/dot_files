# very dumb script to find all .c/.h files and create a dumb CMakeLists.txt to import in CLion
import os
excludes = [
  'webrtc/src/webrtc/sdk/objc/',
  'webrtc/src/webrtc/examples'
]
header = """
cmake_minimum_required(VERSION 3.6)
project(cpp)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES

"""
footer = """
        webrtc/src/webrtc/pc/peerconnectionfactory_unittest.cc
        webrtc/src/webrtc/pc/peerconnectioninterface_unittest.cc
)

include_directories(webrtc/src)
include_directories(webrtc/src/third_party/googletest/src/googlemock/include)
include_directories(webrtc/src/third_party/googletest/src/googletest/include)
include_directories(webrtc/src/third_party/android_tools/ndk/platforms/android-22/arch-arm/usr/include)
add_definitions(-DWEBRTC_POSIX)
add_definitions(-DGTEST_RELATIVE_PATH)
add_definitions(-DWEBRTC_ANDROID)

add_executable(cpp ${SOURCE_FILES})
"""
print header
for root, directory, fs  in os.walk('webrtc/src/webrtc'):
  for f in fs:
    if f.endswith('.c') or f.endswith('.h') or f.endswith('.cpp') or f.endswith('.cc'):
      skip = False
      for e in excludes:
        if root.startswith(e):
          skip = True
      if skip:
        break
      print "    " + root + "/" + f

print footer
