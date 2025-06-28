# Shelf Timer App - Capstone project for BUSA 649
**AI-Enhanced Inventory Management and Sustainability Dashboard**

## Part 1: Project Overview

### Purpose and Scope

Shelf Life Inc. is a web-based application designed to help users monitor and manage their personal or household food inventory while promoting sustainable practices and reducing waste. Built using Streamlit, the system provides a lightweight but powerful user interface that connects to a Google Sheets backend, enabling collaborative, cloud-based inventory tracking. Gemini Pro is used for SHELI, your virtual recipe finding assistant. 

This project was initiated in the context of a digital transformation and sustainability initiative. The application specifically addresses key real-world challenges such as:

- Lack of visibility into food inventory across users
- High levels of food waste due to expiry
- Poor forecasting of grocery needs
- Minimal awareness of environmental (CO₂) impact at the individual level

### Objectives

The system aims to:

- Improve food usage efficiency through item-level inventory tracking
- Automatically identify items close to expiry to reduce waste
- Generate dynamic grocery lists based on real usage
- Provide CO₂ and cost savings dashboards to raise sustainability awareness
- Offer AI-generated recipes based on available ingredients

### Intended Users

The app is intended for:

- Individual households
- Roommates or families sharing an inventory
- Researchers or educators studying sustainable behavior
- Students or professionals building inventory-based AI projects

Each user logs in securely and has access only to their own inventory and metrics. This modular structure ensures both data integrity and privacy, while still maintaining a central dataset.

### Application Value

This solution offers the following practical benefits:

- Accessibility: Runs entirely in the browser using Streamlit, with zero setup for end users beyond login.
- Automation: Tracks expiry, calculates usage and waste metrics automatically.
- Accountability: Shows cost and environmental impact to encourage conscious choices.
- Adaptability: Users can export, re-upload, or even reconfigure their data pipeline.

# Part 2: Installation and Setup

This section provides complete guidance on how to install, configure, and run the Shelf Timer application, both in local development and cloud-hosted environments.

---

## 1. Prerequisites

Ensure the following tools and resources are available before installation:

### System Requirements
- Operating System: Windows 10+, macOS 12+, or Linux (Ubuntu 20.04+)
- Python: Version 3.9 or later
- pip: Python package manager
- Git (optional): To clone repositories

### Required Accounts and Credentials
- Google Account: Needed for access to Google Sheets API
- Hugging Face Account: Required only for deployment on Hugging Face Spaces

### External Files (Provided Separately)
- `secrets`: Secure credentials for accessing your Google Sheet & Gemini Pro API Keys
- `requirements.txt`: List of Python dependencies
- `streamlit_app.py`: Main Streamlit application logic
- Google Sheet URL shared with the appropriate service account

---

## 2. Installation Steps (Local Deployment)

### Step 1: Clone or Download the Repository
Download the app files or clone from a version control repository:
```bash
https://huggingface.co/spaces/hgopalan/shelf_timer/tree/main
cd shelf-timer
```

### Step 2: Create and Activate a Virtual Environment
To avoid dependency conflicts:
```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate         # Windows
```

### Step 3: Install Python Dependencies
Use the `requirements.txt` to install necessary libraries:
```bash
pip install -r requirements.txt
```
If you are missing `requirements.txt`, manually install:
```bash
pip install streamlit pandas gspread oauth2client matplotlib openpyxl
```

---

## 3. Credential Configuration (Google Sheets & Gemini Pro)

The `Secrets` tab enables secure communication with Google Sheets & Gemini Pro.

### To Set Up:
1. Log into your Google Cloud Console.
2. Enable:
   - Google Sheets API and Gemini Pro API Key
3. Add the API keys to the `secrets` tab on the space.
5. Share your Google Sheet with the service account email (e.g., `---------.-------------.com`) with **Editor** rights.
For this project: emailemailemail@gmail.com
                passwordpasswordpassword

---

## 4. Running the App Locally

To start the Streamlit application:
```bash
streamlit run streamlit_app.py
```
After a few seconds, your browser will automatically open the app interface at:
```
http://localhost:8501
```

If not, copy the URL displayed in the terminal manually into your browser.

---

## 5. Hugging Face Deployment

To deploy on Hugging Face Spaces:

1. Create a new Space on Hugging Face as a **"Streamlit"** app.
2. Upload:
   - `streamlit_app.py`
   - `requirements.txt`
   - `credentials.pkl`
   - `shelf_timer_logo.png`
