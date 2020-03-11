# PV Migrator
Resources for migrating PVCs/PVs to a new specified storage class in place without having to update applications with new PVC names.

# Playbooks

## migrate-pvs.yml
Ansible playbook to migrate the PVs assoicated with the PVCs in a given list of projects/namespaces to a new sotrage class.

### Required k8s Permisions

* Permisison to create new PVCs using the given storage class
* project admin on the specified projects
* permisions to edit PVs

### Parameters

| Parameter                                        | Choices / **Defaults** | Comments
|--------------------------------------------------|------------------------|---------
| k8s\_host                                        |                        | K8s API to run this playbook against
| k8s\_validate\_certs                             | **True** / False       | Whether to validate K8s API certificate
| k8s\_api\_key                                    |                        | K8s API token to authenticate with. Mutually exclusive with `k8s_username` and `k8s_password`.
| k8s\_username                                    |                        | K8s username to authenticate with. Mutually exclusive with `k8s_api_key`.
| k8s\_password                                    |                        | K8s password to authenticate with. Mutually exclusive with `k8s_api_key`.
| k8s\_pv\_migrator\_namespaces                                  |          | Required. Namespaces containing the PVCs who's PVs should be migrated.
| k8s\_pv\_migrator\_destination\_storageclass                   |          | Required. Name of the k8s storage class to migrate to.
| k8s\_pv\_migrator\_pvc\_label\_selectors                       | **[]**   | Optional. Label(s) that must be on PVCs in the given namespaces to migrate.
| k8s\_pv\_migrator\_job\_wait\_timeout                          | **3600** | Optional. Timeout in secoonds to wait for migraiton jobs to finish. If you have large data sets you will need to update this.
| k8s\_pv\_migrator\_temp\_destination\_pvc\_postfix             | **-new** | Optional. Postfix appened to PVC name for creating temporary PVC on the new storage class to create a new destination PV. Probably no good reason for you to change this.
| k8s\_pv\_migrator\_temp\_destination\_pvc\_bind\_wait\_retries | **60**   | Optional. How long to wait for new PVCs to bind.
| k8s\_pv\_migrator\_temp\_destination\_pvc\_bind\_wait\_delay   | **1**    | Optional. How long to wait for new PVCs to bind.
| k8s\_pv\_migrator\_pods\_shutdown\_wait\_retries               | **120**  | Optional. How long to wait for pods to shutdown before prompting user what to do.
| k8s\_pv\_migrator\_pods\_shutdown\_wait\_delay                 | **1**    | Optional. How long to wait for pods to shutdown before prompting user what to do.

### Examples

#### Basic example for 2 namespaces
```bash
ansible-playbook migrate-pvs.yml \
  -i localhost.ini \
  -e k8s_host=https://ocp.example.xyz \
  -e k8s_username=admin1 \
  -e k8s_password=secret \
  -e k8s_pv_migrator_namespaces="['test-migration0', 'test-migration1']" \
  -e k8s_pv_migrator_destination_storageclass='my-new-storage-class'
```

#### Example for 2 namespaces with PVC filtering based on labels
```bash
ansible-playbook migrate-pvs.yml \
  -i localhost.ini \
  -e k8s_host=https://ocp.example.xyz \
  -e k8s_username=admin1 \
  -e k8s_password=secret \
  -e k8s_pv_migrator_namespaces="['test-migration0', 'test-migration1']" \
  -e k8s_pv_migrator_destination_storageclass='my-new-storage-class' \
  -e k8s_pv_migrator_pvc_label_selectors="['migrate=true']"
```

### Executed Procedure
This is the procedure implimented to migrate PVs to a new storage class without having to update applications with new PVC names

1. log into k8s cluster
2. for each specified namespace
   1. Get source PVCs
      1. Get PVCs to migrate in namespace with correct label(s)
      2. Filter out PVCs that are already on destiation storage clas
   2. Create destination PVs
      1. Create temporary destination PVCs using new storage class
      2. Wait for temporary destination PVCs to be bound to new destination PV
      3. Get temporary PVC destiantions
   3. Perform pre pod scaledown PV rsync
      1. Create pv-migrator job per PVC
      2. Wait for pv-migrator jobs to complete
   4. Pods scale-down
      1. Get all scaleable resources
      2. Scale down all scaleable resources to 0
      3. Wait for all pods to be stopped
         * if this times out, prompt user on whether to continue or not giving user chance to manually kill pods or abort migration
   5. Perform post pod scale-down PV rsync
      1. Create pv-migrator job per PVC
      2. Wait for pv-migrator jobs to complete
   6. Perform PVC migration
      1. Set destination PVs to 'Retain' so they do not delete when their temporary PVC is deleted
      2. Delete temporary destination PVCs
      3. Set source PVs to 'Retain' and labe
         * migrated: true
         * migrated-to-pv: (destination PV name)
      4. Delete source PVCs
      5. Remove claimRef from destination PVs and update labels
      6. Create new PVC with origional source PVC name pre-bound to new destination PV created in new storage class
      7. Set destination PVs back to their orgional reclaim policy
   7. Pods scale-up
      1. Scale up all scaleable resources to origional replica count
3. log out of k8s cluster
