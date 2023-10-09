###########
# VonixOS #
#############################################
# Automated Installation Script (Functions) #
#############################################
import re
import getpass
import subprocess

##########
# Titles #
##########
def printSectionTitle(title):
    lineLength = len(title) + 4
    print("\n" + "#" * lineLength)
    print(f"# {title} #")
    print("#" * lineLength + "\n")
####################
# Execute Commands #
####################
def runCommand(command, cwd=None):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Command {command} failed: {result.stderr}")
    return result.stdout
######################
# Print Disk Devices #
######################
def getDiskDevices():
    output = runCommand(["parted", "--list"])
    devices = []
    for line in output.splitlines():
        if "Disk /dev/" in line:
            devices.append(line.split(":")[0].replace("Disk", "").strip())
    return devices
#########################
# Choose Disk from List #
#########################
def chooseDisk():
    devices = getDiskDevices()

    print("Available Disks:")
    for index, device in enumerate(devices, 1):
        print(f"{index}. {device}")

    choice = int(input("Select: "))
    if 1 <= choice <= len(devices):
        selectedDevice = devices[choice-1]
        print(f"You selected: {selectedDevice}")

        print(runCommand(["parted", selectedDevice, "print"]))
        return selectedDevice
    else:
        print("Invalid choice.")
        return None
######################
# Disk Naming Scheme #
######################
def getPartitionName(device, partitionNumber):
    if "nvme" in device:
        return f"{device}p{partitionNumber}"
    else:
        return f"{device}{partitionNumber}"
###################################
# Prompt User to Modify Variables #
###################################
def getUsername():
    username = input("User: ")
    return username

def getHashedPassword():
    password = getpass.getpass(prompt="Password: ")
    hashedPassword = runCommand(["mkpasswd", "-m", "sha-512", password])
    return hashedPassword.strip()

def promptFlakeValues(user, hashedPassword):
    variables = {
        "user": user,
        "password": hashedPassword,
        "githubuser": input("GitHub Username: "),
        "githubemail": input("GitHub E-mail: "),
        "defaultlocale": input("Default Locale: "),
        "extralocale": input("Extra Locale: ")
    }
    return variables

def inputUserValues(contents, key, value):
    pattern = f'({key}\\s*=\\s*")([^"]*)(";)'
    replacement = f'\\1{value}\\3'
    return re.sub(pattern, replacement, contents)

def updateFlakeFile(variables, user):
    with open(f'/mnt/home/{user}/VonixOS/flake.nix', 'r') as file:
        contents = file.read()
    contents = inputUserValues(contents, "user", variables["user"])
    contents = inputUserValues(contents, "password", variables["password"])
    contents = inputUserValues(contents, "githubuser", variables["githubuser"])
    contents = inputUserValues(contents, "githubemail", variables["githubemail"])
    contents = inputUserValues(contents, "defaultlocale", variables["defaultlocale"])
    contents = inputUserValues(contents, "extralocale", variables["extralocale"])
    with open(f'/mnt/home/{user}/VonixOS/flake.nix', 'w') as file:
        file.write(contents)
