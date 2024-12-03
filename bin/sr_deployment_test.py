#!/usr/bin/env python3

'''

    can ping google.com

    can ping download.docker.com

    any other apt sources (apt linux, nvidia etc..)

    Anything else we can think of 

    can clone from github

    has appropriate nvida environment
'''

import os
import subprocess
import sys
import threading
import time
import re
from multiprocessing.pool import ThreadPool
from multiprocessing.context import TimeoutError
import speedtest

# class PoolTimeout:
#     def __init__(self):
#         pass

#     def run(self, timeout, funct, args):
#         pool = ThreadPool(processes=1)
#         async_result = pool.apply_async(funct, args)
#         try:
#             return_val = async_result.get(timeout)  # get the return value from your function.
#         except TimeoutError as e:
#             print(f"Function timed out after {timeout} seconds")
#             return_val = 'timeout'
#         return return_val



class BaseUrlTest:
    def __init__(self, name_url_dict):
        self._name_url_dict = name_url_dict
        self.results = {}

    def _loop_test(self, funct, args, success_function, after_test_funct=None, num_retries=5, timeout=5):
        results = {}
        successes = 0
        for i in range(num_retries):
            print(f"Attempt {i+1}..")
            results[i] = funct(*args)
            if success_function(results[i]):
                successes += 1
            if after_test_funct:
                after_test_funct()
            time.sleep(1)
        failures = num_retries - successes
        return self._generate_result(num_retries, successes, failures, results)

    @staticmethod
    def _generate_result(self):
        raise NotImplementedError

    def _run_tests(self):
        pass

    def _generate_result(self):
        pass


class WgetTest(BaseUrlTest):
    def __init__(self, name_url_dict):
        self._timeout = 5
        self._temp_file_name = '/tmp/sr_test_wget_python'
        self._num_retries = 3
        super().__init__(name_url_dict)

    def _run_tests(self):
        for name, url in self._name_url_dict.items():
            args = (url, self._temp_file_name, self._timeout)
            
            def _after_test_funct():
                if os.path.exists(self._temp_file_name):
                    os.remove(self._temp_file_name)

            _after_test_funct()
            print(f"Running {self._num_retries} wget test(s) on {url} with a timeout of {self._timeout}s each test")
            self.results[name] = self._loop_test(self._wget, args, self.success_function, _after_test_funct, num_retries=self._num_retries)
        return self.results

    @staticmethod
    def success_function(result):
        temp_file_path = result.args[3]
        if os.path.getsize(temp_file_path) > 0:
            return True
        return

    @staticmethod
    def _wget(url, output_path, timeout=None):
        command = ['wget', '-O', f'{output_path}', url]
        if timeout:
            command.insert(1, '--timeout=' + str(timeout))
        return subprocess.run(command, capture_output=True)        

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

    def print_results(self, results):
        for name in self._name_url_dict.keys():
            print(f"Wget test results for {name}:")
            result_dict = results[name]
            print(f"  All succeeded: {result_dict['all_succeeded']}")
            print(f"  Total attempts: {result_dict['attempts']}")
            print(f"  Successful attempts: {result_dict['successes']}")
            print(f"  Failed attempts: {result_dict['failures']}\n")


class PingTest(BaseUrlTest):
    def __init__(self, name_url_dict):
        self._num_retries = 3
        super().__init__(name_url_dict)

    @staticmethod
    def success_function(result):
        if result.returncode == 0:
            return True
        return False

    def _run_tests(self):
        for name, url in self._name_url_dict.items():
            args = (url,)
            print(f"Running {self._num_retries} ping test(s) on {url}")
            self.results[name] = self._loop_test(self._ping, args, self.success_function, num_retries=self._num_retries)
        return self.results

    @staticmethod
    def _ping_regex(result):
        # extract all 'time=x.xx ms' from the ping output
        return re.findall(r'time=\d+\.\d+ ms', result.stdout.decode('utf-8'))

    @staticmethod
    def _ping(url, num_pings=4):
        return subprocess.run(['ping', '-c', str(num_pings), url], capture_output=True)

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
        avg_time = sum([time for time_list in numerical_times.values() for time in time_list.values()]) / (repeats * len(numerical_times))
        jitter = max_time - min_time
        return {
            'all_succeeded': all_succeeded,
            'min_time_ms': min_time,
            'max_time_ms': max_time,
            'avg_time_ms': avg_time,
            'jitter_ms': jitter,
            'attempts': repeats,
            'successes': successes,
            'failures': failures}

    def print_results(self, results):
        for name in self._name_url_dict.keys():
            result_dict = results[name]
            print(f"Ping test results for {name}:")
            print(f"  All succeeded: {result_dict['all_succeeded']}")
            print(f"  Min time: {result_dict['min_time_ms']} ms")
            print(f"  Max time: {result_dict['max_time_ms']} ms")
            print(f"  Avg time: {result_dict['avg_time_ms']} ms")
            print(f"  Jitter: {result_dict['jitter_ms']} ms")
            print(f"  Total attempts: {result_dict['attempts']}")
            print(f"  Successful attempts: {result_dict['successes']}")
            print(f"  Failed attempts: {result_dict['failures']}\n")


