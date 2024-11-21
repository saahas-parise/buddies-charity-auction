# Buddies Charity Auction

Buddies Charity Auction is a full-stack web application for managing charity auctions. It allows users to list items, bid on auctions, and manage transactions, leveraging Flask, PostgreSQL, and other tools.

---

## Features

- **User Authentication**: Secure user registration and login functionality.
- **Auction Listings**: Users can create, edit, and manage auction items.
- **Bidding System**: Enables real-time bidding on auction items.
- **Database-Backed**: Uses PostgreSQL to store and manage auction data.
- **Responsive Design**: User-friendly interface built with HTML, CSS, and JavaScript.

---

## Prerequisites

Ensure the following are installed on your system:
1. **Python** (v3.8 or higher)
2. **PostgreSQL** (v12 or higher)
3. **Node.js** (v14 or higher, if needed for JavaScript assets)
4. **Poetry** (for Python dependency management)

---

## Setup Instructions

### Step 1: Clone the Repository
```bash
git clone https://github.com/saahas-parise/buddies-charity-auction.git
cd buddies-charity-auction
```

### Step 2: Install Dependencies

1. **Python Dependencies**: Use `Poetry` to install dependencies in a virtual environment:
```bash
   poetry install
```
   Enter the virtual environment:
```bash
  poetry shell
```

2. **JavaScript Dependencies** (if applicable):
```bash
  npm install
```

### Step 3: Configure Environment Variables

1. A `.flaskenv` file is automatically generated when you run `install.sh`. If you need to edit it, include the following:
```ini
   FLASK_APP=app
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   DATABASE_URL=postgresql://username:password@localhost:5432/auction
```

2. **Do not track `.flaskenv` in Git**, as it contains sensitive information.

### Step 4: Initialize the Database

1. Run the installation script:
```bash
  ./install.sh
```

2. To reinitialize the database, use:
   # db/setup.sh

### Step 5: Run the Application

1. Start the Flask server:
```bash
  flask run
```

2. Access the application at:
   - **Local Setup**: [http://localhost:8080/](http://localhost:8080/)
   - **Duke OIT Containers**: Visit the URL specific to your container (check your container dashboard).

---

## Working with the Database

- **Access the database**: Use `psql` to connect directly:
```bash
  psql auction
```

- **Reinitialize the database**: Run:
```bash
  db/setup.sh
```

- **Modifying the schema**:
  1. Update `db/create.sql` for schema changes.
  2. Update `db/load.sql` to include new data mappings.
  3. Reinitialize the database with:
```bash
  db/setup.sh
```

- **Debugging the database**: Open a second terminal, access the database using `psql`, and run queries to verify updates after interacting with the website.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgements

- Originally created for COMPSCI 316 (Database Systems).
- Adapted from Rickard Stureborg's and Yihao Hu's work and expanded for Buddies Charity Auction by Saahas Parise.

---
