# based on https://android.googlesource.com/platform/ndk/+/master/ndk-gdb.py
import atexit
import os
import re
import subprocess
import sys
import tempfile
import time
import shutil

# inputs
package_id = "ru.ok.android.debug"
arch = "arm"
ndk_dir = "/Users/anatoly.korniltsev/Library/Android/sdk/ndk-bundle"
sys_root = "/Users/anatoly.korniltsev/tmp/tmp_sysroot"
additional_libs_dir = [
	"/Users/anatoly.korniltsev/ok/android/libwebrtc/jni/armeabi-v7a"
]
native_sources = [
	"/Users/anatoly.korniltsev/ok/webrtc-ok/out/Debug"
]
gdb_cmds = [
	"handle SIG33 noprint nostop",
	"handle SIGSEGV noprint nostop",
]
# end of inputs

gdb_port = "5555"
gdbserver = "{}/prebuilt/android-{}/gdbserver/gdbserver".format(ndk_dir, arch)
remote_gdbserver = "/data/data/{}/gdbserver".format(package_id)
remote_gdbserver_debug_scoket = "/data/data/{}/debug_socket".format(package_id)
local_gdb = "{}/prebuilt/darwin-x86_64/bin/gdb".format(ndk_dir)
gdb_server_log = "/data/local/tmp/gdb_server_log"
app_process_file = "{}/system/bin/app_process".format(sys_root)
sys_root_bin="{}/system/bin".format(sys_root)
sys_root_lib="{}/system/lib".format(sys_root)
app_process_target_file = "{}/system/bin/app_process".format(sys_root)

def error(msg):
	print(msg)
	sys.exit(-1)

def simple_call(cmd):
	print(">> simple_call: {}".format(cmd))
	return subprocess.call(cmd)

def run_as(cmd):
	return ["adb", "shell", "run-as", package_id] + cmd

def remote_gdbserver_exists():
	return simple_call(run_as(["ls",  remote_gdbserver])) == 0

def adb_push(src, dst):
	res = subprocess.call(["adb",  "push", src, dst])
	if res != 0:
		error("failed to push {} to {}".format(src, dst))

def push_gdbserver():
	if not remote_gdbserver_exists():
		tmp_file = "/data/local/tmp/mygdbserver"
		adb_push(gdbserver, tmp_file)
		cp_res = simple_call(run_as(["cp", tmp_file, remote_gdbserver])) 
		if cp_res != 0:
			error("failed to copy gdbserver to apps data directory")

def forward_port():
	res = simple_call([
		"adb", 
		"forward", 
		"tcp:{}".format(gdb_port),
		"localfilesystem:{}".format(remote_gdbserver_debug_scoket)
		])
	if res == 0:
		atexit.register(lambda: simple_call(["adb", "forward", "--remove", "tcp:{}".format(gdb_port)]))
	else:
		error("failed to forward port")

def get_app_pid():
	ps = grep_pids(package_id)
	print(ps)
	if len(ps) == 1:
		return ps[0]
	else:
		error("failed to find ps: {}".format(ps))	
	
def grep_pids(pattern):	
	res = subprocess.run(["adb", "shell", "ps", "|", "grep", pattern], stdout=subprocess.PIPE)
	if res.returncode == 0:
		ps = []
		print(res.stdout)
		processes = res.stdout.decode("utf-8").strip().split("\n")				
		for line in processes:			
			columns = re.split("\s+", line)
			if len(columns) >= 2:
				pid = columns[1]
				ps += [pid]
			else:
				error("failed to get pid, invalid command output {}".format(p))
		return ps
	else:
		return []		

def kill_gdbserver():
	ps = grep_pids("gdbserver")
	for p in ps:
		res = simple_call(run_as(["kill", "-9", p]))
		if res != 0:			
			print("failed to kill {}".format(p))

def start_gdbserver(pid):
	forward_port()
	kill_gdbserver()
	
	proc = subprocess.Popen(run_as([remote_gdbserver, "--once", "+{}".format(remote_gdbserver_debug_scoket), "--attach", pid]), stdin=subprocess.PIPE)
	
	time.sleep(1) # todo read stdout until line "Listening on Unix domain socket"

def pull_libraries_from_device():	
	if os.path.exists(sys_root):
		shutil.rmtree(sys_root)
		os.makedirs(sys_root_bin)
		os.makedirs(sys_root_lib)

	binaries = [
		"/system/bin/linker",
		"/system/lib/libc.so",
		"/system/lib/libm.so",
		"/system/lib/libdl.so",
	]
	
	app_process_res = simple_call(["adb", "pull", "/system/bin/app_process32", app_process_target_file])
	if app_process_res != 0:
		error("failed to pull lib /system/bin/app_process32")

	for b in binaries:
		print("pull {}".format(b))
		target_file = "{}{}".format(sys_root, b)
		target_dir = os.path.dirname(target_file)		
		res = simple_call(["adb", "pull", b, target_file])
		if res != 0:
			error("failed to pull lib {}".format(b))

	for d in additional_libs_dir:
		fs = os.listdir(d)
		for f in fs:
			shutil.copy("{}/{}".format(d,f), "{}/{}".format(sys_root_lib, f))

def start_gdb():	
	init_script = ""
	init_script += "set osabi GNU/Linux\n"	
	init_script += "file {}\n".format(app_process_file)
	init_script += "set solib-absolute-prefix {}\n".format(sys_root)
	init_script += "set solib-search-path {}:{}/system/bin:{}/system/lib\n".format(sys_root, sys_root, sys_root)
	init_script += "target remote :{}\n".format(gdb_port)
	for s in native_sources:
		init_script += "directory {}\n".format(s)

	for c in gdb_cmds:
		init_script += "{}\n".format(c)
	print(init_script)	
	script_fd, script_path = tempfile.mkstemp()
	os.write(script_fd, init_script.encode("utf-8"))
	os.close(script_fd)
	atexit.register(lambda: os.unlink(script_path))

	subprocess.call([local_gdb, "-x", script_path])


def main():
	app_pid = get_app_pid()
	print("pid is {}".format(app_pid))
	push_gdbserver()	
	start_gdbserver(app_pid)
	pull_libraries_from_device()
	start_gdb()

main()
