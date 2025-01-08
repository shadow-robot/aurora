#!/usr/bin/env python3

# Copyright 2024, 2025 Shadow Robot Company Ltd.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation version 2 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import subprocess
import sys
import threading
import time
import re
import inspect
import shutil
import platform
import speedtest
import distro


class bcolors:  # pylint: disable=C0103
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class SubprocessTimeout:
    def __init__(self):
        pass

    @staticmethod
    def check_for_hung_processes_spawned_by_child(proc):
        """
            proc.kill(); proc.communicate() can hang if the child process itself creates new
            children which aren't responding, so let's check for that in a second try layer
        """
        try:
            result = proc.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            return_code = "timed out (sub-sub process not responding)"
            stdout = "timed out (sub-sub process not responding)"
        else:
            return_code = "timed out"
            stdout = result[0]
        return return_code, stdout

    @staticmethod
    def run(timeout, command):
        with subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as proc:
            try:
                result = proc.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                return_code, stdout = SubprocessTimeout.check_for_hung_processes_spawned_by_child(proc)
            else:
                return_code = proc.returncode
                stdout = result[0]
        return subprocess.CompletedProcess(args=command, returncode=return_code, stdout=stdout)


class ProgressBar:
    def __init__(self):
        self._last_start = 0
        self._progress_x = 0

    def start_progress(self, title):
        sys.stdout.write(title + ": [" + "-"*40 + "]" + chr(8)*41)
        sys.stdout.flush()
        self._last_start = 0

    def progress(self, x, sleep_time=0.01, event=None):
        for i in range(self._last_start, x):
            self._update_progress(i)
            time.sleep(sleep_time)
            if event:
                if event.is_set():
                    for j in range(i, x):
                        self._update_progress(j)
                        time.sleep(0.01)
                    break
        self._last_start = x

    def _update_progress(self, x):
        x = int(x * 40 // 100)
        sys.stdout.write("#" * (x - self._last_start))
        sys.stdout.flush()
        self._last_start = x

    def end_progress(self):
        sys.stdout.write("#" * (40 - self._last_start) + "]\n")
        sys.stdout.flush()

    def thread_interpolate_progress(self, x, duration):
        diff = x - self._last_start
        time_per_step = duration / diff
        event = threading.Event()
        def thread_target():
            self.progress(x, time_per_step, event)

        thread = threading.Thread(target=thread_target)
        return thread, event

    @staticmethod
    def delete_last_n_lines(n):  # pylint: disable=C0103
        "Deletes the last n lines printed to the terminal"
        for _ in range(n):
            # cursor up one line
            sys.stdout.write('\x1b[1A')
            # delete last line
            sys.stdout.write('\x1b[2K')


class BaseUrlTest:
    def __init__(self, name_url_dict):
        self._name_url_dict = name_url_dict
        self.results = {}

    def _loop_test(self, funct, args, success_function, message_str,
                   after_test_funct=None, num_retries=5, timeout=5, thread_interp_prog=False):
        results = {}
        successes = 0
        attempts = num_retries
        print(message_str)
        progress_bar = ProgressBar()
        progress_bar.start_progress(f"Running {attempts} tests")
        for i in range(attempts):
            progress_bar_goal = int((i+1) * 100 / attempts)
            if thread_interp_prog:
                thread, event = progress_bar.thread_interpolate_progress(progress_bar_goal, timeout)
                thread.start()
            results[i] = funct(*args)
            if success_function(results[i]):
                successes += 1
            if after_test_funct:
                after_test_funct()
            if not thread_interp_prog:
                progress_bar.progress(progress_bar_goal)
            else:
                event.set()
                thread.join()
            time.sleep(1)
        progress_bar.end_progress()
        progress_bar.delete_last_n_lines(2)
        print(message_str.replace("Running", "Finished"))
        failures = attempts - successes
        return self._generate_result(attempts, successes, failures, results)


    def _generate_result(self, attempts, successes, failures, results):
        raise NotImplementedError

    def run_tests(self):
        raise NotImplementedError


class WgetTest(BaseUrlTest):
    TIMEOUT = 45
    TEMP_FILE_NAME = '/tmp/sr_test_wget_python'
    NUM_RETRIES = 3

    def run_tests(self):
        total_urls = len(self._name_url_dict)
        for name, url in self._name_url_dict.items():
            args = (url, self.TEMP_FILE_NAME, self.TIMEOUT)

            def _after_test_funct():
                if os.path.exists(self.TEMP_FILE_NAME):
                    os.remove(self.TEMP_FILE_NAME)

            _after_test_funct()
            this_url_index = list(self._name_url_dict.keys()).index(name) + 1
            message_str = f"Running {self.NUM_RETRIES} wget test(s) on {url} with a timeout " \
                          f"of {self.TIMEOUT}s each test ({this_url_index}/{total_urls})"
            self.results[name] = self._loop_test(self._wget,
                                                 args,
                                                 self.success_function,
                                                 message_str,
                                                 _after_test_funct,
                                                 timeout=self.TIMEOUT,
                                                 num_retries=self.NUM_RETRIES,
                                                 thread_interp_prog=True)
        return self.results

    @staticmethod
    def success_function(result):
        temp_file_path = result.args[2]
        if not os.path.exists(temp_file_path):
            return False
        if os.path.getsize(temp_file_path) > 0:
            return True
        return False

    @staticmethod
    def _wget(url, output_path, timeout=None):
        command = ['wget', '-O', f'{output_path}', url]
        return SubprocessTimeout().run(timeout, command)

    @staticmethod
    def _generate_result(attempts, successes, failures, results):
        all_succeeded = False
        if successes == attempts:
            all_succeeded = True
        return {
            'all_succeeded': all_succeeded,
            'attempts': attempts,
            'successes': successes,
            'failures': failures,
            'results': results
        }

    def print_results(self, results, extended_info=True):
        for name in self._name_url_dict.keys():
            result_dict = results[name]
            out_color = bcolors.FAIL
            if result_dict['all_succeeded']:
                out_color = bcolors.OKGREEN

            print(f"Wget test results for {name}:")

            print(out_color, end='')
            print(f"  All succeeded: {result_dict['all_succeeded']}")
            print(f"  Total attempts: {result_dict['attempts']}")
            print(f"  Failed attempts: {result_dict['failures']}")
            print(bcolors.ENDC, end='')
            if extended_info:
                out_color = bcolors.FAIL
                if result_dict['all_succeeded']:
                    out_color = bcolors.OKGREEN
                elif result_dict['successes'] > 0:
                    out_color = bcolors.WARNING

                print(f"{out_color}  Successful attempts: {result_dict['successes']}{bcolors.ENDC}\n")
                for attempt, wget_result in result_dict['results'].items():
                    out_color = bcolors.WARNING
                    if wget_result.returncode == 0:
                        continue
                    print(f"{out_color}Wget test attempt {attempt+1} output: \n{wget_result.stdout.decode('utf-8')}" +
                          f"{bcolors.ENDC}\n")
            print('')


class PingTest(BaseUrlTest):
    NUM_RETRIES = 3
    TIMEOUT = 10

    @staticmethod
    def success_function(result):
        return result.returncode == 0

    def run_tests(self):
        total_urls = len(self._name_url_dict)
        for name, url in self._name_url_dict.items():
            args = (url,self.TIMEOUT)
            this_url_index = list(self._name_url_dict.keys()).index(name) + 1
            message_str = f"Running {self.NUM_RETRIES} ping test(s) on {url} with a timeout " \
                          f"of {self.TIMEOUT}s each ({this_url_index}/{total_urls})"
            self.results[name] = self._loop_test(self._ping,
                                                 args,
                                                 self.success_function,
                                                 message_str,
                                                 timeout=self.TIMEOUT,
                                                 num_retries=self.NUM_RETRIES,
                                                 thread_interp_prog=True)
        return self.results

    @staticmethod
    def _ping_regex(result):
        # extract all 'time=x.xx ms' from the ping output
        return re.findall(r'time=\d+\.\d+ ms', result.stdout.decode('utf-8'))

    @staticmethod
    def _ping(url, timeout, num_pings=4):
        command = ['ping', '-c', str(num_pings), url]
        return SubprocessTimeout().run(timeout, command)

    def _generate_result(self, attempts, successes, failures, results):
        all_succeeded = False
        string_results = {}
        numerical_times = {}
        if successes == attempts:
            all_succeeded = True
        for attempt, ping_result in results.items():
            string_results[attempt] = PingTest._ping_regex(ping_result)
        for attempt, ping_result_string_list in string_results.items():
            numerical_times[attempt] = {}
            for i, time_string in enumerate(ping_result_string_list):
                numerical_times[attempt][i] = float(time_string.split('=')[1].split(' ')[0])
        min_time = min([time for time_list in numerical_times.values() for time in time_list.values()])
        max_time = max([time for time_list in numerical_times.values() for time in time_list.values()])
        avg_time = round(sum([time for time_list in numerical_times.values() for time in time_list.values()]) /
                         (attempts * len(numerical_times)), 2)
        jitter = round((max_time - min_time), 2)
        return {
            'all_succeeded': all_succeeded,
            'min_time_ms': min_time,
            'max_time_ms': max_time,
            'avg_time_ms': avg_time,
            'jitter_ms': jitter,
            'attempts': attempts,
            'successes': successes,
            'failures': failures}

    def print_results(self, results, extended_info=True):
        for name in self._name_url_dict.keys():
            result_dict = results[name]
            print(f"Ping test results for {name}:")
            out_color = bcolors.FAIL
            if result_dict['all_succeeded']:
                out_color = bcolors.OKGREEN

            print(f"{out_color}", end='')
            print(f"  All succeeded: {result_dict['all_succeeded']}")
            print(f"  Total attempts: {result_dict['attempts']}")
            print(f"  Failed attempts: {result_dict['failures']}")
            print(f"{bcolors.ENDC}", end='')
            if extended_info:
                if out_color == bcolors.FAIL:
                    out_color = bcolors.WARNING
                print(f"{out_color}", end='')
                print(f"  Successful attempts: {result_dict['successes']}")
                print(f"  Failed attempts: {result_dict['failures']}")
                print(f"  Min time: {result_dict['min_time_ms']} ms")
                print(f"  Max time: {result_dict['max_time_ms']} ms")
                print(f"  Avg time: {result_dict['avg_time_ms']} ms")
                print(f"  Jitter: {result_dict['jitter_ms']} ms")
                print(f"{bcolors.ENDC}", end='')
            print('')


class GitCloneTest(BaseUrlTest):
    TIMEOUT = 30
    NUM_RETRIES = 2
    LOCAL_GIT_PATH = '/tmp/sr_test_git_clone_python'

    @staticmethod
    def _after_test_funct():
        if os.path.exists(GitCloneTest.LOCAL_GIT_PATH):
            subprocess.run(['rm', '-rf', GitCloneTest.LOCAL_GIT_PATH], check=True)

    def run_tests(self):
        self._after_test_funct()
        for name, url in self._name_url_dict.items():
            message_str = f"Running git clone test on {url} with a timeout of {self.TIMEOUT}s"
            self.results[name] = self._loop_test(self.git_clone, (url, self.LOCAL_GIT_PATH, self.TIMEOUT),
                                                 self.success_function,
                                                 message_str,
                                                 self._after_test_funct,
                                                 num_retries=self.NUM_RETRIES,
                                                 timeout=self.TIMEOUT,
                                                 thread_interp_prog=True)
        return self.results

    @staticmethod
    def git_clone(url, local_path, timeout):
        clone_command = ['git', 'clone', url, local_path]
        status_command = ['git', '-C', local_path, 'status', '--porcelain']
        result = SubprocessTimeout().run(timeout, clone_command)
        clone_status = subprocess.run(status_command, capture_output=True, check=False)
        result.clone_status = clone_status
        return result

    @staticmethod
    def success_function(result):
        # Check return code from git clone
        if result.returncode != 0:
            return False
        # Check return code from git status --porcelain
        if result.clone_status.returncode != 0:
            return False
        # Check for any output from git status --porcelain (indicates difference between local and remote)
        if result.clone_status.stdout.decode('utf-8') != '':
            return False
        return True

    def _generate_result(self, attempts, successes, failures, results):

        all_succeeded = False
        if successes == attempts:
            all_succeeded = True
        return {
            'all_succeeded': all_succeeded,
            'attempts': attempts,
            'successes': successes,
            'failures': failures,
            'results': results,
            'clone_return_codes': [result.returncode for result in results.values()],
            'clone_status_return_codes': [result.clone_status.returncode for result in results.values()]
        }

    def print_results(self, results, extended_info=True):
        for name in self._name_url_dict.keys():
            print(f"Git clone test results for {name}:")
            result_dict = results[name]
            out_color = bcolors.FAIL
            if result_dict['all_succeeded']:
                out_color = bcolors.OKGREEN

            print(f"{out_color}", end='')
            print(f"  All succeeded: {result_dict['all_succeeded']}")
            print(f"  Total attempts: {result_dict['attempts']}")
            print(f"  Failed attempts: {result_dict['failures']}")
            print(f"{bcolors.ENDC}", end='')
            if extended_info:
                if out_color == bcolors.FAIL:
                    out_color = bcolors.WARNING
                print(f"{out_color}", end='')
                print(f"  Git clone return codes: {result_dict['clone_return_codes']}")
                print(f"  Git status return codes: {result_dict['clone_status_return_codes']}")
                print(f"{bcolors.ENDC}")


class SpeedTest:
    ACCEPTABLE_UPLOAD_SPEED = 10  # Mbps
    ACCEPTABLE_DOWNLOAD_SPEED = 20  # Mbps
    ACCEPTABLE_PING = 50  # ms

    @staticmethod
    def run_tests():
        test = speedtest.Speedtest(secure=True)
        servernames = []
        test.get_servers(servernames)
        data = test.get_config()

        service_data = data["client"]["isp"]
        ip_data = data["client"]["ip"]

        print("Performing upload test...")
        uploading = round(test.upload() / (1024 * 1024), 2)
        print("Performing download test...")
        downloading = round(test.download() / (1024 * 1024), 2)

        ping = test.results.ping
        results = {
            'ping': ping,
            'upload': uploading,
            'download': downloading,
            'service': service_data,
            'ip': ip_data
        }
        return results

    def print_results(self, results, extended_info=True):
        up_color = bcolors.WARNING
        if results['upload'] > self.ACCEPTABLE_UPLOAD_SPEED:
            up_color = bcolors.OKGREEN

        down_color = bcolors.WARNING
        if results['download'] > self.ACCEPTABLE_DOWNLOAD_SPEED:
            down_color = bcolors.OKGREEN

        ping_color = bcolors.WARNING
        if results['ping'] < self.ACCEPTABLE_PING:
            ping_color = bcolors.OKGREEN

        print("Results for general internet speed test:")
        print(f"{ping_color}  Ping: {results['ping']} ms{bcolors.ENDC}")
        print(f"{up_color}  Upload: {results['upload']} Mbps{bcolors.ENDC}")
        print(f"{down_color}  Download: {results['download']} Mbps{bcolors.ENDC}")
        if extended_info:
            print(f"  Service provider: {results['service']}")
            print(f"  IP address: {results['ip']}")
        print('')


class GetSystemInfo:
    ACCEPTABLE_OS_VERSION = '20.04'
    WANRING_OS_VERSION = '22.04'
    ACCEPTABLE_CPU_STRING = 'Intel'
    ACCEPTABLE_UPTIME_HOURS = 24
    ACCEPTABLE_FREE_DISK_SPACE_GB = 25
    ACCEPTABLE_UPTIME_SECONDS = ACCEPTABLE_UPTIME_HOURS * 60 * 60

    def __init__(self):
        self.results = {}

    @staticmethod
    def get_uptime():
        with open('/proc/uptime', 'r', encoding='utf-8') as proc:
            uptime_seconds = float(proc.readline().split()[0])
        return uptime_seconds

    @staticmethod
    def get_processor_name():
        if platform.system() == "Windows":
            return platform.processor()
        if platform.system() == "Darwin":
            os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
            command ="sysctl -n machdep.cpu.brand_string"
            return subprocess.check_output(command).strip()
        if platform.system() == "Linux":
            command = "cat /proc/cpuinfo"
            all_info = subprocess.check_output(command, shell=True).decode().strip()
            for line in all_info.split("\n"):
                if "model name" in line:
                    return re.sub( ".*model name.*:", "", line,1)
        return ""

    @staticmethod
    def _bytes_to_gb(ibytes):
        return round(ibytes / (1024 ** 3), 2)

    def run_tests(self):
        results = {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'uptime': self.get_uptime(),
            'machine': platform.machine(),
            'processor': self.get_processor_name(),
            'architecture': platform.architecture(),
            'wsl': self._check_for_wsl(),
            'distro': "N/A (can't detect linux)"}
        results['os_version_supported'] = 'no'
        if results['system'] == 'Linux':
            results['distro'] = ' '.join(distro.linux_distribution())
            if results['wsl'] is False:
                if f'Ubuntu {self.ACCEPTABLE_OS_VERSION}' in results['distro']:
                    results['os_version_supported'] = 'yes'
                elif f'Ubuntu {self.WANRING_OS_VERSION}' in results['distro']:
                    results['os_version_supported'] = 'warning'
            else:
                results['os_version_supported'] = 'wsl'
        if self.ACCEPTABLE_CPU_STRING.lower() in results['processor'].lower():
            results['acceptable_processor'] = 'yes'
        else:
            results['acceptable_processor'] = 'no'
        results['disk_space_stats'] = shutil.disk_usage('/')
        results['total_disk_space_gb'] = self._bytes_to_gb(results['disk_space_stats'].total)
        results['free_disk_space_gb'] = self._bytes_to_gb(results['disk_space_stats'].free)
        results['used_disk_space_gb'] = self._bytes_to_gb(results['disk_space_stats'].used)
        return results

    @staticmethod
    def _check_if_in_container():
        return os.path.exists('/.dockerenv')

    @staticmethod
    def _check_for_wsl():
        microsoft_in_proc_version = subprocess.run(['grep',
                                                    '-iq',
                                                    'microsoft',
                                                    '/proc/version'],
                                                    shell=False,
                                                    check=False).returncode == 0
        wsl_in_proc_version = subprocess.run(['grep',
                                              '-iq',
                                              'wsl',
                                              '/proc/version'],
                                              shell=False,
                                              check=False).returncode == 0
        return microsoft_in_proc_version and wsl_in_proc_version

    @staticmethod
    def print_results(results, extended_info=True):
        print("System information:")

        distro_color = bcolors.FAIL
        if results['os_version_supported'] == 'yes':
            distro_color = bcolors.OKGREEN
        elif results['os_version_supported'] == 'warning':
            distro_color = bcolors.WARNING

        proc_color = bcolors.WARNING
        if results['acceptable_processor'] == 'yes':
            proc_color = bcolors.OKGREEN

        uptime_color = bcolors.WARNING
        if results['uptime'] < GetSystemInfo.ACCEPTABLE_UPTIME_SECONDS:
            uptime_color = bcolors.OKGREEN

        if GetSystemInfo._check_if_in_container():
            print(f"{bcolors.FAIL}  Found /.dockerenv file. Running in a container. Please don't do that"
                  f"{bcolors.ENDC}")

        if results['wsl']:
            print(f"{bcolors.FAIL}  Running in Windows Subsystem for Linux (WSL). This is not supported"
                  f"{bcolors.ENDC}")

        print(f"{distro_color}  Linux distribution: {results['distro']}{bcolors.ENDC}")
        print(f"  Release: {results['release']}")
        print(f"{proc_color}  Processor: {results['processor']}{bcolors.ENDC}")
        uptime_days = round((results['uptime'] / (60 * 60 * 24)), 2)
        print(f"{uptime_color}  Uptime: {results['uptime']} seconds ({uptime_days} days){bcolors.ENDC}")
        if uptime_days > GetSystemInfo.ACCEPTABLE_UPTIME_HOURS / 24:
            print(f"{bcolors.WARNING}  Uptime is above {GetSystemInfo.ACCEPTABLE_UPTIME_HOURS} hours. "
                  f"Please consider rebooting{bcolors.ENDC}")
        disk_space_color = bcolors.OKGREEN
        if results['free_disk_space_gb'] < GetSystemInfo.ACCEPTABLE_FREE_DISK_SPACE_GB:
            disk_space_color = bcolors.WARNING
            print(f"{bcolors.FAIL}  Free disk space is below {GetSystemInfo.ACCEPTABLE_FREE_DISK_SPACE_GB} GB. "
                  f"Please free up space{bcolors.ENDC}")
        print(f"{disk_space_color}  Free disk space: {results['free_disk_space_gb']} GB")

        if extended_info:
            print(f"{disk_space_color}  Total disk space: {results['total_disk_space_gb']} GB")
            print(f"  Used disk space: {results['used_disk_space_gb']} GB{bcolors.ENDC}")
            print(f"  System: {results['system']}")
            print(f"  Version: {results['version']}")
            print(f"  Machine: {results['machine']}")
            print(f"  Architecture: {results['architecture']}")
        print('')


class GetNvidiaInfo:
    ACCEPTABLE_DRIVER_VERSIONS = ['535.183.x']

    @staticmethod
    def _detect_gpu():
        command = ['lspci']
        output, return_code = GetNvidiaInfo._get_utf8_output(command, shell=True)
        if return_code != 0:
            print(f"{bcolors.FAIL}Could not use lspci to detect Nvidia GPU. Are you in a container?{bcolors.ENDC}")
            return False
        for line in output.split('\n'):
            if 'NVIDIA' in line.upper() and 'VGA' in line.upper():
                return True
        return False

    @staticmethod
    def _detect_nvidia_smi():
        command = ['which', 'nvidia-smi']
        output, return_code = GetNvidiaInfo._get_utf8_output(command, shell=False)
        if return_code != 0:
            return False
        if 'nvidia' in output:
            return True
        return False

    @staticmethod
    def _get_utf8_output(command, shell=False):
        proc = subprocess.run(command, shell=shell, capture_output=True, check=False)
        return proc.stdout.decode('utf-8'), proc.returncode

    @staticmethod
    def _get_info_if_available(command):
        output, return_code = GetNvidiaInfo._get_utf8_output(command)
        if return_code == 0:
            return output.strip('\n')
        return False

    @staticmethod
    def _check_nvidia_smi():
        command = ['nvidia-smi']
        proc = subprocess.run(command, capture_output=True, check=False)
        if proc.returncode == 0:
            return True
        return False

    @staticmethod
    def _strip_patch_version(version):
        return '.'.join(version.split('.')[:2])

    def _compare_driver_versions(self, detected_version):
        for driver_version in self.ACCEPTABLE_DRIVER_VERSIONS:
            if 'x' in driver_version:
                driver_version = driver_version.replace('x', '').strip('.')

                if detected_version.count('.') > 2:
                    detected_version = self._strip_patch_version(detected_version)

            if driver_version in detected_version:
                return True
        return False

    def run_tests(self):
        results = {}
        results['nvidia_gpu_detected'] = self._detect_gpu()
        results['nvidia_smi_found'] = self._detect_nvidia_smi()
        results['nvidia_smi_working'] = self._get_info_if_available(['nvidia-smi'])
        results['gpu_name'] = self._get_info_if_available(['nvidia-smi',
                                                           '--query-gpu=gpu_name',
                                                           '--format=csv,noheader'])
        results['driver_version'] = self._get_info_if_available(['nvidia-smi',
                                                                 '--query-gpu=driver_version',
                                                                 '--format=csv,noheader'])
        return results

    def print_results(self, results, extended_info=True):
        if results['nvidia_gpu_detected'] is False:
            print("No Nvidia GPU detected.")
            return
        if results['nvidia_smi_found'] is False:
            print(f"{bcolors.WARNING}Nvidia GPU detected but nvidia-smi not found. Have you installed the nvidia "
                  f"driver?{bcolors.ENDC}")
            return
        if results['nvidia_smi_working'] is False:
            print(f"{bcolors.FAIL}Nvidia GPU detected but nvidia-smi not working. Is your driver installed correctly?"
                  f"{bcolors.ENDC}")
            return
        print("Nvidia GPU information:")
        print(f"  GPU name: {results['gpu_name']}")
        out_color = bcolors.WARNING
        if self._compare_driver_versions(results['driver_version']):
            out_color = bcolors.OKGREEN
        print(f"{out_color}  Driver version: {results['driver_version']}{bcolors.ENDC}")
        if extended_info:
            print("  Nvidia-smi output: \n")
            for line in results['nvidia_smi_working'].split('\n'):
                print(f"    {line}")
        print('')


class DeploymentTest:
    PING_TEST_URLS = {'google': 'google.com', 'docker': 'download.docker.com'}
    WGET_TEST_URLS = {'libnvidia_container_gpg_key': 'https://nvidia.github.io/libnvidia-container/gpgkey'}
    GIT_CLONE_TEST_URLS = {'sr_interface': 'http://github.com/shadow-robot/sr_interface'}
    def __init__(self, tests_to_run=None):
        self._test_instances_dict = {
            'system_info': GetSystemInfo(),
            'nvidia_info': GetNvidiaInfo(),
            'ping': PingTest(self.PING_TEST_URLS),
            'wget': WgetTest(self.WGET_TEST_URLS),
            'speed_test': SpeedTest(),
            'git_clone': GitCloneTest(self.GIT_CLONE_TEST_URLS)}
        if tests_to_run:
            self.tests_to_run = tests_to_run
        else:
            self.tests_to_run = self._test_instances_dict.keys()

        self.results = {}
        self._run_all_tests()

    def _run_all_tests(self):
        for test_name, test_class in self._test_instances_dict.items():
            if test_name in self.tests_to_run:
                self.results[test_name] = test_class.run_tests()
                test_class.print_results(self.results[test_name])
        print('\n\nResults summary:\n')  # newlines
        for test_name, test_class in self._test_instances_dict.items():
            if test_name in self.tests_to_run:
                if 'extended_info' in str(inspect.signature(test_class.print_results)):
                    test_class.print_results(self.results[test_name], extended_info=False)
                else:
                    test_class.print_results(self.results[test_name])
                print(f"{bcolors.ENDC}", end='')


if __name__ == "__main__":
    deployment_test = DeploymentTest()


# # spit into file
# # recent oneliners?
# # host python packages
# # any other apt sources (apt linux, nvidia etc..)
