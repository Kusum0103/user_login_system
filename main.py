from flask import Flask, render_template , request, jsonify, session, redirect, url_for
import os
import json
import re
from dotenv import load_dotenv
from groq import Groq


from database import init_db

from decorators import login_required, api_login_required

from auth import is_valid_email, check_password_strength

from auth_queries import check_username_exists, register_user, verify_user_login, get_user_id_by_username, update_user_active_status, log_login_activity

from dashboard_queries import get_dashboard_stats, get_active_users

from interview_queries import save_interview, get_interview_history


load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=api_key)
app = Flask(__name__)
app.secret_key = os.urandom(24)
init_db() 

def parse_evaluation(evaluation_text):
    score_match = re.search(r"(\d+)\s*(?:/|out\s+of)\s*50", evaluation_text, re.IGNORECASE)
    score = int(score_match.group(1)) if score_match else None
    
    status = "Needs Practice"
    if re.search(r'\bSelected\b', evaluation_text, re.IGNORECASE):
        status = "Selected"
    elif re.search(r'\bNext\s+Round\b', evaluation_text, re.IGNORECASE):
        status = "Next Round"
    elif re.search(r'\bNeed\s+Practice\b', evaluation_text, re.IGNORECASE):
        status = "Needs Practice"
        
    return score, status

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')


    if not username or not email or not password or not confirm_password :
        return jsonify({'success' : False, 'error': "All fields are required."}), 400
    if not is_valid_email(email):
        return jsonify({'success' : False, 'error': "Invalid Email Address."}), 400



    is_strong,password_strength_message = check_password_strength(password)
    if not is_strong:
        return jsonify({'success' : False, 'error': password_strength_message}), 400

    if password != confirm_password:
        return jsonify({'success': False, 'error': 'Passwords do not match.'}), 400


    if check_username_exists(username):
        return jsonify({'success': False, 'error': "Username already exists."}), 400
        
    if register_user(username, email, password):
        return jsonify({'success': True, 'message': 'Registration Successful! You can Login Now'})
    else:
        return jsonify({'success': False, 'error': 'Registration failed due to a server error.'}), 500
    
@app.route('/login',methods = ['POST'])
def login():
    username = request.form.get('username','').strip()
    password = request.form.get('password','')
    
    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and Password are required.'}), 400
    
    success, message = verify_user_login( username, password)
    if not success:
           return jsonify({'success': False, 'error': message}), 401
    user_id = get_user_id_by_username(username)       
    if not user_id:
        return jsonify({'success' : False , 'error' : 'User ID lookup failed.'}), 500

    update_user_active_status(1, user_id=user_id)

    user_agent = request.headers.get('User-Agent', 'Unknown')
  
          
    # OS identify karne ke liye 
    match user_agent:
        case ua if 'Windows' in ua:
            os_name = 'Windows'
        case ua if 'Mac' in ua:
            os_name = 'macOS'
        case ua if 'Linux' in ua:
            os_name = 'Linux'
        case ua if 'Android' in ua:
            os_name = 'Android'
        case ua if 'iPhone' in ua:
            os_name = 'iPhone'
        case _:
            os_name = 'Unknown OS'
    # Browser identify karne ke liye
    match user_agent:
        case ua if 'Edge' in ua:
            browser = 'Edge'
        case ua if 'Chrome' in ua:
            browser = 'Chrome'
        case ua if 'Firefox' in ua:
            browser = 'Firefox'
        case ua if 'Safari' in ua:
            browser = 'Safari'
        case _:
            browser = 'Browser'
            
    device_info = f"{browser} on {os_name}"
    
    log_login_activity(user_id, device_info)
    session['username'] = username
    
    return jsonify({'success': True, 'message': message})
            
    

@app.route('/dashboard')
@login_required
def dashboard():
    username = session['username']
    
    user_id = get_user_id_by_username(username)
    
    stats = get_dashboard_stats(user_id) if user_id else {'device_info': 'Unknown device', 'login_count_24h': 0}
    
    active_users = get_active_users()
    
    return render_template(
        'dashboard.html',
        username=username,
        device_info=stats['device_info'],
        login_count_24h=stats['login_count_24h'],
        active_users=active_users
    )


