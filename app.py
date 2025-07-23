from flask import Flask, render_template, request, jsonify, send_file
import json
import random
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import black, blue, grey
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import re

app = Flask(__name__)

# AI Resume Generation Engine
class AIResumeGenerator:
    def __init__(self):
        self.skill_categories = {
            'technical': ['Python', 'JavaScript', 'Java', 'C++', 'SQL', 'HTML/CSS', 'React', 'Node.js', 'Machine Learning', 'Data Analysis'],
            'soft': ['Leadership', 'Communication', 'Problem Solving', 'Team Collaboration', 'Time Management', 'Adaptability', 'Critical Thinking'],
            'design': ['Adobe Creative Suite', 'UI/UX Design', 'Graphic Design', 'Figma', 'Sketch', 'InVision'],
            'business': ['Project Management', 'Strategic Planning', 'Market Research', 'Financial Analysis', 'Sales', 'Marketing']
        }
        
        self.action_words = [
            'Developed', 'Implemented', 'Led', 'Managed', 'Created', 'Designed', 'Optimized',
            'Coordinated', 'Analyzed', 'Improved', 'Established', 'Streamlined', 'Collaborated',
            'Executed', 'Delivered', 'Enhanced', 'Initiated', 'Supervised', 'Facilitated'
        ]
        
        self.cover_letter_templates = {
            'technology': {
                'opening': "I am excited to apply for the {position} role at {company}. With my strong background in {key_skills}, I am confident in my ability to contribute to your innovative team.",
                'body': "In my previous role as {last_position}, I successfully {achievement}. My expertise in {technical_skills} has enabled me to {impact}. I am particularly drawn to {company} because of your commitment to {company_value}.",
                'closing': "I would welcome the opportunity to discuss how my {key_strength} and passion for {field} can contribute to {company}'s continued success."
            },
            'business': {
                'opening': "I am writing to express my strong interest in the {position} position at {company}. My {years} years of experience in {field} have prepared me to make an immediate impact on your team.",
                'body': "Throughout my career, I have consistently {achievement_type}. At {previous_company}, I {specific_achievement}, resulting in {quantified_result}. My ability to {key_skill} aligns perfectly with your requirements.",
                'closing': "I am eager to bring my proven track record of {strength} to {company} and would appreciate the opportunity to discuss my qualifications further."
            }
        }

    def generate_resume_summary(self, data):
        """Generate AI-powered professional summary"""
        experience_level = self.determine_experience_level(data.get('experience', []))
        key_skills = data.get('skills', [])[:3]  # Top 3 skills
        career_goal = data.get('career_goals', '')
        
        templates = [
            f"{experience_level} professional with expertise in {', '.join(key_skills)}. {career_goal} Proven track record of delivering results in fast-paced environments.",
            f"Results-driven {experience_level.lower()} specializing in {', '.join(key_skills)}. {career_goal} Strong analytical and problem-solving abilities with excellent communication skills.",
            f"Dynamic {experience_level.lower()} with comprehensive experience in {', '.join(key_skills)}. {career_goal} Committed to continuous learning and professional growth."
        ]
        
        return random.choice(templates)

    def determine_experience_level(self, experience):
        """Determine experience level based on work history"""
        total_years = 0
        for exp in experience:
            # Simple estimation based on typical job duration
            total_years += 2  # Assume 2 years average per position
        
        if total_years <= 2:
            return "Entry-level"
        elif total_years <= 5:
            return "Mid-level"
        elif total_years <= 10:
            return "Senior"
        else:
            return "Executive"

    def enhance_experience_descriptions(self, experience):
        """Enhance job descriptions with action words and impact"""
        enhanced_experience = []
        
        for exp in experience:
            enhanced_desc = []
            descriptions = exp.get('description', '').split('\n') if exp.get('description') else []
            
            for desc in descriptions:
                if desc.strip():
                    # Add action word if not present
                    if not any(word in desc for word in self.action_words):
                        action_word = random.choice(self.action_words)
                        enhanced_desc.append(f"{action_word} {desc.lower()}")
                    else:
                        enhanced_desc.append(desc)
            
            enhanced_exp = exp.copy()
            enhanced_exp['description'] = '\n'.join(enhanced_desc)
            enhanced_experience.append(enhanced_exp)
        
        return enhanced_experience

    def generate_cover_letter(self, data, job_position="", company_name=""):
        """Generate personalized cover letter"""
        # Determine field type
        field_type = 'technology' if any(skill.lower() in ['python', 'javascript', 'programming', 'software', 'java', 'html', 'css', 'react', 'node'] 
                                       for skill in data.get('skills', [])) else 'business'
        
        template = self.cover_letter_templates[field_type]
        
        # Extract relevant information
        key_skills = ', '.join(data.get('skills', [])[:3]) if data.get('skills') else 'relevant skills'
        last_position = data.get('experience', [{}])[0].get('position', 'my previous role') if data.get('experience') else 'my previous role'
        
        # Calculate years of experience
        years_experience = len(data.get('experience', [])) * 2  # Estimate 2 years per position
        years_text = f"{years_experience}+" if years_experience > 0 else "several"
        
        # Get previous company for business template
        previous_company = data.get('experience', [{}])[0].get('company', 'my previous company') if data.get('experience') else 'my previous company'
        
        # Generate cover letter sections
        opening = template['opening'].format(
            position=job_position or "the position",
            company=company_name or "your organization",
            key_skills=key_skills,
            years=years_text,
            field=data.get('preferred_industry', 'my field')
        )
        
        body = template['body'].format(
            last_position=last_position,
            achievement="delivered exceptional results and exceeded performance targets",
            technical_skills=key_skills,
            impact="drive innovation and improve operational efficiency",
            company=company_name or "your organization",
            company_value="innovation and excellence",
            achievement_type="exceeded expectations and delivered results",
            previous_company=previous_company,
            specific_achievement="led key projects and improved team efficiency",
            quantified_result="increased productivity by 25%",
            key_skill="collaborate effectively and solve complex problems"
        )
        
        closing = template['closing'].format(
            key_strength="technical expertise" if field_type == 'technology' else "business acumen",
            field=data.get('preferred_industry', 'this field'),
            company=company_name or "your organization",
            strength="delivering results and driving innovation"
        )
        
        return f"{opening}\n\n{body}\n\n{closing}\n\nSincerely,\n{data.get('name', 'Your Name')}"

