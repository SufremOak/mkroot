import argparse
import os
import subprocess
import configparser

def create_rootfs(rootfs_dir, rootfile_path):
    """Creates and configures the root filesystem."""

    # Check if the rootfs directory exists and create it if necessary
    if not os.path.exists(rootfs_dir):
        os.makedirs(rootfs_dir)

    # Execute the rootfile.sh script to configure the rootfs
    try:
        subprocess.run(["/bin/bash", rootfile_path, rootfs_dir], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing rootfile.sh: {e}")
        return False
    return True



def run_chroot(rootfs_dir, config_path):
    """Runs chroot with the specified rootfs and configuration."""

    # Read configuration from root.conf
    config = configparser.ConfigParser()
    config.read(config_path)

    # Get the command or default shell from the configuration
    command = config.get("chroot", "command", fallback="/bin/bash") # default to bash

    # Add basic mounts required by chroot, you likely need more depending on what you want to run in the container
    mounts = [
        ["--bind", "/dev", f"{rootfs_dir}/dev"],
        ["--bind", "/proc", f"{rootfs_dir}/proc"],
        ["--bind", "/sys", f"{rootfs_dir}/sys"], # Essential, otherwise many commands inside chroot won't work.
        # Add other necessary mounts here (e.g., /tmp, /dev/pts, etc.) as needed.
    ]



    chroot_cmd = ["chroot"]
    for mount in mounts:  # Add mount commands dynamically
        chroot_cmd.extend(mount)
    chroot_cmd.extend([rootfs_dir, command])  # Add the rootfs directory and command

    try:

        # Make sure essential directories exist inside chroot (e.g., dev, proc, sys)
        for dir in ["dev", "proc", "sys", "tmp"]:  # Ensure these dirs exist
             os.makedirs(os.path.join(rootfs_dir, dir), exist_ok=True)

        subprocess.run(chroot_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running chroot: {e}")




def main():
    parser = argparse.ArgumentParser(description="Create and run a chroot environment.")
    parser.add_argument("rootfs_dir", help="Path to the root filesystem directory.")
    parser.add_argument("-r", "--rootfile", default="rootfile.sh", help="Path to the rootfs configuration script (default: rootfile.sh).")
    parser.add_argument("-c", "--config", default="root.conf", help="Path to the chroot configuration file (default: root.conf)")

    args = parser.parse_args()

    if create_rootfs(args.rootfs_dir, args.rootfile):  # Only run chroot if rootfs creation was successful.
        run_chroot(args.rootfs_dir, args.config)



if __name__ == "__main__":
    main()
