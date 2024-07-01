#!/usr/bin/env bash

# Copyright 2024 Shadow Robot Company Ltd.
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

conda_ws_name="aurora_conda_ws"
miniconda_install_root="${HOME}/.shadow_miniconda"
miniconda_install_location="${miniconda_install_root}/miniconda"
miniconda_installer="${miniconda_install_root}/miniconda_installer.sh"
miniconda_installer_url="https://repo.anaconda.com/miniconda/Miniconda3-py311_23.5.2-0-Linux-x86_64.sh"
miniconda_checksum="634d76df5e489c44ade4085552b97bebc786d49245ed1a830022b0b406de5817"
packages_download_root="${miniconda_install_root}/aurora_host_packages"

# Some molecule tests install to `/home/...` (no user account)
if [ -z $USER ]; then
  if [ -z $MY_USERNAME ]; then
    HOME='/home'
  fi
fi

re="^Codename:[[:space:]]+(.*)"
while IFS= read -r line; do
    if [[ $line =~ $re ]]; then
        codename="${BASH_REMATCH[1]}"
    fi
done < <(lsb_release -a 2>/dev/null)

# We use this variable to figure out which pip packages to download. Packages for focal work on jammy, but bionic needs its own packages
if [[ $codename == *"jammy"* ]]; then
  codename="focal"
fi

_fetch_conda_installer() {
    mkdir -p $miniconda_install_root
    attempts=1
    while ! $(echo "${miniconda_checksum} ${miniconda_installer}" | sha256sum --status --check); do
    if [[ -f "$miniconda_installer" ]]; then
        rm $miniconda_installer
    fi
    echo "Attempt number ${attempts}: "
    wget -O $miniconda_installer $miniconda_installer_url
    attempts=$(( attempts + 1 ))
    if [[ $(echo $attempts) -gt 3 ]]; then
        echo "Maximim attempts to fetch ${miniconda_installer} failed. Has the checksum changed?"
        echo "  Previously known good checksum: ${miniconda_checksum}"
        echo "  Current checksum:               $(sha256sum $miniconda_installer)"
        exit 0
    fi
    done
}

_fetch_new_files() {
  aws_bucket_url=$1
  aws_bucket_dir=$2
  local_download_dir="${packages_download_root}/${aws_bucket_dir}"

  echo "Fetching ${aws_bucket_dir}..."
  mkdir -p $local_download_dir

  remote_packages=$(curl -Ls ${aws_bucket_url} | xq | grep $aws_bucket_dir | grep 'Key' | sed -r "s/.*${aws_bucket_dir}\///g" | sed -r 's/",//g' | sed -r 's;</Key>;;g')

  echo "remote_packages: ${remote_packages}"

  local_only=$(comm -23 <(ls $local_download_dir | sort) <(for x in $( echo "${remote_packages}"); do echo $x; done | sort))
  remote_only=$(comm -13 <(ls $local_download_dir | sort) <(for x in $( echo "${remote_packages}"); do echo $x; done | sort))

  echo "Packages found locally that are not in the bucket: ${local_only}"
  echo "Packages found in the bucket that we don't have a local copy of: ${remote_only}"

  if [[ $(echo "${local_only}" | wc -c) -gt 1 ]]; then
    echo "Additional downloaded packages detecting, removing them..."
    for local_package in $(echo ${local_only}); do
      echo "  removing: ${local_download_dir}/${local_package}"
      rm ${local_download_dir}/${local_package}
    done
  else
    echo "No additional local packages found, continuing..."
  fi

  if [[ $(echo "${remote_only}" | wc -c) -gt 1 ]]; then
    echo "Remote packages found that we don't have locally, downloading them..."
    for remote_package in $(echo "${remote_only}"); do
      echo "  Downloading: ${remote_package}"
      wget -q --show-progress -O ${local_download_dir}/${remote_package} ${aws_bucket_url}/${aws_bucket_dir}/${remote_package}
      if [[ $(stat --print="%s" ${local_download_dir}/${remote_package}) -eq 0 ]]; then
        echo -e "\n${RED}WARNING! The package ${remote_package} from ${aws_bucket_url}/${aws_bucket_dir}/${remote_package} has downloaded a file of zero bytes! This probably means s3 bucket permissions are wrong and is very likely to cause deployment issues on your system. Please contact shadow directly to get this fixed.${NC}\n"
        rm ${local_download_dir}/${remote_package}
      fi
    done
  fi
}

deploy_conda_installer() {
  _fetch_conda_installer
  bash $miniconda_installer -u -b -p $miniconda_install_location
  if [[ $(echo $PATH  | grep "${miniconda_install_location}/bin" | wc -l) -eq 0 ]]; then
    PATH="${PATH}:${miniconda_install_location}/bin"
    export PATH=${PATH}
  fi
}

create_conda_ws(){
  deploy_conda_installer
  shadow_conda_ws_dir="${miniconda_install_location}/envs/${conda_ws_name}"
  if [ -d "$shadow_conda_ws_dir" ]; then
    rm -rf $shadow_conda_ws_dir
  fi
  ${miniconda_install_location}/bin/conda create -y -n ${conda_ws_name} python=3.8 && source ${miniconda_install_location}/bin/activate ${conda_ws_name}
  python -m pip install yq xq
}

fetch_pip_files(){ _fetch_new_files "http://shadowrobot.aurora-host-packages-${codename}.s3.eu-west-2.amazonaws.com" "pip_packages"; }
fetch_ansible_files() { _fetch_new_files "http://shadowrobot.aurora-host-packages-${codename}.s3.eu-west-2.amazonaws.com" "ansible_collections"; }

install_pip_packages() { ANSIBLE_SKIP_CONFLICT_CHECK=1 python -m pip install ${packages_download_root}/pip_packages/* ; }
install_ansible_collections() {
  ansible_galaxy_executable=$1
  "${ansible_galaxy_executable}" collection install $(realpath ${packages_download_root}/ansible_collections/*)
}
