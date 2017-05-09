# Owner: Steve Ovens
# Date Created: Aug 2015
# Primary Function: This is a file intended to be supporting functions in various scripts
# This file will do nothing if run directly

import sys

class textColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    HIGHLIGHT = '\033[96m'


class ImportHelper:

    """ This class simply allows for the dynamic loading of modules which are not apart of the stdlib.
     It specifies which module cannot be imported and provides the proper pip install command as output to the user.
    """

    @staticmethod
    def import_error_handling(import_this_module, modulescope):
        try:
            exec("import %s " % import_this_module) in modulescope
        except ImportError:
            print("This program requires %s in order to run. Please run" % import_this_module)
            print("pip install %s" % import_this_module)
            print("To install the missing component")
            sys.exit()


class DictionaryHandling:

    """ This class handles the adding to and output formatting of dictionaries
    """

    @staticmethod
    def add_to_dictionary(dictionary, name_of_server, component, value):
        if name_of_server in dictionary:
            dictionary[name_of_server][component] = value
        else:
            dictionary[name_of_server] = {component: value}

    @staticmethod
    def format_output(text_to_print):
        # Generally if something is False, I want it to be a RED error, but the below list includes headings which
        # are not fatal, and should be treated as warnings only
        warning_heading_list = ["ETCD", "Docker Running", "Docker Enabled", "sum", "available"]

        # This is a hack because I am assuming I have nothing outside of the stdlib available
        longest_line = 0
        for line in text_to_print.split("\n"):
            if line.strip():
                server_name = line.split()[0]
                line_without_server = line.replace("%s " % server_name, "")
                heading = line_without_server.split(": ")[0] + ":"
                if len(heading) > longest_line:
                    longest_line = len(heading)
        previous_heading = ""

        for line_second_pass in text_to_print.split("\n"):
            if line_second_pass.strip():
                server_name = line_second_pass.split()[0]
                value = line_second_pass.split(": ")[1]
                heading = " ".join(line_second_pass.split()[1:]).split(": ")[0] + ":"
                while len(heading) < longest_line:
                    heading += " "
                # Only print the server name once
                if previous_heading != server_name:
                    print("\n\t" + textColors.OKBLUE + server_name + textColors.ENDC)
                previous_heading = server_name
                # All dictionaries should have either True or False in order to be colourized
                # True will be coloured Green, False will be Red. Anything else will be highlighted
                if "False" in value or "None" in value:
                    if any(word in heading for word in warning_heading_list):
                        print(textColors.WARNING),
                    else:
                        print(textColors.FAIL),
                elif "True" in value or "on" in value:
                    if "docker-storage" in heading:
                        print(textColors.WARNING),
                    else:
                        print(textColors.OKGREEN),
                # If the file has been modified mark it yellow as we cannot know whether it is correctly
                # modified or not
                elif any(word in heading for word in warning_heading_list) or "off" in value:
                    print(textColors.WARNING),
                print("\t\t" + heading + "\t" + value)
                print(textColors.ENDC),

    @staticmethod
    def format_dictionary_output(*args):
        temporary_dict = {}
        temp_list = []

        # This populates a temporary dictionary with the contents of all the dictionaries that have been passed in
        # as arguments
        for count, incoming_dictionary in enumerate(args):
            for server_name in incoming_dictionary.keys():
                for component_key in incoming_dictionary[server_name]:
                    DictionaryHandling.add_to_dictionary(temporary_dict, server_name, component_key,
                                                         incoming_dictionary[server_name][component_key])

        # This section prints the server name as a heading in the output
        for server_name in temporary_dict.keys():
            for incoming_dictionary in temporary_dict[server_name]:
                # Turn the dictionaries into a list so that I can sort the output
                temp_var = server_name + " " + incoming_dictionary + " : " + \
                           str(temporary_dict[server_name][incoming_dictionary])
                temp_list.append(temp_var)
            temp_list.sort()

        DictionaryHandling.format_output("\n".join(temp_list))