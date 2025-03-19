# Copyright 2022 Shadow Robot Company Ltd.
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

# pylint: disable=C0103,W0212,E1101
__metaclass__ = type

from ansible import constants as C
from ansible.plugins.callback.default import CallbackModule as CallbackModule_default


class CallbackModule_custom_retry_runner(CallbackModule_default):

    ''''
    This is the default callback interface, which simply prints messages
    to stdout when new callback events are received.
    '''

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'custom_retry_runner'

    def __init__(self):
        self._play = None
        self._last_task_banner = None
        super(CallbackModule_default, self).__init__()

    def v2_runner_on_start(self, host, task):
        pass

    def v2_runner_on_failed(self, result, ignore_errors=False):
        if ignore_errors:
            return
        try:
            task_name = result.task_name or result._task
            msg = f"FAILED: {task_name}"
            if (self._display.verbosity > 2 or '_ansible_verbose_always' in result._result) \
                                    and '_ansible_verbose_override' not in result._result:
                msg += "Result was: %s" % self._dump_results(result._result)
            self._display.display(msg, color=C.COLOR_ERROR)
            
            # Try to show task path if available
            try:
                if hasattr(result._task, '_role') and result._task._role:
                    task_path = result._task._role._role_path
                elif hasattr(result._task, '_ds') and result._task._ds:
                    task_path = result._task._ds._data_source
                else:
                    task_path = None
                
                if task_path:
                    self._display.display(f"Task path: {task_path}", color=C.COLOR_ERROR)
            except Exception:
                # Silently ignore any errors in showing task path
                pass
                
        except Exception as e:
            # Handle any exceptions that might occur during failure reporting
            self._display.display(f"Error reporting failure: {str(e)}", color=C.COLOR_ERROR)

    def v2_runner_retry(self, result):
        try:
            task_name = result.task_name or result._task
            if "pull" in task_name.lower() and "docker" in task_name.lower():
                msg = "Docker image pulling in progress... Message count: "+str(result._result['attempts'])
                if (self._display.verbosity > 2 or '_ansible_verbose_always' in result._result) \
                                        and '_ansible_verbose_override' not in result._result:
                    msg += "Result was: %s" % self._dump_results(result._result)
                self._display.display(msg, color=C.COLOR_DEBUG)
            elif "arp" in task_name.lower() and "mac" in task_name.lower():
                msg = "Waiting for the MAC address of a connected adapter to appear in arp..."
                msg += f"Message count: {result._result['attempts']}"
                if (self._display.verbosity > 2 or '_ansible_verbose_always' in result._result) \
                                        and '_ansible_verbose_override' not in result._result:
                    msg += "Result was: %s" % self._dump_results(result._result)
                self._display.display(msg, color=C.COLOR_DEBUG)
            else:
                retries = result._result['retries'] - result._result['attempts']
                msg = f"FAILED - RETRYING: {task_name} ({retries} retries left)."
                if (self._display.verbosity > 2 or '_ansible_verbose_always' in result._result) \
                                        and '_ansible_verbose_override' not in result._result:
                    msg += "Result was: %s" % self._dump_results(result._result)
                self._display.display(msg, color=C.COLOR_DEBUG)
        except Exception as e:
            # Handle any exceptions that might occur during retry reporting
            self._display.display(f"Error reporting retry: {str(e)}", color=C.COLOR_ERROR)

CallbackModule = CallbackModule_custom_retry_runner
