'''
Copyright 2014-2015 Reubenur Rahman
All Rights Reserved
@author: reuben.13@gmail.com
'''

import sys
import XenAPI


inputs = {'xenserver_master_ip': '15.14.19.27',
          'xenserver_password': 'reuben',
          'xenserver_user': 'root',
          'vm_name' : 'SLES-11-SP2-x64',
          'operation': 'stop',
          'force': 'false'
          }

def validate_vm_state(current, request, force):
    """
    Validates whether to change the VM state to requested state
    """

    msg = "Current state = %s | Requested State = %s | Force = %s" %(current, request, force)
    print msg

    if request == "start":
        return current in [ "Halted", "Suspended" ]
    elif request == "stop":
        if not force: return current in [ "Running", "Paused" ] 
        else: return current in ["Running", "Paused", "Suspended"]
    elif request == "pause":
        return current in ["Running"]
    elif request == "suspend":
        return current in ["Running"]
    elif request == "resume":
        return current in ["Paused"]
    elif request == "reset":
        if not force: return current in [ "Running", "Paused"]
        else: return current in ["Running", "Paused", "Suspended"]
    else:
        return False

def _is_operation_allowed(session, reference, api_endpoint, op):
    api_target = getattr(session.xenapi, api_endpoint)
    allowed_ops = api_target.get_allowed_operations(reference)
    print "Allowed operations: %s" % (allowed_ops)
    return op in allowed_ops
 
def start_vm(session, vm, force):
    current_state = session.xenapi.VM.get_power_state(vm)
    requested_state = 'start'
    target_host_ref = None
    is_host_cluster = True # If not cluster setup then provide the uuid of the host
    
    if not is_host_cluster:
        target_host_uuid = '33075f30-097f-4fa1-86e5-44e26cbf2ee7'
        target_host_ref = session.xenapi.host.get_by_uuid(target_host_uuid)
    
    if validate_vm_state(current_state, requested_state, force):
        if current_state == 'Halted':
            if target_host_ref:
                session.xenapi.VM.start_on(vm, target_host_ref, False, False)
            else:
                session.xenapi.VM.start(vm, False, False)
            print "VM started successfully"
        else:
            if target_host_ref:
                session.xenapi.VM.resume_on(vm, target_host_ref, False, False)
            else:
                session.xenapi.VM.resume(vm, False, False)
            print "VM resumed successfully"
    else:
        msg = "Current state of VM can not be changed to requested state. Failed to '%s' VM" % requested_state
        print msg
        sys.exit()


def stop_vm(session, vm, force):
    current_state = session.xenapi.VM.get_power_state(vm)
    requested_state = 'stop'

    if _is_operation_allowed(session, vm, "VM", "clean_shutdown"):
        if validate_vm_state(current_state, requested_state, force):

            if not force:
                session.xenapi.Async.VM.clean_shutdown(vm)
                print "VM successfully soft shutdown"
            else:
                session.xenapi.VM.hard_shutdown(vm)
                print "VM successfully hard shutdown"
    else:
        print "Clean shutdown is not allowed on VM, Attempting a hard shutdown"
        session.xenapi.VM.hard_shutdown(vm)
        print "VM successfully hard shutdown"

  
def suspend_vm(session, vm):
    #If you face this error "VM_MISSING_PV_DRIVERS"
    #then contact me. I will update the suspend code.
    current_state = session.xenapi.VM.get_power_state(vm)
    requested_state = 'suspend'
    
    if validate_vm_state( current_state, requested_state, False):
        session.xenapi.VM.suspend(vm)
        print "VM suspended successfully"
    else:
        msg = "Current state of VM can not be changed to requested state. Failed to suspend VM"
        print msg
        sys.exit()  

def pause_vm(session, vm):
    current_state = session.xenapi.VM.get_power_state(vm)
    requested_state = 'pause'
    
    if validate_vm_state( current_state, requested_state, False):
        session.xenapi.VM.pause(vm)
        print "VM paused successfully"
    else:
        msg = "Current state of VM can not be changed to requested state. Failed to pause VM"
        print msg
        sys.exit()   

def resume_vm(session, vm):
    current_state = session.xenapi.VM.get_power_state(vm)
    requested_state = 'resume'
        
    if validate_vm_state( current_state, requested_state, False):
        session.xenapi.VM.unpause(vm)
        print "VM resumed successfully"
    else:
        msg = "Current state of VM can not be changed to requested state.Failed to resume VM"
        print msg
        sys.exit()

def reset_vm(session, vm):
    pass

def str2bool(string):
    return string.lower() in ("true")

def main():
    try:
        print "Aquiring session with the provided xenserver IP"
        session = XenAPI.Session('http://'+inputs['xenserver_master_ip'])
        print "Trying to connect to xenserver %s" % inputs['xenserver_master_ip']
        session.xenapi.login_with_password(inputs['xenserver_user'], inputs['xenserver_password'])
        print "Connected to xenserver !"
    
        vm_refs = session.xenapi.VM.get_by_name_label(inputs['vm_name'])
        for vm_ref in vm_refs:
            vm_uuid = session.xenapi.VM.get_uuid(vm_ref)

        vm = session.xenapi.VM.get_by_uuid(vm_uuid)

        force = str2bool(inputs['force'])

        if inputs['operation'] == 'start':
            start_vm(session, vm, force)
        elif inputs['operation'] == 'stop':
            stop_vm(session, vm, force)
        elif inputs['operation'] == 'suspend':
            suspend_vm(session, vm)
        elif inputs['operation'] == 'pause':
            pause_vm(session, vm)
        elif inputs['operation'] == 'resume':
            resume_vm(session, vm)
        elif inputs['operation'] == 'reset':
            reset_vm(session, vm, force)

    except Exception, e:
        print "Caught exception: %s" % str(e)

    session.logout()
# Start program
if __name__ == "__main__":
    main()
