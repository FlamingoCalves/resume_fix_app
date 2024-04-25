from openai import OpenAI
from datetime import datetime
import docx

class ResumeProcessor:
    def __init__(self, openai_client):
        """
        Initializes the ResumeProcessor with an OpenAI client.
        Args:
            openai_client: An instance of the OpenAI API client to be used for API calls.
        """
        self.client = openai_client
        self.conversation_log = []

    def process_job_description(self, job_description, verbose=True):
        """
        Extracts keywords from a given job description using the OpenAI API.
        Args:
            job_description: A string containing the job description from which to extract keywords.
            verbose: A boolean that determines if the function should return a verbose response.
        Returns:
            A list of extracted keywords.
        """

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_interaction(f"({current_time}) Processing Job Description...\n")
        self.job_description = job_description
        """ Process the job description to extract keywords using OpenAI's API. """
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system",
                 "content": "Your task is to find and list all of the keywords and key skills that are present in "
                            "a job description using ATS standards. Please write nothing other than the keywords "
                            "and key skills from this job description in your response."},
                {"role": "user", "content": self.job_description}
            ]
        )
        self.keywords = response.choices[0].message.content.strip().split(",")
        if verbose:
            self.keywords = (f"Keywords Extracted: \n{self.keywords}")
        else:
            self.keywords = self.keywords
        return self.keywords
    
    def load_resume_sections(self, resume_file_path):
        """
        Loads and parses specific sections (Key Skills, Work Experience) from a given resume file.
        Args:
            resume_file_path: A string path to the resume file to be processed.
        Returns:
            Two strings containing formatted Key Skills and Work Experience sections.
        """

        doc = docx.Document(resume_file_path)
        key_skills_text = ''
        work_experience_text = ''
        capture_skills = False
        capture_experience = False

        stop_sections = ['Education', 'Projects', 'Certifications', 'Skills', 'Languages', 'Interests', 'References']

        for para in doc.paragraphs:
            if para.text == 'Key Skills':
                capture_skills = True
                continue

            if para.text == 'Work Experience':
                capture_skills = False
                capture_experience = True
                work_experience_text += "Work Experience: \n"
                continue

            elif para.text in stop_sections:
                capture_experience = False
                capture_skills = False

            if capture_skills and para.text.strip() != '':
                key_skills_text += para.text + '\n'
            if capture_experience and para.text.strip() != '':
                work_experience_text += para.text + '\n'

        key_skills_final = f'Key Skills: \n{key_skills_text.split('•')}\n'
        work_experience_final = work_experience_text
        
        return key_skills_final, work_experience_final
    

    def process_resume(self, resume_file_path, keywords=None):
        """
        Processes the resume to match against provided keywords or previously extracted keywords.
        Args:
            resume_file_path: A string path to the resume file.
            keywords: Optional; a list of keywords to match against the resume content.
        Returns:
            A processed resume with emphasis on matched skills and experiences.
        """

        if keywords is None:
            keywords = self.keywords

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_interaction(f"\n\n({current_time}) Processing Resume...")
        
        key_skills, work_experience = self.load_resume_sections(resume_file_path)
        my_resume = f"{key_skills}\n{work_experience}"
        response = self.client.chat.completions.create(
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

        self.log_interaction("\nProcessed Resume: " + self.processed_resume)

        return self.processed_resume


    def review_resume(self, job_description=None, processed_resume=None, model_='gpt-4-turbo-2024-04-09'):
        """
        Reviews the processed resume against the job description to provide a match score and feedback.
        Args:
            job_description: Optional; a string of the job description to compare against.
            processed_resume: Optional; the processed resume text.
            model_: The model identifier to use for the OpenAI API call.
        Returns:
            A detailed review of how well the resume matches the job description.
        """

        if job_description is None:
            job_description = self.job_description
        if processed_resume is None:
            processed_resume = self.processed_resume

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_interaction(f"\n\n({current_time}) Reviewing Resume...")

        response3 = self.client.chat.completions.create(
            model=model_,
            #model="gpt-3.5-turbo-0125",
            messages = [{"role": "system",
                        "content": """Your task is to look at my resume and this job description and let me know how well my resume matches the job description.
                        I would like you to provide a score from 0 to 100, where 0 is a poor match and 100 is a perfect match. Please provide a brief explanation of why you gave this score.
                        Additionally, please tell me which keywords and key skills from the job description are missing from my resume and how I can improve my resume to better match the job description."""},
                        
                        {"role": "user",
                        "content": f"job description: {self.job_description}\n\nmy resume: {self.processed_resume}"}]
        )

        self.review_response = response3.choices[0].message.content
        self.log_interaction("\nReview Response:\n" + self.review_response)

        return self.review_response
    

    def save_special_log_for_gpt(self, job_description=None, processed_resume=None, review_response=None, new_experiences=None):
        """
        Saves a detailed log specifically formatted for use with GPT models.
        Args:
            job_description: Optional; a string of the job description.
            processed_resume: Optional; the processed resume content.
            review_response: Optional; the review feedback from the resume review.
            new_experiences: Optional; newly added experiences by the user.
        Returns:
            A formatted string containing all the information.
        """

        self.new_experiences = new_experiences

        if job_description is None:
            job_description = self.job_description
        if processed_resume is None:
            processed_resume = self.processed_resume
        if review_response is None:
            review_response = self.review_response
        if new_experiences is None:
            new_experiences = self.new_experiences

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
        return f"\nPrompt for ChatGPT: \n{content}\n\n{content2}"

    
    def fix_resume(self, job_description=None, processed_resume=None, new_experiences=None, model_='gpt-4-turbo-2024-04-09'):
        """
        Integrates new experiences into the processed resume based on user input and API feedback.
        Args:
            job_description: Optional; the job description to align the resume with.
            processed_resume: Optional; the previously processed resume text.
            new_experiences: Optional; new experiences to integrate.
            model_: The model identifier to use for processing.
        Returns:
            The updated resume with new experiences integrated.
        """

        self.new_experiences = new_experiences
        
        if job_description is None:
            job_description = self.job_description
        if processed_resume is None:
            processed_resume = self.processed_resume
        if new_experiences is None:
            new_experiences = self.new_experiences

        self.log_interaction("\nNew Experiences: \n" + self.new_experiences)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_interaction(f"\n\n({current_time}) Fixing Resume...")

        response4 = self.client.chat.completions.create(
        model=model_,
        #model="gpt-3.5-turbo-0125",
        messages = [{"role": "system",
                    "content": """Your task is to read my resume, a job description, and a list of my experiences that are currently not present in my resume.
                    After reading these, please write the relevant experiences from my list of experiences into my resume in a way that makes sense and is easy for recruiters to read and 
                    interpret. For each of the bullets that you add to the resume, please keep the same level of succinctness that is present in the bullets in the 
                    current resume. Please also make sure to include the experiences in the correct sections and jobs of my resume."""},
                    
                    {"role": "user",
                    "content": f"job description: {self.job_description}\n\nmy resume: {self.processed_resume}\n\nexperiences not on resume: {self.new_experiences}"}]
        )

        self.fixed_resume = response4.choices[0].message.content
        self.log_interaction("\nFixed Resume:\n" + self.fixed_resume)
        return self.fixed_resume


    def log_interaction(self, text):
        """
        Logs interactions and steps taken during the processing of the resume.
        Args:
            text: A string of text to log.
        """
        self.conversation_log.append(text)

    def print_log(self):
        """
        Prints the entire conversation log.
        """
        print("\n".join(self.conversation_log))