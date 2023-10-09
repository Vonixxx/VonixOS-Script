###########
# VonixOS #
########################################
# Automated Installation Script (Main) #
########################################
import os
import shutil
import subprocess
from functions import *

#####################
# Disk Manipulation #
#####################
printSectionTitle("Choose Disk from List: <integer>")
selectedDevice = chooseDisk()
if not selectedDevice:
    print("No disk selected. Exiting script.")
    exit()
runCommand(["wipefs", "-a", selectedDevice])
runCommand(["parted", selectedDevice, "mklabel", "gpt"])

##############
# Partitions #
##############
printSectionTitle("Root Partition Size (in GiB): <integer>")
runCommand(["parted", selectedDevice, "mkpart", "boot", "fat32", "1MiB", "513MiB"])
size = input("Enter: ")
endPosition = f"{size}GiB"
runCommand(["parted", selectedDevice, "mkpart", "nixos", "ext4", "515MiB", endPosition])

##############
# Formatting #
##############
runCommand(["parted", selectedDevice, "set", "1", "esp", "on"])
runCommand(["mkfs.vfat", getPartitionName(selectedDevice, 1)])
runCommand(["mkfs.ext4", getPartitionName(selectedDevice, 2)])

############
# Mounting #
############
runCommand(["mount", getPartitionName(selectedDevice, 2),  "/mnt"])
runCommand(["mkdir", "-p", "/mnt/boot"])
runCommand(["mount", getPartitionName(selectedDevice, 1), "/mnt/boot"])

###############################
# Default NixOS Configuration #
###############################
runCommand(["nixos-generate-config", "--root", "/mnt"])

#################################
# Cloning VonixOS Configuration #
#################################
printSectionTitle("Choose Username: <string> and Password (will be hashed): <string>")
user = getUsername()
hashedPassword = getHashedPassword()
runCommand(["git", "clone", "https://github.com/Vonixxx/VonixOS.git", f"/mnt/home/{user}/VonixOS"])

##################################################
# Copying System-Specific Hardware Configuration #
##################################################
printSectionTitle("Locales and Github: <string>")
variables = promptFlakeValues(user, hashedPassword)
updateFlakeFile(variables, user)
printSectionTitle("Choose Host --> Laptop (Sway) or Desktop (KDE or Budgie): <string> (1st letter must be lowercase)")
host = input("Enter: ")
destination = f"/mnt/home/{user}/VonixOS/system/{host}"
shutil.copy2("/mnt/etc/nixos/hardware-configuration.nix", destination)

##############################################
# Adding Swap --> hardware-configuration.nix #
##############################################
printSectionTitle("Swap File Size (16 for 16GB, 8 for 8GB, etc.): <integer>")
hardwareConfiguration = f"{destination}/hardware-configuration.nix"
swapMultiplier = int(input("Enter: "))
content = f'''{{
    device = "/var/swap";
    size   = {swapMultiplier}*1024;
}}'''
with open(hardwareConfiguration, 'r') as file:
    contents = file.read()
contents = contents.replace('swapDevices = [ ];', f'swapDevices = [ {content} ];')
with open(hardwareConfiguration, 'w') as file:
    file.write(contents)

#########################################
# Initialising Flake/NixOS Installation #
#########################################
printSectionTitle("System Installation")
os.system(f"cd /mnt/home/{user}/VonixOS && nixos-install --flake .#{host}; exec $SHELL")
