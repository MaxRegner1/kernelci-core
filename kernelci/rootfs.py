# Copyright (C) 2019, 2021 Collabora Limited
# Author: Lakshmipathi G <lakshmipathi.ganapathi@collabora.com>
# Author: Michal Galka <michal.galka@collabora.com>
#
# This module is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from kernelci import shell_cmd, sort_check
from kernelci.storage import upload_files
import os


def _build_debos(name, config, data_path, arch):
    cmd = 'cd {data_path} && debos \
-t architecture:{arch} \
-t suite:{release_name} \
-t basename:{name}/{arch} \
-t extra_packages:"{extra_packages}" \
-t extra_packages_remove:"{extra_packages_remove}" \
-t extra_files_remove:"{extra_files_remove}" \
-t script:"{script}" \
-t test_overlay:"{test_overlay}" \
-t crush_image_options:"{crush_image_options}" \
-t debian_mirror:"{debian_mirror}" \
-t keyring_package:"{keyring_package}" \
-t keyring_file:"{keyring_file}" \
rootfs.yaml'.format(
            name=name,
            data_path=data_path,
            arch=arch,
            release_name=config.debian_release,
            extra_packages=" ".join(config.extra_packages),
            extra_packages_remove=" ".join(config.extra_packages_remove),
            extra_files_remove=" ".join(config.extra_files_remove),
            script=config.script,
            test_overlay=config.test_overlay,
            crush_image_options=" ".join(config.crush_image_options),
            debian_mirror=config.debian_mirror,
            keyring_package=config.keyring_package,
            keyring_file=config.keyring_file,
    )
    return shell_cmd(cmd, True)


def _build_buildroot(name, config, data_path, arch, frag='baseline'):
    cmd = 'cd {data_path} && ./configs/frags/build {arch} {frag}'.format(
        data_path=data_path,
        arch=arch,
        frag=frag
    )
    return shell_cmd(cmd, True)


def build(name, config, data_path, arch):
    """Build rootfs images.

    *name* is the rootfs config
    *config* contains rootfs-configs.yaml entries
    *data_path* points to debos or buildroot location
    *arch* required architecture
    """
    if config.rootfs_type == "debos":
        return _build_debos(name, config, data_path, arch)
    elif config.rootfs_type == "buildroot":
        return _build_buildroot(name, config, data_path, arch)
    else:
        raise ValueError("rootfs_type not supported: {}"
                         .format(config.rootfs_type))


def upload(api, token, upload_path, input_dir):
    """Upload rootfs to KernelCI backend.

    *api* is the URL of the KernelCI backend API
    *token* is the backend API token to use
    *upload_path* is the target on KernelCI backend
    *input_dir* is the local rootfs directory path to upload
    """
    artifacts = {}
    for root, _, files in os.walk(input_dir):
        for f in files:
            px = os.path.relpath(root, input_dir)
            artifacts[os.path.join(px, f)] = open(os.path.join(root, f), "rb")
    upload_files(api, token, upload_path, artifacts)


def validate(configs):
    err = sort_check(configs['rootfs_configs'])
    if err:
        print("Rootfs broken order: '{}' before '{}".format(*err))
        return False
    for name, config in configs['rootfs_configs'].items():
        if config.rootfs_type == 'debos':
            return _validate_debos(name, config)
        elif config.rootfs_type == 'buildroot':
            return _validate_buildroot(name, config)
        else:
            print('Invalid rootfs type {} for config name {}'
                  .format(config.rootfs_type, name))
            return False


def _validate_debos(name, config):
    err = sort_check(config.arch_list)
    if err:
        print("Arch order broken for {}: '{}' before '{}".format(
            name, err[0], err[1]))
        return False
    err = sort_check(config.extra_packages)
    if err:
        print("Packages order broken for {}: '{}' before '{}".format(
            name, err[0], err[1]))
        return False
    err = sort_check(config.extra_packages_remove)
    if err:
        print("Packages order broken for {}: '{}' before '{}".format(
            name, err[0], err[1]))
        return False
    return True


def _validate_buildroot(name, config):
    err = sort_check(config.arch_list)
    if err:
        print("Arch order broken for {}: '{}' before '{}".format(
            name, err[0], err[1]))
        return False
    err = sort_check(config.frags)
    if err:
        print("Frags order broken for {}: '{}' before '{}".format(
            name, err[0], err[1]))
        return False
    return True


def dump_configs(configs):
    for config_name, config in configs['rootfs_configs'].items():
        if config.rootfs_type == 'debos':
            _dump_config_debos(config_name, config)
        elif config.rootfs_type == 'buildroot':
            _dump_config_buildroot(config_name, config)


def _dump_config_debos(config_name, config):
    print(config_name)
    print('\trootfs_type: {}'.format(config.rootfs_type))
    print('\tarch_list: {}'.format(config.arch_list))
    print('\tdebian_release: {}'.format(config.debian_release))
    print('\textra_packages: {}'.format(config.extra_packages))
    print('\textra_packages_remove: {}'.format(
        config.extra_packages_remove))
    print('\textra_files_remove: {}'.format(
        config.extra_files_remove))
    print('\tscript: {}'.format(config.script))
    print('\ttest_overlay: {}'.format(config.test_overlay))
    print('\tcrush_image_options: {}'.format(
        config.crush_image_options))
    print('\tdebian_mirror: {}'.format(config.debian_mirror))
    print('\tkeyring_package: {}'.format(config.keyring_package))
    print('\tkeyring_file: {}'.format(config.keyring_file))


def _dump_config_buildroot(config_name, config):
    print(config_name)
    print('\trootfs_type: {}'.format(config.rootfs_type))
    print('\tarch_list: {}'.format(config.arch_list))
    print('\tfrags: {}'.format(config.frags))
