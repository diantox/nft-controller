#!/usr/bin/env bash

# Utility Functions ------------------------------------------------------------

# Usage: readEnv <file>
# Read environment variables from a file.
readEnv() {
  set -a
  . "${1}"
  set +a
}

# Usage: log <message>
# Log a message.
log() {
  printf "%s\n" "${1}"
}

# Usage: warning <warning_message>
# Log a warning message.
warning() {
  printf "\e[33m%s\e[m\n" "${1}"
}

# Usage: error <error_message>
# Log an error message.
error() {
  printf "\e[31m%s\e[m\n" "${1}"
}

# Usage: findFiles <directory> <extension>
# Find files in a directory with an extension.
findFiles() {
  find -path "${1}/**${2}" -type f
}

# Usage: <command> | findChangedFiles
# Find changed files.
findChangedFiles() {
  while read file; do

    # If the file isn't a sum file (its extension isn't .sum), get its sum file.
    local sum_file=''
    if [[ "${file}" != *.sum ]]; then
      sum_file="${file}.sum"
   
    # If the file is a sum file (their extension is .sum), get its file.
    else
      sum_file="${file}"
      file="${file::-4}"
    fi

    # If the sum file doesn't match its file, log the file.
    sha256sum -c --status "${sum_file}" &> /dev/null
    [[ "${?}" -eq 1 ]] && log "${file}"
  done
}

# Usage: <command> | copyFiles
# Copy files to a pyboard and update their sum files.
copyFiles() {
  while read file; do

    # If the file isn't a sum file (its extension isn't .sum), get its sum file.
    local sum_file=''
    if [[ "${file}" != *.sum ]]; then
      sum_file="${file}.sum"
   
    # If the file is a sum file (its extension is .sum), get its file.
    else
      sum_file="${file}"
      file="${file::-4}"
    fi

    # Get the remote file and its directory.
    local remote_file="$(realpath --relative-to=./src ${file})"
    local remote_directory="$(dirname ${remote_file})"

    # If the remote directory isn't a root directory (isn't / or .), create the
    # remote directory.
    if [[ "${remote_directory}" != '/' && "${remote_directory}" != '.' ]]; then
      ampy mkdir --exists-okay "${remote_directory}"
    fi

    # Copy the file to the remote file, update its sum file, and log the file. 
    ampy put "${file}" "${remote_file}"
    sha256sum "${file}" > "${sum_file}"
    log "${file}"
  done
}

# Usage: <command> | removeFiles
# Remove files from a pyboard and remove their sumfiles.
removeFiles() {
  while read file; do

    # If the file isn't a sum file (its extension isn't .sum), get its sum file.
    local sum_file=''
    if [[ "${file}" != *.sum ]]; then
      sum_file="${file}.sum"
   
    # If the file is a sum file (its extension is .sum), get its file.
    else
      sum_file="${file}"
      file="${file::-4}"
    fi

    # Get the directory, remote file, and its directory.
    local directory="$(dirname ${file})"
    local remote_file="$(realpath --relative-to=./src ${file})"
    local remote_directory="$(dirname ${remote_file})"

    # Remove the sum file and remote file.
    # rm -f "${file}"
    rm -f "${sum_file}"
    ampy rm "${remote_file}"

    # If the remote directory isn't a root directory (isn't / or .) and the
    # directory is empty, remove the remote directory.
    if [[ "${remote_directory}" != '/' && "${remote_directory}" != '.' && -z "$(ls -A ${directory})" ]]; then
      ampy rm "${remote_directory}"
    fi

    # Log the file.
    log "${file}"
  done
}

