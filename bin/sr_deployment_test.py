#!/usr/bin/env python3


import os
import subprocess
import sys
import threading
import time
import re
import speedtest
import platform
import distro
import time
import inspect
import shutil


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class subprocessTimeout:
    def __init__(self):
        pass

    def run(self, timeout, command):
        x = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            y = x.communicate(timeout=timeout)
        except subprocess.TimeoutExpired as e:
            x.kill()
            y = x.communicate()
            return_code = -5
        else:
            return_code = x.returncode
        return subprocess.CompletedProcess(args=command, returncode=return_code, stdout=y[0])


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

    def delete_last_n_lines(self, n):
        "Deletes the last line in the STDOUT"
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
        durs = []
        successes = 0
        print(message_str)
        p = ProgressBar()
        p.start_progress(f"Running {num_retries} tests")
        for i in range(num_retries):
            now = time.monotonic()
            progress_bar_goal = int((i+1) * 100 / num_retries)
            if thread_interp_prog:
                thread, event = p.thread_interpolate_progress(progress_bar_goal, timeout)
                thread.start()
            results[i] = funct(*args)
            if success_function(results[i]):
                successes += 1
            if after_test_funct:
                after_test_funct()
            if not thread_interp_prog:
                p.progress(progress_bar_goal)
            else:
                event.set()
                thread.join()
            time.sleep(1)
            durs.append(time.monotonic() - now)
        p.end_progress()
        p.delete_last_n_lines(2)
        print(message_str.replace("Running", "Finished"))
        failures = num_retries - successes
        return self._generate_result(num_retries, successes, failures, results)

    @staticmethod
    def _generate_result(self, num_retries, successes, failures, results):
        raise NotImplementedError

    def run_tests(self):
        pass

    def _generate_result(self):
        pass


