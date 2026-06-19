function switchTab(mode) {
    const loginTab = document.getElementById("login-tab")

    const registerTab = document.getElementById("register-tab")

    const loginForm = document.getElementById("login-form")

    const registerForm = document.getElementById("register-form")

    const messageBox = document.getElementById("message-box")

    messageBox.style.display = "none"

    if (mode === "login") {
        loginTab.classList.add("active");
        registerTab.classList.remove("active");
        loginForm.classList.remove("hidden");
        registerForm.classList.add("hidden");
    } else {
        registerTab.classList.add("active");
        loginTab.classList.remove("active");
        registerForm.classList.remove("hidden");
        loginForm.classList.add("hidden");
    }
}

async function handleAuth(event, endpoint) {
    event.preventDefault();

    const form = event.target;


    const formData = new FormData(form);


    const messageBox = document.getElementById("message-box");

    messageBox.style.display = "none";
    messageBox.className = "message-box";

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            messageBox.textContent = data.message;
            messageBox.classList.add("success");
            messageBox.style.display = "block";

            if (endpoint === '/login') {
                setTimeout(() => {
                    window.location.href = "/dashboard";
                }, 1000);
            }
            else {

                setTimeout(() => {
                    form.reset();
                    switchTab("login");
                }, 2000);
            }
        }
        else {
            messageBox.textContent = data.error || "Something went wrong!! Try again";
            messageBox.classList.add("error");
            messageBox.style.display = "block";
        }

    }
    catch (error) {
        messageBox.textContent = "Could not connect to the server. Please check your internet connection.";
        messageBox.classList.add("error");
        messageBox.style.display = "block";
        console.error("Error during authentication:", error);
    }

}

let interviewSession = {
    domain: '',
    difficulty: '',
    totalQuestions: 3,
    currentQuestionIndex: 0,
    qaPairs: [],
    loadedHistory: []
};

function switchDashboardTab(tab) {
    const tabInterview = document.getElementById("btn-tab-interview");
    const tabHistory = document.getElementById("btn-tab-history");
    const contentInterview = document.getElementById("content-interview");
    const contentHistory = document.getElementById("content-history");

    if (tab === "interview") {
        tabInterview.classList.add("active");
        tabHistory.classList.remove("active");
        contentInterview.classList.remove("hidden");
        contentHistory.classList.add("hidden");
    } else {
        tabHistory.classList.add("active");
        tabInterview.classList.remove("active");
        contentHistory.classList.remove("hidden");
        contentInterview.classList.add("hidden");
        fetchHistory();
    }
}
function startInterview() {
    // 1. Options le lenge
    interviewSession.domain = document.getElementById("interview-domain").value;
    interviewSession.difficulty = document.getElementById("interview-difficulty").value;
    interviewSession.totalQuestions = parseInt(document.getElementById("interview-question-count").value);


    document.getElementById("interview-setup-state").classList.add("hidden");
    document.getElementById("interview-active-state").classList.remove("hidden");


    loadQuestion();
}
async function loadQuestion() {
    const questionTextEl = document.getElementById("current-question-text");
    const progressEl = document.getElementById("question-progress");
    const answerTextArea = document.getElementById("user-answer");
    const submitBtn = document.getElementById("submit-answer-btn");

    questionTextEl.textContent = "Generating technical question, please wait...";
    answerTextArea.value = "";
    answerTextArea.disabled = true;
    submitBtn.disabled = true;

    const currentNum = interviewSession.currentQuestionIndex + 1;
    progressEl.textContent = `Question ${currentNum} of ${interviewSession.totalQuestions}`;

    const previous_questions = interviewSession.qaPairs.map(pair => pair.question);

    try {
        // Backend `/generate-question` API call karna
        const response = await fetch('/generate-question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                domain: interviewSession.domain,
                difficulty: interviewSession.difficulty,
                previous_questions: previous_questions
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // Question show karna aur input unlock karna
            questionTextEl.textContent = data.question;
            answerTextArea.disabled = false;
            submitBtn.disabled = false;
            answerTextArea.focus();
        } else {
            questionTextEl.textContent = "Error: " + (data.error || "Failed to load question.");
        }
    } catch (err) {
        questionTextEl.textContent = "Network error. Could not reach server.";
        console.error("Fetch question error:", err);
    }
}
// 1. Current answer ko check aur submit karne ka function
async function submitAnswer() {
    const answerTextArea = document.getElementById("user-answer");
    const userAnswer = answerTextArea.value.trim();

    // Verification: Agar answer khali (empty) hai, toh user ko alert do
    if (!userAnswer) {
        alert("Please write an answer before submitting.");
        return;
    }

    const currentQuestionText = document.getElementById("current-question-text").textContent;

    // Answer aur Question ko humare session memory (qaPairs) mein daalna
    interviewSession.qaPairs.push({
        question: currentQuestionText,
        answer: userAnswer
    });

    // Question counter ko aage badhana
    interviewSession.currentQuestionIndex++;

    // Check karna: Kya abhi aur questions bache hain?
    if (interviewSession.currentQuestionIndex < interviewSession.totalQuestions) {
        // Agar bache hain, toh agla sawaal load karo
        loadQuestion();
    } else {
        // Agar saare questions ho gaye, toh screen badal kar "Results Screen" dikhao
        document.getElementById("interview-active-state").classList.add("hidden");

        const resultsState = document.getElementById("interview-results-state");
        resultsState.classList.remove("hidden");

        // Loader Text set karna jab tak AI check kar raha hai
        document.getElementById("result-score-value").textContent = "...";
        document.getElementById("result-feedback-text").innerHTML = "<p>AI is evaluating your responses. This may take 10-15 seconds...</p>";

        const statusBadge = document.getElementById("result-status-badge");
        statusBadge.textContent = "Evaluating...";
        statusBadge.className = "badge-status";

        try {
            // Backend API '/evaluate-interview' ko final request bhejna
            const response = await fetch('/evaluate-interview', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    domain: interviewSession.domain,
                    difficulty: interviewSession.difficulty,
                    qa_pairs: interviewSession.qaPairs
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Score out of 50 screen par print karna
                document.getElementById("result-score-value").textContent = data.score || "N/A";

                // Feedback text ko format karke dikhana (\n ko line break <br> banana)
                document.getElementById("result-feedback-text").innerHTML = data.evaluation.replace(/\n/g, "<br>");

                // Status ke according green/yellow/red color classes apply karna
                statusBadge.textContent = data.status;

                switch (data.status) {
                    case "Selected":
                        statusBadge.className = "badge-status badge-selected";
                        break;
                    case "Next Round":
                        statusBadge.className = "badge-status badge-next-round";
                        break;
                    default:
                        statusBadge.className = "badge-status badge-practice";
                }
            } else {
                document.getElementById("result-feedback-text").textContent = "Evaluation failed: " + (data.error || "Server error.");
            }
        } catch (err) {
            document.getElementById("result-feedback-text").textContent = "Connection error. Failed to load evaluation.";
            console.error("Evaluation error:", err);
        }
    }
}

// 2. Interview ko wapas shuru se reset karne ka function 
function resetInterview() {
    interviewSession = {
        domain: "Object-Oriented Programming (OOPs)",
        difficulty: "Easy",
        totalQuestions: 5,
        currentQuestionIndex: 0,
        qaPairs: [],
        qaSession: false
    };

    // Sabhi text area ko clear karna aur setup form wapas dikhana
    document.getElementById("user-answer").value = "";
    document.getElementById("interview-results-state").classList.add("hidden");
    document.getElementById("interview-active-state").classList.add("hidden");
    document.getElementById("interview-setup-state").classList.remove("hidden");
}
