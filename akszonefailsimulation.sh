#!/bin/bash

# Input Variables
aksClusterName="<your-aks-clustername>"
resourceGroupName="<your-aks-resource-group-name>"
userNodePoolName="<user-node-pool-name>" # Name of the target user node pool
systemNodePoolName="<user-node-pool-name>"  # Name of the system node pool
namespace="<application namespace>" # Namespace where the application is deployed
sqlservername="<Azure SQL MI server name>" # Azure SQL MI server name
mysqlname="<Azure Db for MySQL flexible server name>" # MySQL flexible server name
zoneToFail="<zone-to-fail>"  # Specify the zone to fail (e.g., centralindia-1)

# Login to the AKS Cluster
az aks get-credentials --resource-group $resourceGroupName --name $aksClusterName --overwrite-existing

# Fetch updated node information
kubectl get nodes -L kubernetes.azure.com/agentpool,topology.kubernetes.io/region,topology.kubernetes.io/zone

kubectl get pod -o=custom-columns=NAME:.metadata.name,STATUS:.status.phase,IP:.status.podIP,HOSTIP:.status.hostIP,NODE:.spec.nodeName -n $namespace

# Get all nodes in the target zone with their node pool labels
NODES_AND_POOLS=$(kubectl get nodes -o json | jq -r --arg zone "$zoneToFail" \
    '.items[] | select(.metadata.labels["topology.kubernetes.io/zone"] == $zone) | "\(.metadata.name) \(.metadata.labels["kubernetes.azure.com/agentpool"])"')

# Check if there are nodes in the zone
if [ -z "$NODES_AND_POOLS" ]; then
    echo "No nodes found in the zone $zoneToFail."
    exit 1
fi

# Prepare arrays to store nodes for each pool
systemPoolNodes=()
userPoolNodes=()

# Populate the arrays based on the node pool
while IFS=" " read -r nodeName nodePool; do
    if [ "$nodePool" == "$systemNodePoolName" ]; then
        systemPoolNodes+=("$nodeName")
    elif [ "$nodePool" == "$userNodePoolName" ]; then
        userPoolNodes+=("$nodeName")
    fi
done <<< "$NODES_AND_POOLS"

# Disable cluster autoscaler for the system and user node pools

az aks nodepool update --resource-group $resourceGroupName --cluster-name $aksClusterName --name $systemNodePoolName --disable-cluster-autoscaler

az aks nodepool update --resource-group $resourceGroupName --cluster-name $aksClusterName --name $userNodePoolName --disable-cluster-autoscaler


# ---- Start the API Test Harness ----
# In another terminal, run the API test harness to simulate the failure -- ./apitestharness.sh


# Helper function to delete nodes in a given node pool
delete_nodes_in_pool() {
    local poolName=$1
    shift
    local nodes=("$@")
    if [ ${#nodes[@]} -gt 0 ]; then
        local machineNames=$(IFS=" "; echo "${nodes[*]}")
        local command="az aks nodepool delete-machines --resource-group $resourceGroupName --cluster-name $aksClusterName --name $poolName --machine-names $machineNames"
        echo "Executing command for pool $poolName:"
        echo "$command"
        eval "$command"
    else
        echo "No nodes to delete in pool $poolName."
    fi
}

# Delete nodes in system node pool
delete_nodes_in_pool "$systemNodePoolName" "${systemPoolNodes[@]}" &

# Delete nodes in user node pool
delete_nodes_in_pool "$userNodePoolName" "${userPoolNodes[@]}" &

# Restart MySQL flexible server and force a failover in parallel
az mysql flexible-server restart --resource-group $resourceGroupName --name $mysqlname --failover Forced &

# Azure SQL MI failover
#az sql mi failover -g $resourceGroupName -n $sqlservername &

wait

echo "Node deletion in both node pools and Azure Db for MySQL/Azure SQL MI failover completed."


# Precautionary step: Scale down the user node pool to 0
az aks nodepool scale --resource-group $resourceGroupName --cluster-name $aksClusterName --name $userNodePoolName --node-count 0



# Fetch updated node information
kubectl get nodes -L kubernetes.azure.com/agentpool,topology.kubernetes.io/region,topology.kubernetes.io/zone

kubectl get pod -o=custom-columns=NAME:.metadata.name,STATUS:.status.phase,IP:.status.podIP,HOSTIP:.status.hostIP,NODE:.spec.nodeName -n $namespace

