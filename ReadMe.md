# Macaroons examples / demo

Two macaroons Python demos for a school project.

Photo sharing demo:

### Prerequisites

```
pip install pymacaroons
pip install Flask
```

### How to use

There are 2 demos included:

#### Auth demo

A simple demonstration of how macaroons are used to facilitate authentication using a third party authentication service.

The two server (alices server) and the auth server are running on the same frontent for simplicity.

##### Goal of the demo

Bob wants to access a service on Alices Server. Alice wants Bob to be authenticated by a separate Auth Server.

##### How to use

1. Get Macaroon
    - This will get a new Macaroon from Alices Server
    - Bob now knows where to authenticate
2. Get discharge macaroon from Auth Server (Login)  
    - Bob can now login to the auth server which in turn will return a discharche macaroon
3. Try to access service
    - Bob can now use the two macaroons to access Alices Server

#### Photo sharing demo

##### Goal of the demo


## Acknowledgments

The auth demo is heaviliy based on this ReadMe:
https://github.com/rescrv/libmacaroons/blob/master/README

The photo sharing demo was inspired by:
http://evancordell.com/2015/09/27/macaroons-101-contextual-confinement.html
