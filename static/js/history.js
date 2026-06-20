async function fetchHistory() {
    const historyListContainer = document.getElementById("history-list-container");
    
    // Loader dikhana jab tak database se data fetch ho raha ho
    historyListContainer.innerHTML = `<div class="history-placeholder"><p>Loading history, please wait...</p></div>`;
    try {
        const response = await fetch('/get-history');
        const data = await response.json();
        if (response.ok && data.success) {
            // Data ko local session memory (interviewSession) mein save karna
            interviewSession.loadedHistory = data.history;
            
            if (data.history.length === 0) {
                historyListContainer.innerHTML = `
                    <div class="history-placeholder">
                        <p>No interview history found. Start your first mock placement interview now!</p>
                    </div>`;
                return;
            }
            let htmlContent = '';
            data.history.forEach(item => {
                let badgeClass = 'badge-practice';
                if (item.status === 'Selected') badgeClass = 'badge-selected';
                else if (item.status === 'Next Round') badgeClass = 'badge-next-round';
                htmlContent += `
                    <div class="history-card" onclick="openHistoryModal(${item.id})">
                        <div class="history-card-header">
                            <span class="history-domain">${item.domain}</span>
                            <span class="badge-status ${badgeClass}">${item.status || 'Needs Practice'}</span>
                        </div>
                        <div class="history-card-body">
                            <div class="history-info">Difficulty: <strong>${item.difficulty}</strong></div>
                            <div class="history-info">Score: <strong>${item.score !== null ? item.score : 'N/A'}/50</strong></div>
                            <div class="history-date">${new Date(item.timestamp).toLocaleString()}</div>
                        </div>
                    </div>`;
            });
            historyListContainer.innerHTML = htmlContent;
        } else {
            historyListContainer.innerHTML = `<div class="history-placeholder error"><p>Error: ${data.error || 'Failed to load history.'}</p></div>`;
        }
    } catch (err) {
        historyListContainer.innerHTML = `<div class="history-placeholder error"><p>Network error. Failed to load history.</p></div>`;
        console.error("Fetch history error:", err);
    }
}

function openHistoryModal(id) {
    const item = interviewSession.loadedHistory.find(h => h.id === id);
    if (!item) return;

       document.getElementById("modal-title").textContent = `${item.domain} (${item.difficulty})`;
    document.getElementById("modal-score-value").textContent = item.score !== null ? item.score : 'N/A';

    const statusBadge = document.getElementById("modal-status-badge");
    statusBadge.textContent = item.status || 'Need Practice';

    statusBadge.className = "badge-status";
    if (item.status === 'Selected') {
        statusBadge.classList.add("badge-selected");
    } else if (item.status === 'Next Round') {
        statusBadge.classList.add("badge-next-round");
    } else {
        statusBadge.classList.add("badge-practice");
    }

    let qaPairs =[];
    try {
        qaPairs = typeof item.qa_data === 'string' ? JSON.parse(item.qa_data) : item.qa_data;
    } catch (e) {
        console.error( "QA data parse error :" , e );
    }

    let qaHtml = '';
    if (Array.isArray(qaPairs) && qaPairs.length > 0) {
        qaPairs.forEach((pair, idx) => {
            qaHtml += `
                <div class="modal-qa-item" style="margin-bottom: 15px; border-bottom: 1px dashed rgba(37,99,235,0.1); padding-bottom: 10px;">
                    <p class="modal-question" style="font-weight: 600; margin-bottom: 5px; color: var(--text-primary);">Q${idx + 1}: ${pair.question}</p>
                    <p class="modal-answer" style="color: var(--text-secondary); padding-left: 10px; border-left: 2px solid var(--accent-color);">Answer: ${pair.answer}</p>
                </div>`;
        });
    } else {
        qaHtml = '<p>No transcript details available.</p>';
    }
    document.getElementById("modal-qa-list").innerHTML = qaHtml;
    const feedbackText = item.evaluation || 'No feedback details available.';
    document.getElementById("modal-feedback-text").innerHTML = feedbackText.replace(/\n/g, "<br>");
    document.getElementById("history-modal").classList.remove("hidden");
}

function closeModal() {
    document.getElementById("history-modal").classList.add("hidden");
}
