import argparse
import subprocess
import os
import getpass

DOCUMENT_ROOT = '/var/www/vhosts/'

parser = argparse.ArgumentParser(description='migrate a website from one server to another')
parser.add_argument('site', help='the site to be migrated')
parser.add_argument('destination', help='where to move the site')

# parser.add_argument('-v', '--verbose', help='explain what you are doing', action='store_true')
# parser.add_argument('--no-db', help='skip the database migration', action='store_true')
parser.add_argument('-sdn', '--source-db-name', help='what the database is currently named', required=True)
parser.add_argument('-ddn', '--dest-db-name', help='what the database should be named, defaults to source-db-name')
parser.add_argument('-sdu', '--source-db-user',
                    help='what user currently uses the database, defaults to source-db-name')
parser.add_argument('-ddu', '--dest-db-user', help='what user will use the database, defaults to dest-db-name')
parser.add_argument('-sdp', '--source-db-pass', nargs='?',
                    help='what the password for the user currently is, defaults to prompt', const='prompt',
                    required=True)
parser.add_argument('-ddp', '--dest-db-pass', nargs='?',
                    help='what the password for the user should be, defaults to source-db-pass', const='prompt')
parser.add_argument('-sdh', '--source-db-host', help='where the database currently resides', required=True)
parser.add_argument('-ddh', '--dest-db-host', help='where the database should go', default='aws-db1.firstscribe.com')
args = parser.parse_args()

# Populate the rest of the arguments

if args.dest_db_name == None:
    args.dest_db_name = args.source_db_name
if args.source_db_user == None:
    args.source_db_user = args.source_db_name
if args.dest_db_user == None:
    args.dest_db_user = args.source_db_user
if args.source_db_pass == 'prompt':
    args.source_db_pass = getpass.getpass(prompt='Please enter the source database password: ')
if args.dest_db_pass == None:
    args.dest_db_pass = args.source_db_pass
elif args.dest_db_pass == 'prompt':
    args.dest_db_pass = getpass.getpass(prompt='Please enter the destination database password: ')


def step_placeholder(action):
    print('Now would be a great time to', action, '.')
    input('Press enter when done.')


# Verify ssh-agent is running
step_placeholder('start an ssh agent')

# Verify DNS abilities
step_placeholder('verify that we can alter DNS')

# Notify customer
step_placeholder('notify the customer')

# Create new customer/domains on plesk
step_placeholder('make the new customer in plesk')

# Copy SSL certs if any
step_placeholder('copy the SSL certificates')

# Copy any special hosting settings/php settings
step_placeholder('verify the PHP and hosting settings')

# Find database references.  I like grep -R '\.firstscribe\.com'
step_placeholder('locate the database configuration')

# Make database (through plesk, to get ref)
step_placeholder('create the database ' + str(args.dest_db_name))

# Transfer the Database

# I bit off more than I can chew...

# mysqldump_proc = subprocess.Popen(
#     ('mysqldump', '-u', args.source_db_user, '-h', args.source_db_host, '-p', args.source_db_pass, args.source_db_name),
#     stdout=subprocess.PIPE)
# sed_proc = subprocess.Popen(('sed', 's/TIME_ZONE=\'+00:00\'/TIME_ZONE=\'+06:00\'/'), stdout=subprocess.PIPE,
#                             stdin=mysqldump_proc.stdout)
# mysqldump_proc.stdout.close()
# pv_proc = subprocess.Popen('pv',
#                            stdin=sed_proc.stdout, stdout=subprocess.PIPE)
# sed_proc.stdout.close()
# xz_proc = subprocess.Popen(('xz', '-c', '-4'), stdout=subprocess.PIPE, stdin=pv_proc.stdout)
# pv_proc.stdout.close()
# # noinspection PyPep8
# ssh_mysql_proc = subprocess.Popen(('ssh', args.destination,
#                                    '\"xz -d -c | mysql -u ' + args.dest_db_user + ' -p \\\"' + args.dest_db_pass + '\\\" -h ' + args.dest_db_host + ' ' + args.dest_db_name),
#                                   stdin=xz_proc.stdout)
# pv_proc.stdout.close()
#
# ssh_mysql_proc.communicate()
# ssh_mysql_proc.wait()

subprocess.call(
    'mysqldump -u{} -p"{}" -h{} {} | sed "s/TIME_ZONE=\'+00:00\'/TIME_ZONE=\'+06:00\'/" | pv | xz -c -4 | ssh {} "xz -d -c | mysql -u{} -p\"{}\" -h{} {}"'.format(
        args.source_db_user, args.source_db_pass,
        args.source_db_host, args.source_db_name,
        args.destination, args.dest_db_user,
        args.dest_db_pass, args.dest_db_host,
        args.dest_db_name), shell=True) # This is the "wrong" way to do it, but I can't get the nested Popen's to work

# Update the DB refs in local.xmls or wp-config.php
step_placeholder('update database refs')

# Make sure you didn't break anything
step_placeholder('test the original site')

# Transfer the site
site_path = DOCUMENT_ROOT + args.SITE
site_httpdocs = site_path + '/httpdocs'

subprocess.call(('ssh', '-t', args.destination, '\"sudo chmod -R g+w ' + site_path + '\"'))
subprocess.call(('ssh', args.destination, '\"rm -rf ' + site_httpdocs + '*\"'))


def get_folder_size(folder):
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += get_folder_size(itempath)
    return total_size


# Bit off more than I can chew...

# tar_proc = subprocess.Popen(('tar', 'cf', '-', 'httpdocs', '-C', site_path), stdout=subprocess.PIPE)
# pv2_proc = subprocess.Popen(('pv', '-s', get_folder_size(site_path)), stdin=tar_proc.stdout, stdout=subprocess.PIPE)
# tar_proc.stdout.close()
# xz2_proc = subprocess.Popen(('xz', '-c'), stdin=pv2_proc.stdout, stdout=subprocess.PIPE)
# pv2_proc.stdout.close()
# ssh_tar_proc = subprocess.Popen(('ssh', args.description, '\"tar xJf - -C ' + site_path + '\"'), stdin=xz2_proc.stdout)
#
# ssh_tar_proc.communicate()
# ssh_tar_proc.wait()

subprocess.call('tar cf - httpdocs -C {0} | pv -s {1} | xz -c |  ssh {2} "tar xJf - -C {0}"'.format(site_path, get_folder_size(site_path), args.destination), shell=True)

# If we host DNS, copy records
step_placeholder('update new DNS if on plesk')

# Test the site in the new location
step_placeholder('test the site in the new location.')

# Update DNS/Switch Nameserver
step_placeholder('update the real DNS')

# Clear magento cache
step_placeholder('clear the magento cache')

# Disable old site next day
step_placeholder('make a reminder to disable the site the next day')
