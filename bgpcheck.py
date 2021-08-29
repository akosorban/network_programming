import sys
from getpass import getpass

from netmiko import ConnectHandler

# adding command line args to a list
cmargs = []
n = len(sys.argv)
for i in range(1, n):
    cmargs.append(sys.argv[i])

# device parameters, connecting
device_type = 'cisco_ios'
username = 'te445587teadm'
password = getpass()
verbose = True
device = cmargs[0]
print('-' * 20 + '\nConnecting to ' + device + '\n' + '-' * 20)
cisco_dev = {'device_type': 'cisco_ios', 'ip': device, 'username': username, 'password': password}
session = ConnectHandler(**cisco_dev)
out = session.send_command_timing('enable')

# bgp summary-check
if 'bgp' or 'BGP' in cmargs:
    print('-=Checking BGP=-')

    # checking whether BGP is active on the device..
    out = session.send_command('show bgp ipv4 unicast summary')
    # if not active..
    if '% BGP not active' in out:
        print('BGP is not configured on ' + device)

    # if active..
    else:
        # adding each line of the show command output to a list
        out = session.send_command_timing('show bgp ipv4 unicast summary | begin Nei')

        for i in out.splitlines()[1:]:  # looping through the lines, ignoring the header

            pieces = i.split()
            # if peer is Active or Idle and not in Idle (Admin)
            # if pieces' length is larger than 9, then there's an '(Admin)' word after Idle

            out = session.send_command_timing(
                'show bgp ipv4 unicast neighbors ' + pieces[0] + ' | include Description')
            check = out.split(' ')  # checking if there's a description for the peer
            desc_str = ''

            if len(check) > 1:
                desc_str = out.strip()
            else:
                desc_str = 'Description: N/A'

            # if connection is down
            if pieces[9] == 'Active' or pieces[9] == 'Idle':
                if len(pieces) <= 10:

                    print('[-] BGP Peer ' + pieces[0] + ' is DOWN for ' +
                          pieces[8] + ' on ' + device + ' # ' + desc_str)

                else:
                    print('[-] BGP Peer ' + pieces[
                        0] + ' is manually SHUT DOWN [Idle (Admin)] on ' + device + ' # ' + desc_str)

            # if connection is up
            else:
                print('[+] BGP Peer ' + pieces[0] + ' is UP for ' + pieces[8] + ' on ' + device + ' # ' + desc_str)

        out = ''

out = session.send_command_timing('show clock')
print('-' * 20 + '\nSystem clock: ' + out)
