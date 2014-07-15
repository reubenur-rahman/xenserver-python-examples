'''
Copyright 2014-2015 Reubenur Rahman
All Rights Reserved
@author: reuben.13@gmail.com
'''

import XenAPI

inputs = {'xenserver_master_ip': '15.212.180.137',
          'xenserver_password': 'reuben',
          'xenserver_user': 'root',
          'vm_name': 'SLES11SP2x64',
          'target_host': 'xenserver-2'
          }
"""
NB: You need a shared storage to perform this action
"""

def main():
    try:
        print "Aquiring session with the provided xenserver IP..."
        session = XenAPI.Session('http://' + inputs['xenserver_master_ip'])
        print "Trying to connect to xenserver %s ..." % inputs['xenserver_master_ip']
        session.xenapi.login_with_password(inputs['xenserver_user'], inputs['xenserver_password'])
        print "Connected to xenserver !"

        for vm_ref in session.xenapi.VM.get_by_name_label(inputs['vm_name']):
            vm_uuid = session.xenapi.VM.get_uuid(vm_ref)

        vm = session.xenapi.VM.get_by_uuid(vm_uuid)

        for host_ref in session.xenapi.host.get_by_name_label(inputs['target_host']):
            host_uuid = session.xenapi.host.get_uuid(host_ref)

        target_host = session.xenapi.host.get_by_uuid(host_uuid)
        print "Migrating VM using XenMotion..."
        try:
            session.xenapi.VM.pool_migrate(vm, target_host, {"live": "true"})
            msg = "Successfully migrated VM %s to %s" % (inputs['vm_name'], inputs['target_host'])
            print msg
        except Exception, e:
            print e
            msg = "Failed to Migrate VM %s to %s " % (inputs['vm_name'], inputs['target_host'])
            print msg
    except Exception, e:
        print "Caught exception: %s" % str(e)

    session.logout()
# Start program
if __name__ == "__main__":
    main()
