# FASTAPI & CLOUDFLARE SET UP AND ARCHITECTURE

HOW IS THE DOCKER WORKING ?

- the docker is accessing the data from the main.py file , main.py file acts as the wrapper where all the api functions are added and the end point is created

DOES THE API END POINT RUN ON ITS OWN?

- the api end points are stored in the wrapper and then the main.py is run with the uvicorn command by fastapi , this opens the port 1555 in the server making it accessable by curl

HOW CAN WAS THE API MADE PUBLIC? 

- the api is made public with the help of cloud flare and with the domain saifmk.wesbite where the DNS was added and then config with CF , we run the tunnel inorder to make the api public

<br> ---------------------------------------------------

WHAT ARE THE API ENDPOINTS??

| Docker Image Name | Environment | Endpoint |
|----------|-------------|----------|
| stock-api-endpoints | Public | https://stock-api.saifmk.website/stock/{stockname} |
| stock-api-endpoints | Local | http://localhost:1555/stock/{stockname} |
| stock-api-endpoints | Public | https://stock-api.saifmk.website/search/{stockname} |
| stock-api-endpoints | Local | http://localhost:1555/search/{stockname} |

<br> ---------------------------------------------------

WHERE CAN I FIND THE FILES AND CONFIG , JSON OF THE CLOUD FLARED?

- in the server the folders and all the files related to the cloud flare are added in the ~/.cloudflare the yml file is the main file where all the configs are added

WHATS THE STRUCTURE OF RUNNING THE CODE IN THE SERVER?

- the code is run within the server by the docker , the api end point port 1555 become live with the docker compose and the name has been specified as stock-api-endpoints:latest      ef9ea0a1fa3c  
- the cloudflare is required to run locally with the command [cloudflared tunnel run]