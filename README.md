# Flask Dictionary App

This is a Flask-based web application that allows users to create and search their own dictionary with text definitions, images, voice notes, and links.

## Features

- **Add Words**: Users can add words along with text definitions, images, voice notes, and links.
- **Search Functionality**: Retrieve saved words along with their associated data.
- **Database Storage**: Uses SQLite for efficient word storage.
- **File Uploads**: Supports image and voice note uploads.
- **User-Friendly Interface**: Simple Bootstrap-based UI.

## Installation & Setup

1. **Clone the Repository**
    ```sh
    git clone https://github.com/your-username/flask-dictionary-app.git
    cd flask-dictionary-app
    ```

2. **Create a Virtual Environment**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```

3. **Install Dependencies**
    ```sh
    pip install flask
    ```

4. **Run the Application**
    ```sh
    python app.py
    ```
    The app will be available at [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

## Deployment on Render

1. Push the project to GitHub.
2. Go to Render and create a new Web Service.
3. Connect your GitHub repository.
4. Set the Start Command to:
    ```sh
    python app.py
    ```
5. Deploy and access your hosted web app!

## Folder Structure

```
flask-dictionary-app/
│── static/uploads/       # Stores uploaded images and voice files
│── templates/            # HTML templates (index.html, search.html)
│── app.py                # Main Flask application
│── dictionary.db         # SQLite database
│── README.md             # Documentation
```

## Future Enhancements

- User Authentication for private word collections.
- API Integration for exporting dictionary data.
- Better UI Enhancements for improved user experience.

## License

This project is licensed under the MIT License.
