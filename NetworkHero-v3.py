from netmiko import ConnectHandler
from datetime import datetime
import time
import os

class DeviceManager:
    def __init__(self, host, username, password):
        self.switch = {
            'device_type': 'cisco_ios',
            'host': host,
            'username': username,
            'password': password,
        }
        self.net_connect = None
        self.hostname = None

    def connect(self):
        print("Establishing SSH connection...")
        self.net_connect = ConnectHandler(**self.switch)
        time.sleep(2)  # Simulating connection time

        print("Entering enable mode...")
        self.net_connect.enable()
        time.sleep(1)  # Simulating enable mode entry

        print("Disabling paging...")
        self.net_connect.send_command("terminal length 0")

        self.hostname = self.net_connect.find_prompt().strip('#')

    def disconnect(self):
        if self.net_connect:
            self.net_connect.disconnect()
            print("SSH connection closed.")

    def execute_command(self, command):
        return self.net_connect.send_command(command)

class FileManager:
    @staticmethod
    def save_to_file(content, filename):
        os.makedirs('output', exist_ok=True)
        filepath = os.path.join('output', filename)
        with open(filepath, 'w') as file:
            file.write(content)
        print(f"Output saved to {filepath}")

    @staticmethod
    def get_filename(hostname):
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"{hostname}_{current_time}.txt"

class MenuManager:
    def __init__(self, device_manager):
        self.device_manager = device_manager
        self.commands = {
            'A': ("Show Version", "show version"),
            'B': ("Show Interface Status", "show interface status | ex down"),
            'C': ("Show Transceivers", "show interface transceiver"),
            'D': ("Show Recent Logs", "show logging")
        }

    def display_main_menu(self):
        while True:
            print("\nMain Menu:")
            print("1) FSOS")
            print("2) Cisco IOS")
            print("3) Cisco NX-OS")
            print("4) Exit")

            choice = input("Enter your choice (1-4): ")

            if choice in ['1', '2', '3']:
                device_types = {
                    '1': "FSOS",
                    '2': "Cisco IOS",
                    '3': "Cisco NX-OS"
                }
                self.device_menu(device_types[choice])
            elif choice == '4':
                break
            else:
                print("Invalid choice. Please try again.")

    def device_menu(self, device_type):
        while True:
            print(f"\n{device_type} Menu:")
            for key, (description, _) in self.commands.items():
                print(f"{key}) {description}")
            print("E) Run all previous commands and Save output to file")
            print("F) Return to Main Menu")

            choice = input("Enter your choice (A-F): ").upper()

            if choice in self.commands:
                self.submenu(self.commands[choice][1])
            elif choice == 'E':
                self.run_all_commands()
            elif choice == 'F':
                break
            else:
                print("Invalid choice. Please try again.")

    def submenu(self, command):
        while True:
            print(f"\nSubmenu for '{command}':")
            print("1) Display on screen")
            print("2) Save to file")
            print("3) Return to Previous Menu")

            choice = input("Enter your choice (1-3): ")

            if choice == '1':
                output = self.device_manager.execute_command(command)
                print(f"\nOutput of '{command}':\n")
                print(output)
            elif choice == '2':
                output = self.device_manager.execute_command(command)
                filename = FileManager.get_filename(self.device_manager.hostname)
                FileManager.save_to_file(output, filename)
            elif choice == '3':
                break
            else:
                print("Invalid choice. Please try again.")

    def run_all_commands(self):
        output = ""
        for description, cmd in self.commands.values():
            output += f"\n\n--- {description} ---\n"
            output += self.device_manager.execute_command(cmd)
        
        filename = FileManager.get_filename(self.device_manager.hostname)
        FileManager.save_to_file(output, filename)

def main():
    try:
        host = input("Enter the IP address of the switch: ")
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        device_manager = DeviceManager(host, username, password)
        device_manager.connect()

        menu_manager = MenuManager(device_manager)
        menu_manager.display_main_menu()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'device_manager' in locals():
            device_manager.disconnect()

if __name__ == "__main__":
    main()