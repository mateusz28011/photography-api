# PhotoBay - api

![Screenshot of site](https://raw.github.com/mateusz28011/photography-api/main/Photography-API.png)

## Table of contents

- [Live demo](#live-demo)
- [General info](#general-info)
- [Technologies](#technologies)
- [Functionalities](#functionalities)
- [Setup](#setup)
- [Sources](#sources)

## Live demo

[Demo link](https://photography-api-project.herokuapp.com/)

## General Info

This is application for photographers and their customers. I wanted to create place where:\
- Photograpers can:
    - easily show his/her work to world, 
    - manage his/her albums and images in one place,
    - allow his/her clients to making order for services in accesible form,
    - share albums to choosed people.
- Customers can:
    - find a photographer whose style suits them best,
    - make and track their orders,
    - have all their photos in one place.
 
I must admit that the project does not meet my expectations at the moment and it is unlikely to be released yet. There are a lot of things that still need to be thought over and implemented:
- payment system
- limitations uploading, creating albums and images
- search engine that should take in consideration somekind of statistics
- bulk operations of uploading photos
- order's message chat in real time using websocekts
- think of abonament for vendors

This project also includes client created in React which you can find [here](https://github.com/mateusz28011/photography-client).

## Technologies

Project is created with:

- [Django](https://www.djangoproject.com/)
- [Django Rest Framework](https://www.django-rest-framework.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [Dj-rest-auth](https://github.com/iMerica/dj-rest-auth)
- [Drf-yasg](https://github.com/axnsan12/drf-yasg)
- [Django-imagekit](https://github.com/matthewwithanm/django-imagekit)
- [AWS S3](https://aws.amazon.com/s3/)

## Functionalities

### Albums
Only user with profile can create albums. Images in advance are private in S3 and Django is responsible of authorization. Thumbnails are automatically generated for uploaded photos.
- Filtering, searching, ordering and pagination.
- If the album is private, only the author or a user with access can view the album. 
- Moving albums to others.
- Adding images.
- Giving and removing access to albums.

### Orders
Every user can make order. The entire order cycle is implemented. There is no payment system implemented. 

- Filtering, searching, ordering and pagination.
- Sending messages in orders.
- Vendor can attach created album to order.

#### Available statuses:
The created orders have default status of 2.

    0 - Canceled
    1 - Rejected
    2 - Waiting for acceptance
    3 - Accepted
    4 - Waiting for payment
    5 - Payment received
    6 - Finished

#### Permissions
If order status is 0, 1 or 6 it cannot be changed.
- **Client**\
Can only update status.\
Can only update status when it is 2 and can only be set to 0.\
- **Vendor**\
Upating album automatically adds client to allowed users and makes it private.\
Available update for specific status:\
    - 2 -> 1 or 3
    - 3 -> 0, 4 or 6
        - If set to 4, cost cannot be null.
    - 4 -> 0, 5, 6
    - 5 -> 0 or 6
    
### Profiles
By creating a profile, the user becomes a vendor. Portfolio is created automatically and can not be deleted, this is album in which vendor can create nested albums and upload photos to show his/her skills etc. Payment info is optional beacouse there is no payment system implemented.

- Searching, ordering and pagination.
- Uploading avatar.

## Setup

TODO

## Sources

[Illustrations](https://undraw.co/illustrations)
