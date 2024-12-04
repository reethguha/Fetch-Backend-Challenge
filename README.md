# Fetch-Backend-Challenge

## Overview
This program implements a points management system using Flask. Users can:
    
    1. Add points for specific payers with timestamps.
    2. Spend points in a "first in, first out" (FIFO) manner.
    3. View the current balance of all payers.

The program ensures proper deduction while maintaining the order of transactions.

## Requirements

    1. Python
    2. Flask
    3. Flask-SQLAlchemy

## Installation

    1. Clone the repository:
        git clone https://github.com/reethguha/Fetch-Backend-Challenge.git
        cd Fetch-Backend-Challenge 

    2. Install the required packages:
        pip3 install flask flask-sqlalchemy

    3. Run the application:
        python3 fetch.py
        The API will be hosted at http://localhost:8000.

## API Endpoints

### Add Points
**POST `/add`**

**Request Body:**
```json
{
 "payer": "DANNON",
 "points": 300,
 "timestamp": "2022-10-31T10:00:00Z"
}
```
**Response**

    Status: 200 OK

### Spend Points
**POST `/spend`**

**Request Body:**
```json
{
 "points": 5000
}
```

**Response**

```json
[
    { "payer": "DANNON", "points": -100 },
    { "payer": "UNILEVER", "points": -200 },
    { "payer": "MILLER COORS", "points": -4700 }
]
```

**GET `/balance`**

**Response**

```json
{
    "DANNON": 1000,
    "UNILEVER": 0,
    "MILLER COORS": 5300
}
```

## How It Works
Adding Points:

    When points are added using /add, they are recorded in the Transaction table and also update the cumulative payer balance in the Balance table.

Spending Points:

    Points are deducted in a FIFO order based on the timestamps of the transactions. The /spend endpoint ensures that the total points deducted are distributed across transactions while maintaining compliance with available balances.

Viewing Balances:

    The /balance endpoint retrieves the current total points available for each payer from the Balance table.








 




