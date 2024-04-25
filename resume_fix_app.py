import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QMessageBox, QFileDialog, QSplitter)
from openai import OpenAI
from config import API_KEY
import docx
from datetime import datetime

client = OpenAI(api_key=API_KEY)

class ResumeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.conversation_log = []

    def initUI(self):
        self.layout = QVBoxLayout()
        self.splitter = QSplitter(self)
        #splitter2 = QSplitter(self)

        # Label for instructions
        self.label = QLabel("Enter the Job Description:")
        self.layout.addWidget(self.label)

        # Text box for job description input
        self.job_description_input = QTextEdit()
        self.layout.addWidget(self.job_description_input)

        # Button to process the job description
        self.process_button = QPushButton('Extract Keywords (Costs Will Be Incurred)')
        self.process_button.clicked.connect(self.process_job_description)
        self.layout.addWidget(self.process_button)

        # Text box for displaying keywords
        self.keywords_output = QTextEdit()
        self.keywords_output.setReadOnly(True)
        self.splitter.addWidget(self.keywords_output)

        # Set the layout and window
        self.setLayout(self.layout)
        self.setWindowTitle('Resume Tailoring App')

        # Text box for new experiences input
        self.new_experiences_input = QTextEdit()
        self.new_experiences_input.setPlaceholderText("Enter additional experiences here...")  # Optional: set placeholder text
        self.new_experiences_input.setHidden(True)  # Initially hidden
        #self.new_experiences_input.setHidden(False)
        self.layout.addWidget(self.new_experiences_input)
        self.splitter.addWidget(self.new_experiences_input)
        #splitter2.addWidget(self.new_experiences_input)

        # Submit button for new experiences, initially hidden
        self.submit_experiences_button = QPushButton('Submit New Experiences')
        self.submit_experiences_button.setHidden(True)
        self.submit_experiences_button.clicked.connect(self.submit_new_experiences)
        self.layout.addWidget(self.submit_experiences_button)
        #self.submit_experiences_button.setHidden(False)
        self.splitter.addWidget(self.submit_experiences_button)
        #splitter2.addWidget(self.submit_experiences_button)


        self.layout.addWidget(self.splitter)
        #self.layout.addWidget(splitter2)

        #self.setGeometry(300, 300, 600, 500)
        screen = QApplication.primaryScreen().geometry()
        self_width = 1600  
        screen_height = screen.height()
        self.setGeometry(100, 0, self_width, screen_height)

    def process_job_description(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_interaction(f"({current_time}) Processing Job Description...\n")

        self.job_description = self.job_description_input.toPlainText()
        self.log_interaction("JD Entered: \n" + self.job_description)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system",
                 "content": "Your task is to find and list all of the keywords and key skills that are present in "
                            "a job description using ATS standards. Please write nothing other than the keywords "
                            "and key skills from this job description in your response."},
                {"role": "user", "content": self.job_description}
            ]
        )


        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_interaction(f"({current_time})\n")

        self.keywords = response.choices[0].message.content.strip().split(",")
        self.keywords_output.setPlainText("Keywords Extracted: \n" + "\n".join(self.keywords))
        self.log_interaction("Keywords Extracted: \n" + "\n".join(self.keywords))
        self.prompt_next_step()

    def prompt_next_step(self):
        reply = QMessageBox.question(self, 'Next Step', "Do you want to upload your resume for processing? (Costs Will Be Incurred)",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.upload_resume()

    def upload_resume(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Resume File", "", "Word Documents (*.docx);;All Files (*)")
        if file_name:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.log_interaction(f"\n({current_time}) Uploading Resume...")

            self.log_interaction("\nResume Uploaded: " + file_name)
            key_skills, work_experience = self.load_resume_sections(file_name)
            self.process_resume(key_skills, work_experience)

    def load_resume_sections(self, file_path):
        doc = docx.Document(file_path)
        key_skills_text = ''
        work_experience_text = ''
        capture_skills = False
        capture_experience = False

        # List of headings that should terminate capturing experience
        end_of_experience_markers = ["Education", "Certifications", "Publications", "References"]

        for para in doc.paragraphs:
            # Check if the paragraph contains any underlined text
            is_underlined = any(run.underline for run in para.runs if run.underline)

            if para.style.name.startswith('Heading') or is_underlined:
                if 'Key Skills' in para.text:
                    capture_skills = True
                    key_skills_text += para.text + '\n'
                elif 'Work Experience' in para.text:
                    capture_experience = True
                    capture_skills = False  # Stop capturing skills if we start capturing experience
                elif 'Panorama Education, Boston, MA (Remote)' in para.text:
                    capture_experience = True
                    capture_skills = False
                elif any(marker in para.text for marker in end_of_experience_markers):
                    capture_experience = False

            # Add text to respective sections if we're in capture mode
            if capture_skills and para.text.strip() != '':
                key_skills_text += para.text + '\n'
            if capture_experience and para.text.strip() != '':
                work_experience_text += para.text + '\n'

            key_skills_text = key_skills_text.replace('Key Skills', '').strip()
            work_experience_text = work_experience_text.replace('Work Experience', '').strip()

        key_skills_final = "Key Skills:\n" + "\n".join(skill.strip() for skill in key_skills_text.split(" • "))
        work_experience_final = "\nWork Experience:\n" + "\n".join(work_experience_text.split("\n"))
        
        return key_skills_final, work_experience_final
    

    def process_resume(self, key_skills, work_experience):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_interaction(f"\n\n({current_time}) Processing Resume...")
        
        my_resume = f"Key Skills:\n{key_skills}\n\nWork Experience:\n{work_experience}"
        response = client.chat.completions.create(
            model="gpt-4-turbo-2024-04-09",
            #model="gpt-3.5-turbo-0125",
            messages = [{"role": "system",
                        "content": """Your task is to take a list of keywords and key skills and then look at my resume text (which contains my key skills and my work experience) and remove anything from my resume that
                        doesn't match or have anything to do with the keywords and key skills. Please only write the skills and work experience that match the keywords and key skills from the job description.
                        And if you see any ways to improve the wording in my resume to better match the keywords and key skills in the job description, please do so. When you're done, please write the skills
                        and bullets in a format that I can easily use a Python split function on. More specifically, please enclose the resume section with this delimiter: '```'. This is so I will always be able to access the resume with this code: so I can will always be able to access the resume portion with this code (resume_response.split('```')[1]) """},
                        
                        {"role": "user",
                        "content": f"keywords: {self.keywords}\n\nmy resume: {my_resume}"}]
            )
        self.processed_resume = response.choices[0].message.content.split("\n")
        full_text = "\n".join(self.processed_resume)

        try:
            self.processed_resume = full_text.split('```')[1]
        except IndexError:
            print("No delimited section found.")

        self.keywords_output.append("\nProcessed Resume:\n" + self.processed_resume)
        self.log_interaction("\nProcessed Resume: " + self.processed_resume)
        self.prompt_for_review()



    def prompt_for_review(self):
        reply = QMessageBox.question(self, 'Next Step', "Do you want to review this resume against the job description? (Costs Will Be Incurred)", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.review_resume()
        else:
            self.prompt_to_save_log()




    def prompt_to_save_log(self):
        reply = QMessageBox.question(self, 'Save Conversation', 'Do you want to save the conversation log?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.save_log()


    def save_log(self):
        options = QFileDialog.Options()

        fileName, _ = QFileDialog.getSaveFileName(self, "Save Log", "", "Text Files (*.txt);;All Files (*)", options=options)

        if fileName:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_message = f"\n\nLog saved to: {fileName} at {current_time}"
            self.log_interaction(save_message)

            with open(fileName, 'w') as file:
                file.write("\n".join(self.conversation_log))



    def review_resume(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_interaction(f"\n\n({current_time}) Reviewing Resume...")

        response3 = client.chat.completions.create(
            model="gpt-4-turbo-2024-04-09",
            #model="gpt-3.5-turbo-0125",
            messages = [{"role": "system",
                        "content": """Your task is to look at my resume and this job description and let me know how well my resume matches the job description.
                        I would like you to provide a score from 0 to 100, where 0 is a poor match and 100 is a perfect match. Please provide a brief explanation of why you gave this score.
                        Additionally, please tell me which keywords and key skills from the job description are missing from my resume and how I can improve my resume to better match the job description."""},
                        
                        {"role": "user",
                        "content": f"job description: {self.job_description}\n\nmy resume: {self.processed_resume}"}]
        )

        self.review_response = response3.choices[0].message.content
        self.keywords_output.append("\nReview Response:\n" + self.review_response)
        self.log_interaction("\nReview Response:\n" + self.review_response)
        self.prompt_to_submit_experiences()
        


    def prompt_to_submit_experiences(self):
        reply = QMessageBox.question(self, 'Next Step', "Do you want to submit new experiences?", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.submit_new_experiences()
        elif reply == QMessageBox.No:
            self.prompt_to_save_log()



    def submit_new_experiences(self):
        #self.new_experiences_input.setHidden(False)  # Make the text box visible
        #self.new_experiences_input.setFocus()  # Optional: bring focus to the text box
        #self.new_experiences_input.clear()  # Optional: clear any previous text
        self.new_experiences_input.setHidden(False)
        self.submit_experiences_button.setHidden(False)
        self.new_experiences = self.new_experiences_input.toPlainText()
        # if not self.new_experiences.strip():
        #     QMessageBox.information(self, 'Information', 'Please enter new experiences before fixing the resume.')
        
        if not self.new_experiences:
            QMessageBox.information(self, 'Fix Resume', 'Please enter new experiences and hit submit.')
        else:
            self.prompt_to_fix_resume()






    def prompt_to_fix_resume(self):
        reply = QMessageBox.question(self, 'Fix Resume', "Do you want to fix this resume? (Costs Will Be Incurred)", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.fix_resume()
        elif reply == QMessageBox.No:
            self.prompt_to_save_special_gpt_log()


    def prompt_to_save_special_gpt_log(self):
        reply = QMessageBox.question(self, 'Save Special Log', "Do you want to save the special log for GPT?", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.save_special_log_for_gpt()

    def save_special_log_for_gpt(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_interaction(f"\n\n({current_time}) Saving ChatGPT Prompt...")

        content = (
        "Your task is to read my resume, a job description, a set of recommendations "
        "I received for my resume regarding this job description, and a list of my experiences that "
        "are currently not present in my resume. After reading these, please write the relevant "
        "experiences from my list of experiences into my resume in a way that makes sense and "
        "is easy for recruiters to read and interpret. For each of the bullets that you add "
        "to the resume, please keep the same level of succinctness that is present in the "
        "bullets in the current resume. Please also make sure to include the experiences "
        "in the correct sections and jobs of my resume."
        )

        content2 = f"job description:\n{self.job_description}\n\nmy resume:\n{self.processed_resume}\n\nrecommendations:\n{self.review_response}\n\nexperiences not on resume:\n{self.new_experiences}"
        self.log_interaction(f"\nPrompt for ChatGPT: \n{content}\n\n{content2}")
        self.keywords_output.append(f"\n\nPrompt for ChatGPT: \n{content}\n\n{content2}")
        self.save_log()




    def fix_resume(self):
        self.keywords_output.append("\nNew Experiences:\n" + self.new_experiences)
        self.log_interaction("\nNew Experiences: \n" + self.new_experiences)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_interaction(f"\n\n({current_time}) Fixing Resume...")

        response4 = client.chat.completions.create(
        #model="gpt-4-turbo-2024-04-09",
        model="gpt-3.5-turbo-0125",
        messages = [{"role": "system",
                    "content": """Your task is to read my resume, a job description, and a list of my experiences that are currently not present in my resume.
                    After reading these, please write the relevant experiences from my list of experiences into my resume in a way that makes sense and is easy for recruiters to read and 
                    interpret. For each of the bullets that you add to the resume, please keep the same level of succinctness that is present in the bullets in the 
                    current resume. Please also make sure to include the experiences in the correct sections and jobs of my resume."""},
                    
                    {"role": "user",
                    "content": f"job description: {self.job_description}\n\nmy resume: {self.processed_resume}\n\nexperiences not on resume: {self.new_experiences}"}]
        )

        self.fixed_resume = response4.choices[0].message.content
        self.new_experiences_input.setHidden(True)
        self.keywords_output.append("\nFixed Resume:\n" + self.fixed_resume)
        self.log_interaction("\nFixed Resume:\n" + self.fixed_resume)
        self.prompt_to_save_log()


    def log_interaction(self, text):
        self.conversation_log.append(text)

    # def export_conversation_to_pdf(self):
    #     # Implement the export functionality here
    #     print("\n".join(self.conversation_log))

def main():
    app = QApplication(sys.argv)
    ex = ResumeApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()