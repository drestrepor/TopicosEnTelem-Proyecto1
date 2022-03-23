import time
import os
import json
import base64
import subprocess
import requests
from requests.exceptions import RequestException
import const


def primary_commands(cmd, args):
    # Enter Directory
    if cmd == 'cd':
        try:
            if args:
                if args[0] == '--help' or args[0] == '-h':
                    print('Error Message')
                else:
                    directory = " ".join(args) if len(args) > 1 else args[0]
                    os.chdir(directory)

        except FileNotFoundError as e:
            print(f'cd: {args[0]}: No such file pr directory')
        except TypeError as e:
            print('cd: too many arguments')

    # List files
    elif cmd == "ls":
        params = [s for s in args if s[0] == "-"]
        no_params = [s for s in args if s[0] != "-"]
        args = no_params if len(params) != len(args) else []
        
        hidden = False
        if "-a" in params: hidden = True
        if "--help" in params:
            print('Usage: ls [OPTION]... [FILE]...\nList information about the FILEs (the current directory by default).\n\nMandatory arguments to long options are mandatory for short options too.\n\t-a                  do not ignore entries starting with .\n')
            return

        if len(args) > 1:
            for elem in args:
                try:
                    dirs = os.listdir(elem)
                    print(f'{elem}:')
                    for d in dirs:
                        if d[0] != "." or hidden:
                            print(d, end='\t')
                    print('\n')
                
                except FileNotFoundError as e:
                    print(f'ls: cannot access \'{elem}\': No such file or directory')
        else:
            dirs = os.listdir()
            for d in dirs:
                if d[0] != "." or hidden:
                    print(d, end='  ')
            print('')

            
    elif cmd == "add-phone":
        if not args or len(args) != 2:
            print('Usage: add-phone [key] [value]')
            return
        
        add_phone(args[0], args[1])
    elif cmd == "delete":
        if not args or len(args) != 1:
            print('Usage: delete [key]')
            return

        delete(args[0])
    elif cmd == "show":
        if not args or len(args) != 1:
            print('Usage: show [key]')
            return

        show(args[0])
    else:
        print(f'{cmd}: command not found')


def add_phone(key, value):
    
    try:

        # Test connection
        #test_connection(constants.SERVER_URL, const.MOISES_PORT)

        
        data = json.dumps({ 'key': key, 'value': value })

        r = requests.post(
            f'{const.SERVER_URL}:{const.SERVER_PORT}/phones/create',
            data=data,
            headers={ 'content-type': 'application/json' }
        )


        if ('error' in json.loads(r.text)):
            raise ConnectionAbortedError
        
        print()
    
    
    except Exception as err:
        print(f'{err}')


def delete(key):
    
    try:

        # Test connection
        #test_connection(constants.SERVER_URL, const.MOISES_PORT)

        
        data = json.dumps({ 'key': key })

        r = requests.post(
            f'{const.SERVER_URL}:{const.SERVER_PORT}/phones/delete',
            data=data,
            headers={ 'content-type': 'application/json' }
        )


        if ('error' in json.loads(r.text)):
            raise ConnectionAbortedError
    
    
    except Exception as err:
        print(f'{err}')


def show(key):
    
    try:

        # Test connection


        r = requests.get(
            f'{const.SERVER_URL}:{const.SERVER_PORT}/phones/show?key={key}'
        )
        
        data = json.loads(r.text)['data']


        if ('error' in data):
            raise ConnectionAbortedError
        print(data)
    
    except Exception as err:
        print(f'{err}')

def main():
    try:
        while True:
            pwd = os.getcwd().replace("\\\\", "/")
            shell_input = " ".join(input(pwd + ' # ').split())
            user_input = []
            start = 0
            inQuotes = False
            for i in range(len(shell_input)):
                if shell_input[i] == '"' or shell_input[i] == "'":
                    inQuotes = not inQuotes

                if (shell_input[i] == ' ' or i == len(shell_input) - 1) and not inQuotes:
                    end = i + 1 if i == len(shell_input) - 1 else i
                    user_input.append(shell_input[start:end])
                    start = i + 1
                    inQuotes = False

            command = user_input[0]
            args = user_input[1:] if len(user_input) > 1 else []
            args = [arg.replace("'", "").replace('"', "") for arg in args]

            #print(f'<<TEST STRING: COMMAND: {command}; args {args}>>')
            primary_commands(command, args)
                

    except KeyboardInterrupt:
        print('\nBye!\n')



if __name__ == '__main__':
    main()