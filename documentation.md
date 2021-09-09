# RIDES SERVICE

## **COUNTER**
*/api/v1/_count* (directly ping the service)

| Request Method | Use | Expected Status Codes |
|----------------|-----|-----------------------|
| GET | Sends the number of requests made to Rides APIs | *200* : Sends the number of requests as an integer |
| DELETE | Clears the number of requests i.e. makes them 0 | *204* : Successfully made it 0 |

## **RIDE CREATION BASED**
*/api/v1/rides*

| Request Method | Use | Expected Status Codes |
|----------------|-----|-----------------------|
| GET | Provides details of all upcoming rides (rideId, username,timestamp) between given source and destination | 1. *200* : Sends a list of rides(with their details) in the json body <br/>2. *400* : If source or destination are not in the request <br/>3. *500* : Otherwise|
| POST | Create a ride based on username, timestamp, source and destination provided in the json | 1. *201* : Successfully created <br/>2.*400* : If ```user/username field in request json``` doesn't exist <br/>3. *500* : Otherwise|

## **RIDE DETAILS BASED**
*/api/v1/rides/<int:ride_id>*

| Request Method | Use | Expected Status Codes |
|----------------|-----|-----------------------|
| GET | Provides details (rideId,Created_By,timestamp,source,destination,users) of the given ride_id | 1. *200* : Sends the mentioned fields in the json body <br/>2. *404* : If ride doesn't exist <br/>3. *500* : Otherwise|
| POST | Add the given user (in request json)  to the given ride | 1. *201* : Successfully added <br/>2.*400* : If ```user/username field in request json``` doesn't exist <br/>3. *404* : If ride doesn't exist <br/>4.*500* : Otherwise|
| DELETE | Delete the ride with ride_id | 1. *204* : Successfully deleted <br/> 2. *404* : If ride_id doesn't exist <br/> 3. *500* : Otherwise |

# USERS SERVICE

## **COUNTER**
*/api/v1/_count* (directly ping the service)

| Request Method | Use | Expected Status Codes |
|----------------|-----|-----------------------|
| GET | Sends the number of requests made to Rides APIs | *200* : Sends the number of requests as an integer |
| DELETE | Clears the number of requests i.e. makes them 0 | *204* : Successfully made it 0 |

## **USER CREATION BASED**
*/api/v1/users*

| Request Method | Use | Expected Status Codes |
|----------------|-----|-----------------------|
| GET | Returns all the users currently enrolled with the service | 1. *200* : Sends a list of users in the json body <br/>2. *400* : If source or destination are not in the request <br/>3. *500* : Otherwise|
| PUT | Create a user based on username, SHA1 based password given | 1. *201* : Successfully added <br/>2.*400* : If required fields are not in the request, password not in SHA1 format, user already exists<br/>3. *500* : Otherwise|

## **USER REMOVAL BASED**
*/api/v1/users/<string:user_name>*

| Request Method | Use | Expected Status Codes |
|----------------|-----|-----------------------|
| DELETE | Delete the user having the given username| 1. *204* : Successfully deleted <br/> 2. *400* : If user doesn't exist <br/> 3. *500* : Otherwise |

# WRITING TO DB (common for both)

| Request Method | Use | Expected Status Codes |
|----------------|-----|-----------------------|
| POST | Writes to the respective DB | 1. *201* : Successfully written into the database <br/> 2. *500* : Otherwise |

# READING FROM DB (common for both)

| Request Method | Use | Expected Status Codes |
|----------------|-----|-----------------------|
| POST | Sends the number of requests made to Rides APIs | 1. *200* : Returns a list of dictionaries(representing tuples) where each key-value pair represents column name and its corresponding value in the tuple <br/> 2. *500* : Otherwise |

# CLEARING THE DB
*directly ping the service*

| Request Method | Use | Expected Status Codes |
|----------------|-----|-----------------------|
| POST | 1. *204* : Successfully cleared the tables in the DB<br/> 2. *500* : Otherwise |