# Usage: <command> | logFiles <message> <no_files_warning_message>
# Log files with a message, or a warning message with no files.
logFiles() {
  read -a files -d ''
  if [[ ${#files[@]} -gt 0 ]]; then
    for file in "${files[@]}"; do
      log "${1} ${file}"
    done
  else
    warning "${2}"
  fi
}

# Main Functions ---------------------------------------------------------------

# Usage: help
# Log help.
help() {
  log "Usage $(basename ${0}) [options]"
  log '  -h Log help.'
  log '  -d Detect and save a pyboard.'
  log '  -c Copy changed files to a pyboard.'
  log "  -C Connect to a pyboard's REPL."
}

# Usage: detectPyboard
# Detect and save a pyboard.
detectPyboard() {

  # Print TTY devices with the pyboard disconnected to
  # ./pyboard_disconnected_tty_devices
  read -n 1 -p 'Disconnect the pyboard and press any key.' -s; log ''
  ls -1 /dev | grep -i 'tty' > ./pyboard_disconnected_tty_devices

  # Print TTY devices with the pyboard connected to
  # ./pyboard_connected_tty_devices
  read -n 1 -p 'Connect the pyboard and press any key.' -s; log ''
  ls -1 /dev | grep -i 'tty' > ./pyboard_connected_tty_devices

  # Print TTY devices in ./pyboard_connected_tty_devices but not in
  # ./pyboard_disconnected_tty_devices to ./new_tty_devices
  comm -13 ./pyboard_disconnected_tty_devices ./pyboard_connected_tty_devices >\
    ./new_tty_devices
  
  # Get the number of new TTY devices.
  local num_new_tty_devices="$(cat ./new_tty_devices | wc -l)"

  # If there's no new TTY devices, quit.
  local new_tty_device
  if [[ "${num_new_tty_devices}" -eq 0 ]]; then
    error 'Found no new devices.'
    log 'Quitting.'
    exit 1

  # If there's one new TTY device, continue.
  elif [[ "${num_new_tty_devices}" -eq 1 ]]; then
    log 'Found a new device.'
    new_tty_device="$(cat ./new_tty_devices)"

  # If there's more than one new TTY device, quit.
  elif [[ "${num_new_tty_devices}" -gt 1 ]]; then
    error "Found ${num_new_tty_devices} new devices."
    log 'Quitting.'
    exit 1
  fi

  # Get the new TTY device's speed.
  local new_tty_device_speed="$(stty -F /dev/${new_tty_device} speed)"

  # Save the new TTY device to ./envs/pyboard.env
  log 'Saving the new device.'
  log "AMPY_PORT=/dev/${new_tty_device}" > ./envs/pyboard.env
  log "AMPY_BAUD=115200" >> ./envs/pyboard.env
  # log "AMPY_BAUD=${new_tty_device_speed}" >> ./envs/pyboard.env

  # Remove ./new_tty_devices, ./pyboard_connected_devices, and
  # ./pyboard_disconnected_devices
  rm ./new_tty_devices ./pyboard_connected_tty_devices \
    ./pyboard_disconnected_tty_devices
}

# Usage: copyChangedFilesToPyboard
# Copy changed files to, and remove deleted files from a pyboard.
copyChangedFilesToPyboard() {
  readEnv ./envs/pyboard.env
  log 'Press c to copy changed files to a pyboard and q to quit.'
  local looping=true
  while $looping; do
    read -n 1 -s input
    if [[ "${input}" == 'c' ]]; then
      log 'Copying changed files to a pyboard.'
      findFiles './src' '.py' \
        | findChangedFiles \
        | copyFiles \
        | logFiles 'Copied' 'No changed files.'

      log 'Removing deleted files from a pyboard.'
      findFiles './src' '.sum' \
        | findChangedFiles \
        | removeFiles \
        | logFiles 'Removed' 'No removed files.'

      ampy run -n ./src/main.py

    elif [[ "${input}" == 'q' ]]; then
      log 'Quiting'
      looping=false
    fi
  done
}

# Usage: connectPyboardRepl
# Connect to a pyboard's REPL.
connectPyboardRepl() {
  readEnv ./envs/pyboard.env
  picocom -b "${AMPY_BAUD}" "${AMPY_PORT}"
}

while getopts 'hdcC' option; do
  case "${option}" in
    h)
      help
      ;;
    d)
      detectPyboard
      ;;
    c)
      copyChangedFilesToPyboard
      ;;
    C)
      connectPyboardRepl
      ;;
    *)
      help
      exit 128
      ;;
  esac
done

if [[ -z "${1}" ]]; then
  help
  exit 128
fi