# Initialize AI generator
ai_generator = AIResumeGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_resume', methods=['POST'])
def generate_resume():
    try:
        data = request.json
        
        # Generate AI-enhanced resume components
        summary = ai_generator.generate_resume_summary(data)
        enhanced_experience = ai_generator.enhance_experience_descriptions(data.get('experience', []))
        
        # Prepare enhanced resume data
        resume_data = {
            **data,
            'summary': summary,
            'experience': enhanced_experience,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify({
            'success': True,
            'resume_data': resume_data,
            'message': 'Resume generated successfully!'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating resume: {str(e)}'
        })

@app.route('/generate_cover_letter', methods=['POST'])
def generate_cover_letter():
    try:
        data = request.json
        resume_data = data.get('resume_data', {})
        job_position = data.get('job_position', '')
        company_name = data.get('company_name', '')
        
        cover_letter = ai_generator.generate_cover_letter(resume_data, job_position, company_name)
        
        return jsonify({
            'success': True,
            'cover_letter': cover_letter,
            'message': 'Cover letter generated successfully!'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating cover letter: {str(e)}'
        })

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    try:
        data = request.json
        resume_data = data.get('resume_data', {})
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=blue,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=blue,
            spaceAfter=10
        )
        
        # Header
        story.append(Paragraph(resume_data.get('name', 'Your Name'), title_style))
        contact_info = f"{resume_data.get('email', '')} | {resume_data.get('phone', '')} | {resume_data.get('location', '')}"
        story.append(Paragraph(contact_info, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Professional Summary
        if resume_data.get('summary'):
            story.append(Paragraph("PROFESSIONAL SUMMARY", section_style))
            story.append(Paragraph(resume_data['summary'], styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Skills
        if resume_data.get('skills'):
            story.append(Paragraph("SKILLS", section_style))
            skills_text = " • ".join(resume_data['skills'])
            story.append(Paragraph(skills_text, styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Experience
        if resume_data.get('experience'):
            story.append(Paragraph("PROFESSIONAL EXPERIENCE", section_style))
            for exp in resume_data['experience']:
                job_title = f"<b>{exp.get('position', '')}</b> - {exp.get('company', '')}"
                story.append(Paragraph(job_title, styles['Normal']))
                
                if exp.get('duration'):
                    story.append(Paragraph(exp['duration'], styles['Normal']))
                
                if exp.get('description'):
                    for desc_line in exp['description'].split('\n'):
                        if desc_line.strip():
                            story.append(Paragraph(f"• {desc_line.strip()}", styles['Normal']))
                
                story.append(Spacer(1, 10))
        
        # Education
        if resume_data.get('education'):
            story.append(Paragraph("EDUCATION", section_style))
            for edu in resume_data['education']:
                edu_text = f"<b>{edu.get('degree', '')}</b> - {edu.get('institution', '')}"
                if edu.get('year'):
                    edu_text += f" ({edu['year']})"
                story.append(Paragraph(edu_text, styles['Normal']))
            story.append(Spacer(1, 12))
        
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"{resume_data.get('name', 'resume').replace(' ', '_')}_resume.pdf",
            mimetype='application/pdf'
        )
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating PDF: {str(e)}'
        })

if __name__ == '__main__':
    app.run(debug=True)