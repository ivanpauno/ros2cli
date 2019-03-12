# Copyright 2019 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re

from ament_index_python import get_resource
from ament_index_python import has_resource


def get_action_names_and_types(*, node):
    service_names_and_types = node.get_service_names_and_types()
    # Assumption: actions have a hidden 'send_goal' service with the name:
    #    '/<namespace>/<action_name>/_action/send_goal' (18 trailing characters)
    # And the service type has the suffix '_SendGoal' (9 trailing characters)
    action_names_and_types = [
        (name[:-18], [t[:-9] for t in type_with_suffix])
        for (name, type_with_suffix) in service_names_and_types
        if re.match('.*/_action/send_goal$', name)]
    return action_names_and_types


def get_action_names(*, node):
    action_names_and_types = get_action_names_and_types(node=node)
    return [n for (n, t) in action_names_and_types]


def get_action_types(package_name):
    if not has_resource('packages', package_name):
        raise LookupError('Unknown package name')
    try:
        content, _ = get_resource('rosidl_interfaces', package_name)
    except LookupError:
        return []
    interface_names = content.splitlines()
    # TODO(jacobperron) this logic should come from a rosidl related package
    # Only return actions in action folder
    return list(sorted({
        n[7:-7]
        for n in interface_names
        if n.startswith('action/') and n[-7:] in ('.idl', '.action')}))


def get_action_path(package_name, action_name):
    action_types = get_action_types(package_name)
    if action_name not in action_types:
        raise LookupError('Unknown action type')
    prefix_path = has_resource('packages', package_name)
    # TODO(jacobperron) this logic should come from a rosidl related package
    return os.path.join(prefix_path, 'share', package_name, 'action', action_name + '.action')
