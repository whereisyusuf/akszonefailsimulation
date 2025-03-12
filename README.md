
# Zone-failure simulation in Azure Kubernetes Service (AKS)

The resources in this repository aims to help in the simulation of Zone Failure of an Azure Kubernetes Service (AKS) cluster.

This repository includes a FastAPI-based Python API (**server.py**) which features 3 endpoints. Depending on the endpoints, the API fetches data either from the MySQL or SQL Server instance. For our testing we have used Azure Db for MySQL and Azure SQL MI respectively. The repo also includes the necessary Dockerfile and Kubernetes manifest files for Deployment and Service creation along with the Python-based insert scripts of the sample data for MySQL (**mysqlinsertscript.py**) and SQL Server (**sqlserverinsertscript**).

The repository also includes a bash-based test harness (**apitestharness.sh**) which has the capability to continuosly hit the desired endpoint exposed by the API and to print the HTTP success status.

Another important code file is the bash-based zone fail simulation (**akszonefailsimulation.sh**) which has the necessary steps to simulate the Zone Failure of the desired zone in Azure for the AKS cluster as well as Azure Db for MySQL and Azure SQL MI. 


## Source files

### Database insert scripts
**mysqlinsertscript.py**: Python-based insert scripts of the sample data for MySQL
**sqlserverinsertscript**: Python-based insert scripts of the sample data for SQL Server

### Application files
**server.py**: FastAPI-based Python API
**requirements.txt**: Python package requirements file

### Kubernetes manifest and Docker files
**Dockerfile**: Dockerfile required for containerization of the API
**k8sdeployment.yaml**: Kubernetes manifest file for deployment
**k8sservice.yaml**: Kubernetes manifest file for service

### Files needed for Zone Fail simulation
**apitestharness.sh**: A bash-based test harness which has the capability to continuosly hit the desired endpoint exposed by the API and to print the HTTP success status
**akszonefailsimulation.sh**: A bash-based zone fail simulation which has the necessary steps to simulate the Zone Failure of the desired zone in Azure for the AKS cluster as well as Azure Db for MySQL and Azure SQL MI


## Execution steps

1. Provision the **Azure Db for MySQL - Flexible** and **Azure SQL MI** database servers. Kindly note that these database servers need to be zone-redundant.
2. Provision the **Zone-redundant AKS cluster**. The **system node pool** of the AKS cluster should be spanning across all the 3 Availability Zones. 3 different **user node pools** should also be created - with each user node pool "pinned" to just one unique Availability Zone.
3. Set the database server details in the **server.py** file and containerize the application and push it to the desired Azure Container Registry (ACR). 
4. Update the **k8sdeployment.yaml** file with the container image details from the ACR and create the K8S deployment in the AKS cluster.
5. Create the K8S service in the AKS cluster using **k8sservice.yaml**.
6. Update the **apitestharness.sh** file with the IP address of the K8S service and other endpoint details.
7. Update the **akszonefailsimulation.sh** with the necessary details as mentioned through the placeholders.
8. Execute (step-by-step to begin with) the **akszonefailsimulation.sh** script.
