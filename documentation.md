# RIDES SERVICE

## **COUNTER**
*/api/v1/_count*

| Request Method | Use | Expected Status Codes |
|----------------|-----|-----------------------|
| GET | Sends the number of requests made to Rides APIs | *200* : Sends the number of requests as an integer |
| DELETE | Clears the number of requests i.e. makes them 0 | *204* : Successfully made it 0 |

## **RIDE BASED**
*/api/v1/rides/<int:ride_id>*
| Request Method | Use | Expected Status Codes |
|----------------|-----|-----------------------|
| GET | Provides details (rideId,Created_By,timestamp,source,destination,users) of the given ride_id | 1. *200* : Sends the mentioned fields in the json body <br/>2. *404* : If ride doesn't exist <br/>3. *500* : Otherwise|
| POST | Add the given user (in request json)  to the given ride | 1. *201* : Successfully added <br/>2.*400* : If ```user/username field in request json``` doesn't exist <br/>3. *404* : If ride doesn't exist <br/>4.*500* : Otherwise|
| DELETE | Delete the ride with ride_id | 1. *204* : Successfully deleted <br/> 2. *404* : If ride_id doesn't exist <br/> 3. *500* : Otherwise |

