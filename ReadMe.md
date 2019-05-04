# Macaroons examples / demo

Two macaroons Python demos for a school project.

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

A simple Demonstration of how macaroons can be used to facilitate sharing of a single photo of an album.

##### Goal of the demo

Bob wants to share a single Photo from his Album with Alice.

##### How to use

1. Login and go to photo album
    - Bob is now logged in to his photo album dashboard he recieved a macaroon as a cookie.
2. Share Picture
    - Bob is adding a caveat to his macaroon and has now generated a link that he can send to Alice
3. Open a new private window and paste link
    - Alice is authenticated but can only see the picture that Bob has shared


## Acknowledgments

The auth demo is heavily based on this ReadMe:
https://github.com/rescrv/libmacaroons/blob/master/README

The photo sharing demo was inspired by:
http://evancordell.com/2015/09/27/macaroons-101-contextual-confinement.html