class GitCloneTest(BaseUrlTest):
    def __init__(self, name_url_dict):
        super().__init__(name_url_dict)
        self._name_url_dict = name_url_dict
        remote_size = self._get_remote_repo_size()
        self._remote_size_real = True
        if remote_size == 'Error':
            remote_size = '88M'
            self._remote_size_real = False
        self._remote_size = remote_size.strip('\n')

    def _get_remote_repo_size(self):
        command = '''
                    curl \
                    -H "Accept: application/vnd.github.v3+json" \
                    -s https://api.github.com/repos/torvalds/linux | \
                    jq '.size' | \
                    numfmt --to=iec --from-unit=1024

                    '''
        response = subprocess.run(command.replace('torvalds', 'shadow-robot').replace('linux', 'sr_interface').replace('\n', ''),
                                  capture_output=True,
                                  shell=True)
        if response.returncode == 0:
            return response.stdout.decode('utf-8')
        return 'Error'

    @staticmethod
    def _after_test_funct():
        if os.path.exists('/tmp/sr_test_git_clone_python'):
            subprocess.run(['rm', '-rf', '/tmp/sr_test_git_clone_python'])

    def _run_tests(self):
        if os.path.exists('/tmp/sr_test_git_clone_python'):
                subprocess.run(['rm', '-rf', '/tmp/sr_test_git_clone_python'])
        for name, url in self._name_url_dict.items():
            print(f"Running git clone test on {url}")
            self.results[name] = self._loop_test(self.git_clone, (url, '/tmp/sr_test_git_clone_python'),
                                                 self.success_function,
                                                 self._after_test_funct,
                                                 num_retries=2)
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
            'remote_size_real': self._remote_size_real,
            'remote_size_estimated': not self._remote_size_real,
            'local_sizes': [result.size for result in results.values()]
        }

    def print_results(self, results):
        for name in self._name_url_dict.keys():
            print(f"Git clone test results for {name}:")
            result_dict = results[name]
            print(f"  All succeeded: {result_dict['all_succeeded']}")
            print(f"  Total attempts: {result_dict['attempts']}")
            print(f"  Successful attempts: {result_dict['successes']}")
            print(f"  Failed attempts: {result_dict['failures']}")
            print(f"  Remote size: {result_dict['remote_size']}")
            if result_dict['remote_size_estimated']:
                print("  Remote size is estimated")
            else:
                print("  Remote size is real")
            print(f"  Local sizes: {result_dict['local_sizes']}\n")

class SpeedTest:
    
    @staticmethod
    def _run_tests():
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
        service_data
        ip_data
        return {
            'ping': ping,
            'upload': uploading,
            'download': downloading,
            'service': service_data,
            'ip': ip_data
        }

    def print_results(self, results):
        print("Results for general internet speed test:")
        print(f"  Ping: {results['ping']} ms")
        print(f"  Upload: {results['upload']} Mbps")
        print(f"  Download: {results['download']} Mbps")
        print(f"  Service provider: {results['service']}")
        print(f"  IP address: {results['ip']}\n")

    def get_results(self):
        return self.results


class DeploymentTest:
    PING_TEST_URLS = {'google': 'google.com', 'docker': 'download.docker.com'} #, 'nvidia': 'nvidia.github.io'}
    WGET_TEST_URLS = {'libnvidia_container_gpg_key': 'https://nvidia.github.io/libnvidia-container/gpgkey'}
    GIT_CLONE_TEST_URLS = {'sr_interface': 'http://github.com/shadow-robot/sr_interface'}
    def __init__(self, tests_to_run=None):
        if tests_to_run:
            self.tests_to_run = tests_to_run
        else:
            self.tests_to_run = ['ping', 'wget', 'speed_test', 'git_clone']
        self._ping_tests = PingTest(self.PING_TEST_URLS)
        self._wget_tests = WgetTest(self.WGET_TEST_URLS)
        self._speed_test = SpeedTest()
        self._git_clone_test = GitCloneTest(self.GIT_CLONE_TEST_URLS)

        self.results = {}
        self._run_all_tests()
        self._print_results()

    def _print_results(self):
        if 'ping' in self.tests_to_run:
            self._ping_tests.print_results(self.results['ping'])
        if 'wget' in self.tests_to_run:
            self._wget_tests.print_results(self.results['wget'])
        if 'speed_test' in self.tests_to_run:
            self._speed_test.print_results(self.results['speed_test'])
        if 'git_clone' in self.tests_to_run:
            self._git_clone_test.print_results(self.results['git_clone'])
        
    def _run_all_tests(self):
        if 'ping' in self.tests_to_run:
            self.results['ping'] = self._ping_tests._run_tests()
        if 'wget' in self.tests_to_run:
            self.results['wget'] = self._wget_tests._run_tests()
        if 'speed_test' in self.tests_to_run:
            self.results['speed_test'] = self._speed_test._run_tests()
        if 'git_clone' in self.tests_to_run:
            self.results['git_clone'] = self._git_clone_test._run_tests()


x = DeploymentTest()
a=1