class WgetTest(BaseUrlTest):
    def __init__(self, name_url_dict):
        self._timeout = 45
        self._temp_file_name = '/tmp/sr_test_wget_python'
        self._num_retries = 3
        super().__init__(name_url_dict)

    def run_tests(self):
        total_urls = len(self._name_url_dict)
        for name, url in self._name_url_dict.items():
            args = (url, self._temp_file_name, self._timeout)

            def _after_test_funct():
                if os.path.exists(self._temp_file_name):
                    os.remove(self._temp_file_name)

            _after_test_funct()
            this_url_index = list(self._name_url_dict.keys()).index(name) + 1
            message_str = f"Running {self._num_retries} wget test(s) on {url} with a timeout " \
                          f"of {self._timeout}s each test ({this_url_index}/{total_urls})"
            self.results[name] = self._loop_test(self._wget,
                                                 args,
                                                 self.success_function,
                                                 message_str,
                                                 _after_test_funct,
                                                 timeout=self._timeout,
                                                 num_retries=self._num_retries,
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
        return subprocessTimeout().run(timeout, command)

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
                for k, v in result_dict['results'].items():
                    out_color = bcolors.WARNING
                    if v.returncode == 0:
                        continue
                    print(f"{out_color}Wget test attempt {k+1} output: \n{v.stdout.decode('utf-8')}{bcolors.ENDC}\n")
            print('')


class PingTest(BaseUrlTest):
    def __init__(self, name_url_dict):
        self._num_retries = 3
        self._timeout = 10
        super().__init__(name_url_dict)

    @staticmethod
    def success_function(result):
        return result.returncode == 0

    def run_tests(self):
        total_urls = len(self._name_url_dict)
        for name, url in self._name_url_dict.items():
            args = (url,self._timeout)
            this_url_index = list(self._name_url_dict.keys()).index(name) + 1
            message_str = f"Running {self._num_retries} ping test(s) on {url} with a timeout " \
                          f"of {self._timeout}s each ({this_url_index}/{total_urls})"
            self.results[name] = self._loop_test(self._ping,
                                                 args,
                                                 self.success_function,
                                                 message_str,
                                                 timeout=self._timeout,
                                                 num_retries=self._num_retries,
                                                 thread_interp_prog=True)
        return self.results

    @staticmethod
    def _ping_regex(result):
        # extract all 'time=x.xx ms' from the ping output
        return re.findall(r'time=\d+\.\d+ ms', result.stdout.decode('utf-8'))

    @staticmethod
    def _ping(url, timeout, num_pings=4):
        command = ['ping', '-c', str(num_pings), url]
        return subprocessTimeout().run(timeout, command)

    def _generate_result(self, repeats, successes, failures, results):
        all_succeeded = False
        string_results = {}
        numerical_times = {}
        if successes == repeats:
            all_succeeded = True
        for k, v in results.items():
            string_results[k] = self._ping_regex(v)
        for k, v in string_results.items():
            numerical_times[k] = {}
            for i, time_string in enumerate(v):
                numerical_times[k][i] = float(time_string.split('=')[1].split(' ')[0])
        min_time = min([time for time_list in numerical_times.values() for time in time_list.values()])
        max_time = max([time for time_list in numerical_times.values() for time in time_list.values()])
        avg_time = round(sum([time for time_list in numerical_times.values() for time in time_list.values()]) / 
                         (repeats * len(numerical_times)), 2)
        jitter = round((max_time - min_time), 2)
        return {
            'all_succeeded': all_succeeded,
            'min_time_ms': min_time,
            'max_time_ms': max_time,
            'avg_time_ms': avg_time,
            'jitter_ms': jitter,
            'attempts': repeats,
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
    def __init__(self, name_url_dict):
        super().__init__(name_url_dict)
        self._name_url_dict = name_url_dict
        # remote_size = self._get_remote_repo_size()
        self._timeout = 30
        self._remote_size = '88M'

    def _get_remote_repo_size(self):
        command = '''
                    curl \
                    -H "Accept: application/vnd.github.v3+json" \
                    -s https://api.github.com/repos/torvalds/linux | \
                    jq '.size' | \
                    numfmt --to=iec --from-unit=1024

                    '''
        response = subprocess.run(command.replace('torvalds', 'shadow-robot').replace('linux',
                                                                                      'sr_interface').replace('\n',
                                                                                                              ''),
                                  capture_output=True,
                                  shell=True)
        if response.returncode == 0:
            return response.stdout.decode('utf-8')
        return 'Error'

    @staticmethod
    def _after_test_funct():
        if os.path.exists('/tmp/sr_test_git_clone_python'):
            subprocess.run(['rm', '-rf', '/tmp/sr_test_git_clone_python'])

    def run_tests(self):
        if os.path.exists('/tmp/sr_test_git_clone_python'):
                subprocess.run(['rm', '-rf', '/tmp/sr_test_git_clone_python'])
        for name, url in self._name_url_dict.items():
            message_str = f"Running git clone test on {url} with a timeout of {self._timeout}s"
            self.results[name] = self._loop_test(self.git_clone, (url, '/tmp/sr_test_git_clone_python'),
                                                 self.success_function,
                                                 message_str,
                                                 self._after_test_funct,
                                                 num_retries=2,
                                                 timeout=self._timeout,
                                                 thread_interp_prog=True)
        return self.results

    @staticmethod
    def git_clone(url, local_path):
        clone_command = ['git', 'clone', url, local_path]
        size_command = ['du', '-sh', local_path]
        result = subprocess.run(clone_command, capture_output=True)
        size = subprocess.run(size_command, capture_output=True).stdout.decode('utf-8').split('\t')[0]
        result.size = size
        return result

    def success_function(self, result):
        remote_size = self._remote_size
        cloned_size_int = int(result.size.strip('M'))
        remote_size_int = int(remote_size.strip('\n').strip('M'))
        # if almost equal
        if abs(cloned_size_int - remote_size_int) < 10:
            return True
        return False

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
            'remote_size': self._remote_size,
            #'remote_size_real': self._remote_size_real,
            'remote_size_estimated': True,
            'local_sizes': [result.size for result in results.values()]
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
                print(f"{out_color}", end='')
                print(f"  Remote size: {result_dict['remote_size']}")
                if result_dict['remote_size_estimated']:
                    print("  Remote size is estimated")
                else:
                    print("  Remote size is real")
                print(f"  Local sizes: {result_dict['local_sizes']}\n")
                print(f"{bcolors.ENDC}", end='')


class SpeedTest:
    def __init__(self):
        self._acceptable_download_speed = 20  #Mbps
        self._acceptable_upload_speed = 10  #Mbps
        self._acceptable_ping = 50  #ms

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
        if results['upload'] > self._acceptable_upload_speed:
            up_color = bcolors.OKGREEN

        down_color = bcolors.WARNING
        if results['download'] > self._acceptable_download_speed:
            down_color = bcolors.OKGREEN

        ping_color = bcolors.WARNING
        if results['ping'] < self._acceptable_ping:
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
        with open('/proc/uptime', 'r') as proc:
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
                                                    '/proc/version'], shell=False).returncode == 0
        wsl_in_proc_version = subprocess.run(['grep',
                                              '-iq',
                                              'wsl',
                                              '/proc/version'], shell=False).returncode == 0
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
    def __init__(self):
        self._acceptable_driver_versions = ['535.183.x']

    @staticmethod
    def _detect_gpu():
        command = ['lspci', '|', 'grep', 'VGA', '|', 'grep', '-i', 'nvidia', '|', 'wc', '-l']
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
        proc = subprocess.run(command, shell=shell, capture_output=True)
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
        proc = subprocess.run(command, capture_output=True)
        if proc.returncode == 0:
            return True
        return False

    @staticmethod
    def _strip_patch_version(version):
        return '.'.join(version.split('.')[:2])

    def _compare_driver_versions(self, detected_version):
        for driver_version in self._acceptable_driver_versions:
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
        self._test_classes_dict = {
            'system_info': GetSystemInfo(),
            'nvidia_info': GetNvidiaInfo(),
            'ping': PingTest(self.PING_TEST_URLS),
            'wget': WgetTest(self.WGET_TEST_URLS),
            'speed_test': SpeedTest(),
            'git_clone': GitCloneTest(self.GIT_CLONE_TEST_URLS)}
        if tests_to_run:
            self.tests_to_run = tests_to_run
        else:
            self.tests_to_run = self._test_classes_dict.keys()
        self._ping_tests = PingTest(self.PING_TEST_URLS)
        self._wget_tests = WgetTest(self.WGET_TEST_URLS)
        self._speed_test = SpeedTest()
        self._git_clone_test = GitCloneTest(self.GIT_CLONE_TEST_URLS)
        self._system_info = GetSystemInfo()

        self.results = {}
        self._run_all_tests()

    def _run_all_tests(self):
        for test_name, test_class in self._test_classes_dict.items():
            if test_name in self.tests_to_run:
                self.results[test_name] = test_class.run_tests()
                test_class.print_results(self.results[test_name])
        print('\n\nResults summary:\n')  # newlines
        for test_name, test_class in self._test_classes_dict.items():
            if test_name in self.tests_to_run:
                if 'extended_info' in str(inspect.signature(test_class.print_results)):
                    test_class.print_results(self.results[test_name], extended_info=False)
                else:
                    test_class.print_results(self.results[test_name])
                print(f"{bcolors.ENDC}", end='')




x = DeploymentTest()

# # spit into file
# # recent oneliners?
# # host python packages
# # any other apt sources (apt linux, nvidia etc..)