@app.route('/generate-question' , methods = ['POST'])   
@api_login_required
def generate_question():

    data = request.get_json()
    domain = data.get('domain' , 'Python Programming')
    difficulty = data.get('difficulty', 'Intermediate')
    previous_questions = data.get('previous_questions', [])
    prev_str =  "\n".join([f"- {q}" for q in previous_questions])

    prompt = (
        f"You are a campus placement interviewer. Generate exactly one technical interview question "
        f"for a college graduate on the topic of '{domain}' at the '{difficulty}' level.\n\n"
        f"Do NOT generate any of the following questions which were already asked in this session:\n"
        f"{prev_str}\n\n"
        f"CRITICAL: Output ONLY the question text. Do not write any intro, code solutions, or explanations."
    )
    try :
        chat_completion = client.chat.completions.create(
            messages = [
                {
                    "role" : "user",
                    "content" : prompt,

                }
            ], 
            model = "llama-3.1-8b-instant",

        ) 
        question = chat_completion.choices[0].message.content.strip()
        return jsonify({'success': True,'question' : question})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to generate question:{str(e)}'}), 500
        
        


@app.route('/evaluate-interview', methods=['POST'])
@api_login_required
def evaluate_interview():

    username = session['username']
    data = request.get_json()
    name = data.get('name', 'Candidate')
    domain = data.get('domain')
    difficulty = data.get('difficulty')
    qa_pairs = data.get('qa_pairs', [])

    if not qa_pairs:
        return jsonify({'success': False, 'error': 'No QA data provided.'}), 400
    
    qa_formatted = ""
    for idx, pair in enumerate(qa_pairs):
        qa_formatted += f"Q{idx+1}: {pair['question']}\nCandidate's Answer: {pair['answer']}\n\n"
        
    prompt = (
        f"You are a recruitment panel evaluating the candidate '{name}' who completed a mock placement interview "
        f"in the domain of '{domain}' at '{difficulty}' level.\n\n"
        f"Here is the transcript of the interview (5 Questions and Answers):\n\n"
        f"{qa_formatted}\n"
        f"Evaluate the complete performance with extreme care. Perform checks for logic, conceptual correctness, "
        f"and complexity analysis where applicable. Format your response strictly using these markdown headers:\n\n"
        f"### 1. **Overall Placement Status**\n"
        f"Provide a recommendation (e.g., Selected, Next Round, or Needs Practice) and an overall score out of 50.\n\n"
        f"### 2. **Question-by-Question Breakdown**\n"
        f"Go through each of the 5 questions. Give a brief comment on whether the answer was correct, partially correct, or wrong.\n\n"
        f"### 3. **Key Strengths**\n"
        f"List areas where the candidate demonstrated solid understanding.\n\n"
        f"### 4. **Key Areas of Improvement**\n"
        f"Outline critical gaps, bugs in their code, or conceptual misunderstandings.\n\n"
        f"### 5. **Model Answers & Tips**\n"
        f"Provide the ideal answers for any questions they struggled with to help them improve."
    )
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        evaluation = completion.choices[0].message.content.strip()

        score, status = parse_evaluation(evaluation)

        user_id = get_user_id_by_username(username)
        if not user_id:
            return jsonify({'success': False, 'error': 'User not found.'}), 404
            
        #  Interview results database me save karna 
        saved = save_interview(user_id, domain, difficulty, qa_pairs, evaluation, score, status)
        if not saved:
            return jsonify({'success': False, 'error': 'Failed to save evaluation to database.'}), 500
            
        # Client ko success response return karna
        return jsonify({
            'success': True,
            'evaluation': evaluation,
            'score': score,
            'status': status
        })
    except Exception as e:
        print("Backend Error:", e)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/get-history', methods=['GET'])
@api_login_required
def get_history():
    username = session['username']
    
    # User ID fetch karna 
    user_id = get_user_id_by_username(username)
    if not user_id:
        return jsonify({'success': False, 'error': 'User not found.'}), 404
        
    # History fetch karna 
    history = get_interview_history(user_id)
    
    return jsonify({'success': True, 'history': history})
                            

@app.route('/logout')
def logout():
    if 'username' in session:
        username = session['username']
        update_user_active_status(0, username=username)
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)