3. Commit changes.
4. Wait ~3–5 minutes for Hugging Face to build and deploy the app.
5. Share the live space URL with users.

_Example:_  
[https://huggingface.co/spaces/hgopalan/shelf_timer](https://huggingface.co/spaces/hgopalan/shelf_timer)

---

## 6. Deployment Recommendations

- **Secure credentials**: Do not expose `.pkl` or `.json` files publicly.
- **Environment Variables**: For production, shift to `.env` files or secrets storage.
- **Access Control**: Hugging Face Spaces currently allows public access; restrict by token for private versions.

# Part 3: Usage and Example

## Overview

This section provides detailed guidance on how to interact with the Shelf Life Inc. application. It includes instructions for logging in, navigating the key features, and utilizing the LLM assistant. This serves as a hands-on training guide for both new and returning users.

---

## Credentials and Access

To access the Shelf Life Inc. web app, go to the [Hugging Face Space](https://huggingface.co/spaces/hgopalan/shelf_timer).

**Username Options:**
- `snackhoarder`
- `canofbeans`
- `hungryhippo`

**Password:**
- `password`

> Note: All users share the same password. User data is isolated and filtered by username.

---

## Key Features and Tabs

Once logged in, you will see several navigational tabs at the top of the interface:

### 📅 Shelf Life Timer
- Displays items approaching or past expiry based on current date.
- Helps in prioritizing usage and reducing waste.
- Automatically flags items with warning badges.

### ➖ Quantities
- Allows you to manually subtract quantity from an inventory item.
- You can also mark an item as “trashed” to log it as waste.
- Dropdowns are searchable and auto-populated with your inventory data.

### 🛒 Smart Grocery List
- Automatically generates a grocery list based on depleted stock.
- Rounds up item quantity for practical usability.
- Excludes items that have reached zero and avoids duplicate recommendations.

### 📊 Dashboard
- Provides a visual summary of:
  - Most used and wasted items
  - CO₂ impact trends
  - Sustainability metrics (money saved, emissions reduced)
- KPIs shown:
  - Unique items
  - Total entries
  - Expired / Expiring soon
  - Total savings

---

## Example Use Case: Inventory Training Walkthrough

### Scenario: You are `snackhoarder`, and you’ve just finished a shopping trip.

1. **Login** to the app using:
   - Username: `snackhoarder`
   - Password: `password`

2. **Navigate to “Subtract Quantity” tab:**
   - Select “Tomatoes”
   - Subtract 2 units
   - Add remark: “Used in salad”
   - Save the update

3. **Go to “Grocery List” tab:**
   - Review the list of low or missing items
   - See that “Tomatoes” is now included if below threshold

4. **Visit “Dashboard”:**
   - See updated usage and waste statistics
   - View CO₂ impact and cost savings metrics

5. **Use Chat Assistant:**
   - Click on 💬 “Ask SHELI”
   - Ask: “What can I cook with tomatoes, eggs, and rice?”
   - The assistant will return AI-generated recipe suggestions

---

## Tips for Effective Use

- **Daily Routine**: Start your day by checking the expiry tab.
- **Weekly Cleanups**: Use subtract tab to remove spoiled items and log usage.
- **Grocery Planning**: Visit the grocery list tab before shopping trips.
- **Sustainability Tracking**: Monitor your emissions and savings monthly via the dashboard.
- **Educational**: Use with students or roommates to promote awareness.

---

## Summary

This section empowers users to operate the Shelf Life Inc. app independently, offering a clear process for inventory updates, usage tracking, and sustainability insights. The built-in AI assistant further enhances usability by offering context-aware support and meal planning.

# Part 4: Features and Data Sources

This section outlines the key features available in the Shelf Life Inc. application and the structure and origin of the data sources that power the system.

---

## Features

Shelf Life Inc. integrates several features tailored to support household food inventory management, minimize waste, and enhance sustainability awareness. Each module is designed to be intuitive, informative, and useful for various end users including families, students, and sustainability-focused individuals.

### 1. Expiry Alerts Tab (`📅 Shelf Life Timer`)
- Lists all food items sorted by their expiry dates.
- Flags expired items and those expiring within the next 7 days.
- Helps users prioritize consumption based on shelf life.

### 2. Subtract Quantity Tab (`➖ Quantities`)
- Allows users to manually subtract consumed or trashed quantities from inventory.
- Optional remarks field to specify whether the item was consumed, donated, or wasted.
- Updates the underlying Google Sheet or CSV in real-time.

### 3. Grocery List Tab (`🛒 Smart Grocery List`)
- Dynamically generates shopping recommendations based on user consumption trends.
- Considers current stock, past usage frequency, and expiry to suggest items.
- Filters out items with sufficient quantities remaining.

### 4. Dashboard Tab (`📊 Dashboard`)
- Provides interactive KPIs and visualizations:
  - Unique food items, money saved, CO₂ savings, expired/soon-to-expire items.
  - Pie charts for most wasted and most consumed items.
  - Sustainability level summary (Levels 0–4 based on performance).
- Enables quick diagnostics on stock health and environmental footprint.

### 5. Chat Assistant Tab (`💬 Ask SHELI`)
- AI-powered chatbot using Hugging Face integration.
- Responds to prompts such as:
  - “Give me a recipe using carrots and potatoes.”
  - “What’s the most wasted item in my stock?”
  - “How many items will expire next week?”
- Provides a natural language interface for convenience and guidance.

---

## Data Sources

The application pulls data primarily from a centralized Google Sheet which acts as a lightweight cloud database. The following columns are expected for proper functionality:

| Column Name        | Description                                              |
|--------------------|----------------------------------------------------------|
| `Username`         | Logged-in user ID                                        |
| `Food_Name`        | Name of the item in stock                                |
| `Date_of_Entry`    | Date when the item was added                             |
| `Expiry_Date`      | Expiration date                                          |
| `Quantity`         | Quantity of units available                              |
| `QUnit`            | Unit type (e.g., pack, item, kg)                         |
| `Weight`           | Approximate weight per unit                              |
| `WUnit`            | Weight unit (e.g., g, kg)                                |
| `Price`            | Cost per unit                                            |
| `Brand`            | Brand name (optional but supported)                      |
| `Remarks`          | Descriptive notes (e.g., trashed, used, donated)         |
| `CO2_Emitted`      | Estimated CO₂ footprint per item (if available)          |

The system supports backup/reload of `.csv` files when the Google Sheet fails, enabling offline usage or local testing.

---

## External Tools and Sources
- **Google Sheets API**: For real-time cloud storage and user-specific data syncing.
- **Matplotlib & Pandas**: For generating insights and visuals.
- **Streamlit**: Framework used to build and serve the user interface.
- **Hugging Face Spaces**: Hosts the LLM-based chatbot assistant.
- **OpenPyXL**: Reads `.xlsx` files when needed.
- **OAuth2Client**: Manages authorization with Google APIs.

Each of these tools has been configured to work seamlessly with minimal overhead for users while supporting advanced analytics on the backend.

# Part 5: Troubleshooting and Debugging

This section outlines common issues users and developers may encounter when using or extending the Shelf Life Inc. application, along with step-by-step resolutions and diagnostic tips. These insights aim to ensure smooth and continued operation of the platform, especially during updates or onboarding of new contributors.

---

## 1. Common User Issues

### Blank Username in Dropdown

- **Symptom**: The username dropdown is empty or displays invalid entries.
- **Cause**: The `Username` column in the Google Sheet includes blank cells or non-string values.
- **Solution**:
  - Ensure each row in the sheet includes a valid, non-empty username.
  - Add a `.dropna()` and `.strip()` in the backend to clean empty or malformed usernames:
    ```python
    usernames = df['Username'].dropna().astype(str).str.strip().unique()
    usernames = [u for u in usernames if u != '']
    ```

---

### Pie Chart or Dashboard Crash

- **Symptom**: The app crashes with `ValueError` or `TypeError` on dashboard charts.
- **Cause**: Empty or non-numeric data being passed to `matplotlib.pyplot.pie()`.
- **Solution**:
  - Validate numerical fields before plotting:
    ```python
    df = df[pd.to_numeric(df["Quantity"], errors="coerce").notnull()]
    ```

---

### Expiry Dates Not Displaying Properly

- **Symptom**: Items marked as expired do not show up or dashboard metrics display `NaT`.
- **Cause**: Date columns (`Expiry_Date`, `Date_of_Entry`) are not parsed correctly.
- **Solution**:
  - Use:
    ```python
    df["Expiry_Date"] = pd.to_datetime(df["Expiry_Date"], errors="coerce")
    ```

---

## 2. Deployment Issues

### App Not Launching on Hugging Face

- **Symptom**: App does not load or throws error logs during Hugging Face Spaces launch.
- **Cause**: Missing or misconfigured `requirements.txt`, or missing environment variable setup.
- **Solution**:
  - Ensure `requirements.txt` is uploaded.
  - Confirm the Hugging Face Space runtime is set to `Python` and `streamlit` is declared in dependencies.

---

## 3. Google Sheets Syncing Problems

### No Updates Saved

- **Symptom**: Changes made in the app are not reflected in Google Sheets.
- **Cause**: Missing write access for the service account or API rate limiting.
- **Solution**:
  - Share the sheet with the full service account email listed in your `google_credentials.json` file.
  - Verify that write methods such as `worksheet.update()` or `set_dataframe()` are being called.

---

## 4. Hugging Face Quotas and Errors

### Quota Errors or 504 Gateway Timeout

- **Symptom**: Page becomes unresponsive or operations time out.
- **Cause**: Hugging Face Free tier may restrict processing time or simultaneous users.
- **Solution**:
  - Restart the Space manually from the Hugging Face dashboard.
  - Consider migrating to a paid tier if scaling is needed.

---

## 5. General Best Practices

- Test new features with a small mock dataset before full deployment.
- Use `st.write()` and `st.exception()` liberally during development for logging.
- Structure app logic modularly to isolate faults and enhance maintainability.

---

## 6. Reporting Bugs or Requesting Help

If you encounter issues not listed above, please reach out via one of the following channels:

- **Support Email**: 
- **Development Lead**: Maria Kouider — mariakouider@mail.mcgill.ca Hari Gopalan - hari.gopalan@mail.mcgill.ca

Provide screenshots, app logs, or a copy of the dataset (with sensitive information removed) to help diagnose the problem effectively.

# Part 6: Long-Term Maintenance and Handover Strategy

## Overview

This document outlines the long-term maintenance strategy, development standards, and handover procedures for the Shelf Life Inc. Streamlit app. It ensures continuity, reliability, and secure transfer of knowledge for future maintainers and developers.

---

## 1. Maintenance Procedures

### a. Scheduled Maintenance Tasks

| Frequency  | Task                                                                 |
|------------|----------------------------------------------------------------------|
| Weekly     | Review Google Sheet sync logs and backup dataset locally.           |
| Monthly    | Validate expiry tracking formulae and AI grocery list behavior.     |
| Quarterly  | Update CO₂ conversion constants and UI/UX enhancements.             |
| Annually   | Perform code review and refactor; collect user feedback for KPIs.   |

### b. Security Guidelines

- Rotate Hugging Face tokens and Streamlit secrets annually.
- Maintain secure API key storage through environment variables.
- Share Google Sheet access on a need-to-know basis.

---

## 2. Backup & Archival

### Backup Routine

- Weekly export of current Google Sheet to a timestamped CSV file (e.g., `inventory_2025_07_01.csv`).
- Backups should be stored in a secure, access-controlled folder in Google Drive or Git LFS if versioned.

### Archival Format

- Store both `.csv` and `.parquet` versions if feasible.
- Keep a snapshot of the app version and data dictionary with each backup.

---

## 3. Codebase Organization

```
/ShelfTimer/
│
├── streamlit_app.py               # Main Streamlit app
├── requirements.txt              # Package dependencies
├── credentials.pkl               # Hugging Face credentials (if used)
├── shelf_timer_logo.png          # UI Logo
└── README.md                     # Project documentation
```

## 4. Handover Instructions

### Admin Checklist

- Transfer Hugging Face space access and credentials.
- Provide access to shared Google Sheets and backup directory.
- Share this README set and training materials.
- Schedule a Q&A session or training walkthrough.

### Developer Checklist

- Fork or clone the repository and test locally.
- Set up virtual environment and confirm Streamlit runs end-to-end.
- Validate Google Sheets access and permissions.
- Update and commit changes via Pull Request with reviews.

---

## 5. Contacts and Support

For any issues or handover assistance:

- **Primary Developer**: Maria Kouider & Hari Golapan (H&M Consulting)
- **Email**: mariakouider@mail.mcgill.ca & hari.gopalan@mail.mcgill.ca
- **Support Contact**: mariakouider@mail.mcgill.ca & hari.gopalan@mail.mcgill.ca

---

This handover strategy ensures robust transfer of operational knowledge, with backup practices and collaboration guidelines tailored to support institutional or academic continuity.
