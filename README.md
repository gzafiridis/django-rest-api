# Backend for a streaming service (like Netflix, Spotify etc.)

## Introduction

This is a project that I did to get my feet wet with the Django Framework and create some RESTful API endpoints. The code is documented and I have also written a suite of tests for the various functions of the API. I have used Docker to containerize the created app and Travis for CI. In this README I have instructions on how to run the app with Docker and I have fully documented the API endpoints so that you can test them out!

For this project, I decided to make some endpoints that would be useful in a streaming service. The basic entities of our API are:

- User: The users of the service
- Membership: The membership of each user, which includes the period for which it is valid, a flag that show if it is active or cancelled and the field "credits" which show how many concurrent streams the user can have open (i.e. in a video streaming service, if this number is 3 then the user of this membership can stream 3 videos at the same time)
- Invoice: A monthly invoice for each user which has a date, description, amount and status (outstanding, paid or void)
- Invoice Line: Each invoice can have many invoice lines, and each line includes its own description and amount

These are the entities for our basic system. The logic behind them is not airtight of course, as it is just a project for me to practice and learn. The implemented endpoints allows us to perform CRUD operations on invoices and invoice lines, as well as modifying the credits of a user's membership depending on how many open streams they have (check-in and check-out endpoints).

## Requirements to run the application

The only thing you need to run this project is to have Docker up and running. You can download Docker Desktop from `docker.com`.

## How to run the application

Let's get straight down to business. To start the application, go into the directory where you have downloaded the app and use the command

`$ docker-compose run -d app`

To run the tests, use the command

`$ docker-compose run app sh -c 'python manage.py test'`

The real fun starts now. Run `$ docker-compose up -d` and now go to your browser and type in the address bar http://127.0.0.1:8000/admin/core where it will take you to the django log-in page. You can create an admin user by running the command 


`$ docker-compose run app sh -c 'python manage.py createsuperuser'` and then login to see and manage the database entities of our application. You can also run

`$ docker-compose run app sh -c 'python manage.py loaddata init_db.json'`

to preload some data I have created myself so you can play around. If you load this data, you can login as admin with
- Username: *zaf@test.com*
- Password: *password*

Enjoy!

## The structure of the project and the API endpoints

Here is an overview of the most important files in the project, which contain the logic for its functionality. We have 2 main apps, the core app and the invoice app, both of which are in the 'app' folder of our root directory. The core app contains all our models for our database entities in the core/models.py file, as well as tests for those models in the tests folder (core/test_models.py). Next, we have the invoice app which includes all our RESTful API endpoints. The tests for these endpoints are in the invoice/tests folder. Let's see the endpoints in detail.

1. /invoice/invoices: This endpoint handles GET and POST requests. With GET, a list of all the invoices is returned in the response. Sample GET response if there are 2 invoices:
    ```
    [
      {
          "id": 1,
          "user": 2,
          "date": "2022-03-01",
          "status": "PAID",
          "description": "Invoice for the 3rd month of 2022",
          "amount": 15,
          "invoice_lines": [
              4
          ]
      },
      {
          "id": 2,
          "user": 3,
          "date": "2022-01-05",
          "status": "PAID",
          "description": "Invoice for the 1st month of 2022",
          "amount": 11,
          "invoice_lines": [
              3,
              2,
              1
          ]
      },
    ]
    ```
   The fields user and invoice_lines include the associated objects' id. 
  
    A POST request with the appropriate data creates a new invoice. Sample JSON payload for POST request:
    ```
    {
      "user": 1,
      "date": "2022-04-13",
      "status": "OUT",
      "description": "Invoice for the 4th month of 2022",
      "amount": 15,
    }
    ```
    The only required fields are the user and the status, other fields are populated with default values if omitted. The status fields only accepts the values 'OUT', 'PAID', 'VOID' for outstanding, paid and void status respectively. The response contains the created invoice's fields, as they are shown on GET's response.

