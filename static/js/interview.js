// Global Session state for Interview
let interviewSession = {
    domain: '',
    difficulty: '',
    totalQuestions: 3,
    currentQuestionIndex: 0,
    qaPairs: [],
    loadedHistory: []
};
let timerInterval; // Countdown timer ko control karne ke liye tracker

// Dashboard tabs switch karne ke liye 

function switchDashboardTab(tab) {
    const tabInterview = document.getElementById("btn-tab-interview");
    const tabHistory = document.getElementById("btn-tab-history");
    const contentInterview = document.getElementById("content-interview");
    const contentHistory = document.getElementById("content-history");

    if (tab === "interview") {
        tabInterview.classList.add("active");
        tabHistory.classList.remove("active");

        contentInterview.classList.add("active");
        contentHistory.classList.remove("active");
    } else {
        tabHistory.classList.add("active");
        tabInterview.classList.remove("active");
        contentHistory.classList.add("active");
        contentInterview.classList.remove("active");

        fetchHistory();
    }
}



// Mock Interview start karne ke liye
function startInterview() {

    interviewSession.isActive = true;
    interviewSession.domain = document.getElementById("interview-domain").value;
    interviewSession.difficulty = document.getElementById("interview-difficulty").value;
    interviewSession.totalQuestions = parseInt(document.getElementById("interview-question-count").value);

    document.getElementById("interview-setup-state").classList.add("hidden");
    document.getElementById("interview-active-state").classList.remove("hidden");

    loadQuestion();
}

// Backend AI se question load karne ke liye
async function loadQuestion() {

    clearInterval(timerInterval);
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
            questionTextEl.textContent = data.question;
            answerTextArea.disabled = false;
            submitBtn.disabled = false;
            answerTextArea.focus();

            let secondsLeft = 120;
            const timerEl = document.getElementById("question-timer");
            timerEl.textContent = `Time Left: ${secondsLeft}s`;
            timerInterval = setInterval(() => {
                secondsLeft--;
                timerEl.textContent = `Time Left: ${secondsLeft}s`;
                if (secondsLeft <= 0) {
                    clearInterval(timerInterval);
                    submitAnswer(true);
                }
            }, 1000);



        } else {
            questionTextEl.textContent = "Error: " + (data.error || "Failed to load question.");
        }
    } catch (err) {
        questionTextEl.textContent = "Network error. Could not reach server.";
        console.error("Fetch question error:", err);
    }
}

async function submitAnswer(isAutoSubmit = false) {
    const answerTextArea = document.getElementById("user-answer");
    let userAnswer = answerTextArea.value.trim();

    if (!userAnswer) {
        if (isAutoSubmit) {
            userAnswer = "No answer provided (Time limit reached).";
        } else {
            showCustomAlert("Please write an answer before submitting.");
            return;
        }
    }
    clearInterval(timerInterval);


    const currentQuestionText = document.getElementById("current-question-text").textContent;

    interviewSession.qaPairs.push({
        question: currentQuestionText,
        answer: userAnswer
    });

    interviewSession.currentQuestionIndex++;

    if (interviewSession.currentQuestionIndex < interviewSession.totalQuestions) {
        loadQuestion();
    } else {
        interviewSession.isActive = false;
        document.getElementById("interview-active-state").classList.add("hidden");

        const resultsState = document.getElementById("interview-results-state");
        resultsState.classList.remove("hidden");

        document.getElementById("result-score-value").textContent = "...";
        document.getElementById("result-feedback-text").innerHTML = "<p>AI is evaluating your responses. This may take 10-15 seconds...</p>";

        const statusBadge = document.getElementById("result-status-badge");
        statusBadge.textContent = "Evaluating...";
        statusBadge.className = "badge-status";

        try {
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
                document.getElementById("result-score-value").textContent = data.score || "N/A";
                document.getElementById("result-feedback-text").innerHTML = data.evaluation.replace(/\n/g, "<br>");
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

// Interview reset karne ke liye
function resetInterview() {
    clearInterval(timerInterval);
    interviewSession = {
        domain: "Object-Oriented Programming (OOPs)",
        difficulty: "Easy",
        totalQuestions: 5,
        currentQuestionIndex: 0,
        qaPairs: [],
        qaSession: false,
        isActive: false
    };

    document.getElementById("user-answer").value = "";
    document.getElementById("interview-results-state").classList.add("hidden");
    document.getElementById("interview-active-state").classList.add("hidden");
    document.getElementById("interview-setup-state").classList.remove("hidden");
}

window.addEventListener("blur", () => {

    if (interviewSession && interviewSession.isActive) {
        interviewSession.isActive = false;
        showCustomAlert("Anti-Cheat Alert: You switched tabs or minimized the window during the interview. Your exam has been terminated!");
        resetInterview();
    }
});

function confirmQuitInterview() {
    const isSure = showCustomConfirm("Are you sure you want to quit the interview? All progress in this session will be lost.", () => {
        resetInterview();

    });

}

let confirmCallback = null;


function showCustomAlert(message) {
    document.getElementById("custom-alert-message").textContent = message;
    document.getElementById("custom-alert-modal").classList.remove("hidden");
}


function closeCustomAlert() {
    document.getElementById("custom-alert-modal").classList.add("hidden");
}


function showCustomConfirm(message, callback) {
    document.getElementById("custom-confirm-message").textContent = message;
    confirmCallback = callback;
    document.getElementById("custom-confirm-modal").classList.remove("hidden");
}


function closeCustomConfirm(isConfirmed) {
    document.getElementById("custom-confirm-modal").classList.add("hidden");
    if (isConfirmed && confirmCallback) {
        confirmCallback();
    }
    confirmCallback = null;
}

