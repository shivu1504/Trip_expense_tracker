# Trip Expense Tracker

A simple and modern web application for managing group trip expenses.

The app helps a group create a trip, add members, record expenses, split bills equally, and track how much each member has paid and how much they are responsible for.

## Features

- Create a trip
- Add multiple trip members
- Manage trip members
- Add and manage expenses
- Select who paid for an expense
- Split every expense equally
- Split between:
  - All Members
  - Except selected members
- Track total amount paid by each member
- Track total expense share of each member
- View trip expenses
- Trip memory experience with photos
- Background music during the trip memory
- Responsive design for desktop and mobile
- Dark cinematic UI
- MySQL database

## Tech Stack

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python
- Flask

### Database
- MySQL

### Development
- VS Code
- Git
- GitHub

## Project Structure

```text
trip-expense-tracker/
│
├── database/
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   ├── icons/
│   │
│   ├── js/
│   │   └── script.js
│   │
│   ├── music/
│   │   └── memory-music.mp3
│   │
│   ├── manifest.json
│   └── service-worker.json
│
├── templates/
│   ├── index.html
│   ├── trip.html
│   ├── manage_members.html
│   ├── manage_expenses.html
│   ├── complete_trip.html
│   └── trip_memory.html
│
├── .gitignore
├── app.py
├── database.py
├── readme.md
└── requirements.txt