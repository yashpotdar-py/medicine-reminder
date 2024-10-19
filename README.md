# Medicine Reminder Application

## Overview
This project is a Medicine Reminder Application that helps users manage their medication schedules and set reminders. It includes features for user authentication, storing medicine schedules, and setting up reminders.

## Features
- User registration and login
- Store and manage medicine schedules
- Set reminders for taking medicines
- Speech recognition capability (experimental)

## File Structure
```
.
├── .gitignore
├── app.py
├── auth.db
├── database.db
├── db.py
├── LICENSE
├── Name of Medicine.txt
├── README.md
├── recognized_speech.txt
├── requirements.txt
├── test.pdf
└── test.py
```

## Setup and Installation
1. Clone the repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
1. Run the main application:
   ```
   streamlit run app.py
   ```
2. Register a new user or login with existing credentials
3. Add your medicine schedules and set reminders

## Database Schema
The application uses SQLite for data storage. The database includes the following tables:
- `users`: Stores user authentication information
- `medicine_schedule`: Stores medicine schedules for each user
- `reminders`: Stores reminder settings for medicines

## Speech Recognition (Experimental)
The `test.py` file includes an experimental feature for speech recognition using Streamlit. To use this feature:
1. Run the Streamlit app:
   ```
   streamlit run test.py
   ```
2. Click the "Start Recording" button and speak
3. The recognized speech will be displayed and saved to `recognized_speech.txt`

## Contributing
Contributions to improve the application are welcome. Please follow these steps:
1. Fork the repository
2. Create a new branch
3. Make your changes and commit them
4. Push to your fork and submit a pull request

## License
This project is licensed under the terms of the LICENSE file included in the repository.
