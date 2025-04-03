# Data masking project

Small project for data masking/encryption learning purposes.

Every person can fetch all the data from the database, but only the owner of the data can see the real data. The rest of the people will see the encrypted data.

This project uses HS256 algorithm to generate JWT tokens, AES_256_GCM algorithm to encrypt the data and bcrypt to hash the passwords.

## How to run the project

You can run each service separately or use docker compose to run all the services at once.

If you want to run the services separately, you can access each service folder and check for command to run.

If you want to use docker, you need to build the images first. You can do that by running the following command (in `front/` and `server/` folder):

```bash
make dbuild
```

You also need to initialize the database. You can do that by going to the `database/` folder and running the following command:

```bash
make up # start the database
make access_db # access the database
```

Then you can copy all commands inside `database/init.sql` and paste in the terminal.

After that, you can go back to the root folder make sure you have all neccessery env files (read the [Environment variables](#environment-variables) section) and run the following command:

```bash
make up
```

The default client endpoint will be `http://localhost:3000` and the default server endpoint will be `http://localhost:8000`. You can then access the browser and go to `http://localhost:3000` to see the application.

## Environment variables

### Frontend

| Variable | Description | Required | Default value | Example value |
|----------|-------------|----------|---------------|---------------|
| SERVER_ENDPOINT | The server endpoint | Yes | | http://data-masking-server |
| NEXT_PUBLIC_API_ENDPOINT | The API endpoint | Yes | | http://localhost:8000/api/v1 |
| API_ENDPOINT | The same as `NEXT_PUBLIC_API_ENDPOINT`, but `NEXT_PUBLIC_API_ENDPOINT` is used in the client side, whereas `API_ENDPOINT` is used in the server side (they can be different when using docker) | Yes | | http://data-masking-server/api/v1 |
| AT_DURATION_MINUTES | The access token duration in minutes | No | 15 | 60 |
| RT_DURATION_MINUTES | The refresh token duration in minutes | No | 1440 | 120 |

### Server

| Variable | Description | Required | Default value | Example value |
|----------|-------------|----------|---------------|---------------|
| DB_HOST | The database host | Yes | | data-masking-db |
| DB_USER | The database user | Yes | | admin |
| DB_PASSWORD | The database password of the user | Yes | | somepass |
| DB_DATABASE | The database name | Yes | | data-masking |
| JWT_SECRET | The secret key for JWT | Yes | | secret |
| ORIGINS | The allowed origins for CORS | No | | http://localhost:3000 |
| MASTER_KEY | The master key for encryption (need to be 64 characters long) | Yes | | 1234567890123456789012345678901234567890123456789012345678901234 |
| SUBKEY_ROTATION_COUNTER | The subkey rotation counter for encryption | Yes | | 5 |
| PORT | The port for the server | No | 8200 | 8000 |

### Database

| Variable | Description | Required | Default value | Example value |
|----------|-------------|----------|---------------|---------------|
| MYSQL_ROOT_PASSWORD | The root password for the database | Yes | | rootpass |
| MYSQL_DATABASE | The database name | Yes | | data-masking |
| MYSQL_USER | The database user | Yes | | admin |
| MYSQL_PASSWORD | The database password of the user | Yes | | somepass |

If you want to use docker compose, you have to create `.env.client`, `.env.server` and `.env.db` files in the root folder with the following content:

```bash
# .env.client
SERVER_ENDPOINT=http://data-masking-server
NEXT_PUBLIC_API_ENDPOINT=http://localhost:8000/api/v1
API_ENDPOINT=http://data-masking-server/api/v1

# .env.server
DB_HOST=your_db_host
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_DATABASE=your_db_name
JWT_SECRET=your_jwt_secret
ORIGINS=http://data-masking-client,http://localhost,http://localhost:3000
MASTER_KEY=your_master_key
SUBKEY_ROTATION_COUNTER=your_subkey_rotation_counter
PORT=80

# .env.db
MYSQL_ROOT_PASSWORD: your_db_root_password
MYSQL_DATABASE: your_db_name
MYSQL_USER: your_db_user
MYSQL_PASSWORD: your_db_password
```
