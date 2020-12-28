import colorama as cr
import os


class Logger:
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        self.msg_type = {
            'status': cr.Fore.WHITE,
            'success': cr.Style.BRIGHT + cr.Fore.LIGHTGREEN_EX,
            'error': cr.Style.BRIGHT + cr.Fore.LIGHTRED_EX,
            'warning': cr.Style.BRIGHT + cr.Fore.LIGHTYELLOW_EX
        }

        self.reset = cr.Style.RESET_ALL

        log_dir = os.path.dirname(log_file_path)
        if not os.path.exists(log_dir):
            self.error(log_dir + ' directory does not exist. Creating...', write=False)
            os.mkdir(log_dir)
            self.success(log_dir + ' directory created.\n', write=False)

        self.log_file = open(log_file_path, 'w+')

    def to_file(self, msg):
        self.log_file.write(msg + '\n')

    def error(self, msg, write=True):
        print(self.msg_type['error'] + msg + self.reset)
        if write:
            self.to_file('Error:\t' + msg)

    def warning(self, msg, write=True):
        print(self.msg_type['warning'] + msg + self.reset)
        if write:
            self.to_file('Warning:\t' + msg)

    def status(self, msg, write=True):
        print(self.msg_type['status'] + msg + self.reset)
        if write:
            self.to_file(msg)

    def success(self, msg, write=True):
        print(self.msg_type['success'] + msg + self.reset)
        if write:
            self.to_file(msg)

    def info(self, msg, write=True):
        print(self.msg_type['success'] + msg + self.reset)
        if write:
            self.to_file(msg)

    def close(self):
        self.log_file.close()


