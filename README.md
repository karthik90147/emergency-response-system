# Emergency Response System

A comprehensive Django-based platform for managing emergency incidents, coordinating responders, and providing real-time analytics for emergency services.

## Overview

The Emergency Response System is designed to streamline the process of reporting, tracking, and responding to various types of emergencies. The system provides a centralized platform for emergency control rooms to manage incidents efficiently and dispatch appropriate resources.

## Features

- **Incident Management**
  - Report and track various types of emergencies (Fire, Medical, Accident, Crime, Natural Disaster)
  - Severity classification (Low, Medium, High, Critical)
  - Real-time status updates (Reported, Dispatched, In Progress, Resolved, Closed)
  - Location tracking with GPS coordinates

- **Responder Coordination**
  - Manage emergency response teams
  - Track responder availability and location
  - Assign responders to incidents based on proximity and expertise

- **Dashboard & Control Room**
  - Real-time overview of active incidents
  - Resource allocation management
  - Interactive maps for incident visualization

- **Analytics**
  - Response time metrics
  - Incident type distribution
  - Geographic hotspot analysis
  - Performance reporting

- **AI Integration**
  - Image detection for emergency classification
  - AI-powered incident severity assessment
  - Geo-location utilities

## Technology Stack

- **Backend**: Django (Python)
- **Database**: SQLite (Development), can be configured for PostgreSQL in production
- **Frontend**: HTML, CSS, JavaScript
- **Maps Integration**: Leaflet.js
- **AI Components**: YOLOv8 for image detection

## Project Structure

```
emergency_response_system/
├── analytics/            # Analytics and reporting functionality
├── dashboard/            # Control room dashboard views
├── emergency_system/     # Main Django project settings
├── incidents/            # Core incident management functionality
│   ├── models.py         # Data models for incidents
│   ├── views.py          # Views for incident management
│   ├── api_views.py      # API endpoints
│   └── utils/            # Utility functions including AI components
├── responders/           # Responder management functionality
├── static/               # Static files (CSS, JS)
├── templates/            # HTML templates
│   ├── analytics/
│   ├── dashboard/
│   └── incidents/
└── media/                # User-uploaded content
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/emergency_response_system.git
   cd emergency_response_system
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

7. Access the application at http://127.0.0.1:8000/

## Usage

1. **Admin Interface**: Access the Django admin at `/admin` to manage all system data
2. **Incident Reporting**: Use the home page to report new incidents
3. **Incident Tracking**: Track incident status and updates at `/incidents/track/<incident_id>`
4. **Control Room**: Access the control room dashboard at `/dashboard/control-room`
5. **Analytics**: View system analytics at `/analytics/dashboard`

## Configuration

- Modify `emergency_system/settings.py` for environment-specific configurations
- For production deployment, ensure to set `DEBUG=False` and configure proper security settings

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

For any questions or support, please contact [your-email@example.com](mailto:your-email@example.com).