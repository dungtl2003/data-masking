CREATE TABLE person (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    gender VARBINARY(255) NOT NULL,
    city VARBINARY(255) NOT NULL,
    phone_number VARBINARY(255) NOT NULL,
    private_key VARBINARY(255) NOT NULL,
    decrypt_frequency VARBINARY(255) NOT NULL
);

CREATE TABLE person_refresh_token (
    id SERIAL PRIMARY KEY,
    token VARCHAR(255) NOT NULL,
    person_id BIGINT UNSIGNED NOT NULL,
    FOREIGN KEY (person_id) REFERENCES person(id) ON DELETE CASCADE
);
