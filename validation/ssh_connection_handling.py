# Owner: Steve Ovens
# Date Created: July 2015
# Primary Function: This is an ssh connection handler to be imported by any script requiring remote access.
# It will do nothing if called directly.
# Dependencies: helper_functions.py

class HandleSSHConnections:
    """This class allows for easier multiple connections. It also handles running remote commands """
    from helper_functions import ImportHelper
    ImportHelper.import_error_handling("paramiko", globals())
    ImportHelper.import_error_handling("time", globals())

    def __init__(self):
        self.ssh = paramiko.SSHClient()

    def open_ssh(self, server, user_name):
        if not self.ssh_is_connected():
            self.ssh.load_system_host_keys()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(server, username=user_name, timeout=120)
            self.transport = self.ssh.get_transport()
            self.psuedo_tty = self.transport.open_session()
            self.psuedo_tty.get_pty()
            self.read_tty = self.psuedo_tty.makefile()

    def close_ssh(self):
        if self.ssh_is_connected():
            self.read_tty.close()
            self.psuedo_tty.close()
            self.ssh.close()
            time.sleep(2)

    def ssh_is_connected(self):
        transport = self.ssh.get_transport() if self.ssh else None
        return transport and transport.is_active()

    @staticmethod
    def run_remote_commands(ssh_object, command):
        stdin, stdout, stderr = ssh_object.ssh.exec_command(command)
        temp_list = stdout.readlines()
        return(temp_list)