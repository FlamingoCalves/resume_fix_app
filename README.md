# Resume Fixer App
The Resume Fixer App is designed to enhance and tailor your resume to specific job descriptions using OpenAI's API. This Python application uses PyQt5 for a GUI version and provides a flexible class module for non-GUI usage, making it adaptable for various programming needs.

## Features
- **Extract Keywords**: Automatically extracts important keywords from job descriptions (JD).
- **Resume Processing**: Processes your resume to highlight relevant experiences and skills matching the JD.
- **Interactive Review and Enhancement**: Reviews the processed resume, provides a relevancy score, and identifies missing skills or experiences.
- **Dynamic Resume Updating**: Allows users to input new experiences, which are then integrated into the resume effectively.
- **Logging**: Logs all operations and allows saving the log for record-keeping.
- **GUI and Non-GUI Support**: Available in both a GUI version for interactive use and a class-only version for integration into other Python scripts.

## Project Structure
- `resume_fixer_app.py`: The main application with a PyQt5 GUI.
- `resume_app_class_only.py`: A Python class providing the core functionalities without a GUI.
- `config_example.py`: Example configuration file for setting up your OpenAI API key.
- `requirements.txt`: Contains all necessary Python packages for the application.

## Setup
1. **Clone the repository:**
```bash
git clone https://github.com/FlamingoCalves/resume_fix_app.git
cd resume-fixer-app
```
2. **Install dependencies:**
```bash
pip install -r requirements.txt
```
3. **Obtaining an OpenAI API Key:**
- Visit [OpenAI API](https://platform.openai.com/api-keys) and sign up or log in.
- Navigate to API keys section and create a new API key.
- Copy and paste the generated API key into your config.py file.

4. **API Key Configuration:**
- Copy config_example.py to config.py.
- Replace "enter_openai_api_key_here" with your actual OpenAI API key in config.py.

## Costs Warning
**Important:** Running this application will incur costs associated with the OpenAI API usage. Make sure to review the [pricing detail](https://openai.com/pricing) on OpenAI's website to understand the charges and manage your usage accordingly.

## Running the Application:
- **For GUI version:** 
```bash
python resume_fixer_app.py
```
- **For non-GUI usage:** See examples provided in resume_app_class_only.py.

## How It Works
1. **User Inputs a Job Description:** Start by entering the job description into the application.
2. **Keyword Extraction:** The application extracts and logs keywords from the JD.
3. **Resume Processing Inquiry:** The user is asked if they want their resume processed against the JD.
4. **Resume Processing:** If confirmed, the resume is processed to align more closely with the JD.
5. **Resume Review:** The processed resume is reviewed and scored based on how well it matches the JD.
6. **Fixing the Resume:** Users can input new experiences which are integrated into the resume.
7. **Finalizing:** The changes are logged, and the user can save this log.