2. /invoice/invoices/{invoice id}: This endpoint handles GET, PUT, PATCH and DELETE requests. A DELETE request deletes the invoice, as well as its invoice lines, because of their relationship in the database. A GET request to a url with a valid invoice id returns a single invoice but it also has the fields of each of its lines. Sample GET response on /invoice/invoices/1:
    ```
    {
      "id": 1,
      "user": 2,
      "date": "2022-03-01",
      "status": "PAID",
      "description": "Invoice for the 3rd month of 2022",
      "amount": 15,
      "invoice_lines": [
          {
              "id": 4,
              "invoice": 1,
              "amount": 15,
              "description": ""
          }
      ]
    }
    ```
    A PUT request with the appropriate data can update its fields (other than the invoice lines). Sample JSON payload for PUT request:
    ```
    {
      "user": 1,
      "status": "PAID",
      "description": "Changed description with PUT",
    }
    ```
    The only required fields for PUT are the user and the status. Otherwise, we can use the PATCH method and only provide the fields we need to update in the payload. The response either for PUT or for PATCH contains the invoice, as it is shown on GET's response.

3. /invoice/invoice_lines: This endpoint handles GET and POST requests, similarly with /invoice/invoices. GET returns a list of all invoice_lines, while POST creates a new invoice line. Sample GET response with 4 invoice lines:
    ```
    [
        {
            "id": 1,
            "invoice": 3,
            "amount": 3,
            "description": ""
        },
        {
            "id": 2,
            "invoice": 3,
            "amount": 4,
            "description": ""
        },
        {
            "id": 3,
            "invoice": 3,
            "amount": 4,
            "description": ""
        },
        {
            "id": 4,
            "invoice": 1,
            "amount": 15,
            "description": ""
        }
    ]
    ```
   The invoice field contains the associated invoice id. We can also send GET requests with the 'invoice' parameter assigned to an invoice id, and then the list of invoice lines for this particular invoice only get retrieved. In the above example, the GET response on /invoice/invoice_lines/?invoice=3 would be:
     ```
     [
        {
            "id": 1,
            "invoice": 3,
            "amount": 3,
            "description": ""
        },
        {
            "id": 2,
            "invoice": 3,
            "amount": 4,
            "description": ""
        },
        {
            "id": 3,
            "invoice": 3,
            "amount": 4,
            "description": ""
        }
    ]
     ```
    The only required field to crate a new invoice line with POST is the invoice. Sample JSON payload for POST request:
    ```
    {
      'invoice': 1,
      'amount': 3,
      'description': "A new invoice line"
    }
    ```
    The response contains the created invoice line's fields, as they are shown on GET's response.

4. /invoice/invoice_lines/{invoice line id}: This endpoint handles GET, PUT, PATCH and DELETE requests and its functionality is exactly like that of /invoice/invoices/{invoice id}, except that now it regards a single invoice line. Sample GET response on /invoice/invoice_lines/1:
    ```
    {
    "id": 1,
    "invoice": 3,
    "amount": 3,
    "description": ""
    }
    ```
    A PUT request can update the invoice line's fields. The only required field is the invoice. Sample JSON payload for PUT request:
    ```
    {
    "invoice": 2,
    "amount": 4,
    "description": "changed invoice line description with PUT"
    }
    ```
    A PATCH request can update only the provided fields and does not require any particular field. The response either for PUT or for PATCH contains the invoice line, as it is shown on GET's response.

5. /checkin: This endpoint handles POST requests that contain a valid user's id. When it receives such a request, the user with that id is considered to start a stream. This means that if the user has a valid membership, a credit will be subtracted from his mebership and a new invoice line will be added to his monthly invoice (if an invoice for the current month doesn't exist for this user, it will be created). Sample JSON payload for POST:
    ```
    {
      "id": 1
    }
    ```
    In the response of the POST request, the created invoice line's id is returned, along with its associated invoice id:
    ```
    {
    "invoice_id": 2,
    "invoice_line_id": 6
    }
    ```
    
6. /checkout: This endpoint handles POST requests that contain a valid user's id, like the /checkin endpoint. When it receives a valid request, the corresponding user is considered to stop an open stream. This means that if the user has a valid membership, a credit will be added back to his mebership and a new invoice line will be added to his monthly invoice. Sample JSON payload for POST:
    ```
    {
      "id": 1
    }
    ```
    In the response of the POST request, the created invoice line's id is returned, along with its associated invoice id:
    ```
    {
    "invoice_id": 2,
    "invoice_line_id": 7
    }
    ```

## Try it out!

That was a presentation of the endpoints and their functionality. You are welcome of course to try them out to your heart's content and also go into the code to have a clear view of their functionality. The Django REST framework provides a web browsable API for testing the responses of your endpoints to various HTTP requests, so if you navigate to the endpoints from your browser (ex. http://127.0.0.1:8000/invoice/invoices) you can make requests and see their responses. Hope you like it!
