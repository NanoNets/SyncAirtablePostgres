# Sync Airtable to Postgres 

This is a utility to sync tables from Airtable to Postgres

## Requirements

Docker

Docker Compose

## Installation

### Docker
On a command line run
```
curl -fsSL https://test.docker.com -o test-docker.sh

sh test-docker.sh
```

### Docker Compose
On a command line run
```
sudo wget --output-document=/usr/local/bin/docker-compose "https://github.com/docker/compose/releases/download/$(wget --quiet --output-document=- https://api.github.com/repos/docker/compose/releases/latest | grep --perl-regexp --only-matching '"tag_name": "\K.*?(?=")')/run.sh"

sudo chmod +x /usr/local/bin/docker-compose

sudo wget --output-document=/etc/bash_completion.d/docker-compose "https://raw.githubusercontent.com/docker/compose/$(docker-compose version --short)/contrib/completion/bash/docker-compose"
```

## Usage

### 0. Clone the Repostiory

Run the following on your command line
```
git clone https://github.com/sjain07/SyncAirtablePostgres.git
cd SyncAirtablePostgres
```

### 1.  Edit db-params.json
Add your database connection parameters

### 2. Add the list of tables you want to sync and your api key to airtable.json

You have to add the `BaseId` and `Table Name`

To get Base Id:

#### a. Go to [Airtable API](https://airtable.com/api)

#### b. Click on the Base of your choice, it will take you to a url looking like:

https://airtable.com/appnUr44xd9unezyt/api/docs#curl/introduction

`appnUr44xd9unezyt` is your `BaseId` and within that `BaseId` pick the table you want (like `Epics`) to sync

#### c. add to airtable.json
```
"bases": {
    "appnUr44xd9unezyt" : ["Epics"]
}
```

#### d. add your Airtable API Key to airtable.json

https://support.airtable.com/hc/en-us/articles/219046777-How-do-I-get-my-API-key-


### 3. Run with Docker Compose
```
docker-compose up -d --build
```

It will sync your Airtable Table to the Postgres DB that you specified every 5 minutes.

## Use Cases
We at [Nanonets](https://nanonets.com) use it to Sync data about Scrum, OKRs, Failures, Errors, CRM that we store in Airtable.
We also support our customers who want data written back to Airtable from Invoices they send to us for processing [Invoice Processing](https://nanonets.com/invoice-ocr)

## Limitations

1. Currently only supports numbers and dates.
2. Aggressively changes field and table names to avoid Postgres keywords, this could be much lighter

## To DO

1. Add support for JSON, Lists, Boolean  etc. Currently only supports numbers and dates.
2. Autodetect Bases and Tables (Requires Airtable Meta API Access)

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)