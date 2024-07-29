The LDAP configuration details, such as the LDAP server IP, bind DN, and base DN, are typically provided in the `ldap-group-sync.yaml` configuration file, which is referenced in the `--sync-config` argument of the CronJob.

Here’s an example of what the `ldap-group-sync.yaml` file might look like:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ldap-group-syncer
  namespace: openshift-authentication
data:
  ldap-group-sync.yaml: |
    kind: LDAPSyncConfig
    apiVersion: v1
    url: ldap://<LDAP_SERVER_IP>
    bindDN: cn=admin,dc=example,dc=com
    bindPassword:
      file: /etc/secrets/bind-password
    rfc2307:
      groupsQuery:
        baseDN: ou=groups,dc=example,dc=com
      usersQuery:
        baseDN: ou=users,dc=example,dc=com
      groupUID: dn
      userUID: dn
      groupNameAttributes: [ cn ]
      groupMembershipAttributes: [ member ]
      userNameAttributes: [ uid ]
```

In this example:

- Replace `<LDAP_SERVER_IP>` with the actual IP address or hostname of your LDAP server.
- `bindDN` is the distinguished name used to bind to the LDAP server.
- `baseDN` under `groupsQuery` and `usersQuery` specifies the base distinguished names to search for groups and users.
- `bindPassword` points to the file where the bind password is stored. This file should be mounted from the secret as shown in the CronJob configuration.

Make sure you create this ConfigMap before applying the CronJob. You can create it with the following command:

```sh
oc create -f ldap-group-sync-config.yaml
```

Here’s an example of how to mount this configuration and secret in your CronJob:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: ldap-group-syncer
  namespace: openshift-authentication
spec:
  schedule: "0 * * * *"  # Runs every hour
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: ldap-group-sync
              image: "registry.redhat.io/openshift4/ose-cli:v4.7"
              command:
                - "/bin/bash"
                - "-c"
                - oc adm groups sync --sync-config=/etc/config/ldap-group-sync.yaml --confirm
              volumeMounts:
                - mountPath: "/etc/config"
                  name: "ldap-sync-config"
                - mountPath: "/etc/secrets"
                  name: "ldap-bind-password"
          volumes:
            - name: "ldap-sync-config"
              configMap:
                name: "ldap-group-syncer"
            - name: "ldap-bind-password"
              secret:
                secretName: "v4-0-config-user-idp-0-bind-password"
          restartPolicy: "Never"
```

The `ldap-group-sync.yaml` file will contain all the necessary LDAP connection details, including the LDAP server IP address. Ensure that the LDAP server's IP address and other required details are correctly set in this file.