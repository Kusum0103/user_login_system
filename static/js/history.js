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

                           <!-- PDF Download Section -->
                        <div class="history-card-footer" style="display: flex; justify-content: flex-end; margin-top: 10px; border-top: 1px solid rgba(37, 99, 235, 0.08); padding-top: 10px;">
                            <button class="download-pdf-btn" onclick="event.stopPropagation(); downloadPDF(${item.id})" style="background: linear-gradient(135deg, var(--primary-color), var(--accent-color)); color: white; border: none; padding: 6px 14px; border-radius: 8px; font-size: 0.8rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px; transition: all 0.2s;">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                                Download PDF
                            </button>
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

    let qaPairs = [];
    try {
        qaPairs = typeof item.qa_data === 'string' ? JSON.parse(item.qa_data) : item.qa_data;
    } catch (e) {
        console.error("QA data parse error :", e);
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
function downloadPDF(id) {
    // 1. History array se current interview ka data fetch karenge
    const item = interviewSession.loadedHistory.find(h => h.id === id);
    if (!item) return;

    let qaPairs = [];
    try {
        qaPairs = typeof item.qa_data === 'string' ? JSON.parse(item.qa_data) : item.qa_data;
    } catch (e) {
        console.error("QA data parse error:", e);
    }

    // 2. Q&A list ke liye HTML structure ready karenge (PDF ke andar dikhane ke liye)
    let qaHtml = '';
    if (Array.isArray(qaPairs) && qaPairs.length > 0) {
        qaPairs.forEach((pair, idx) => {
            qaHtml += `
                <div style="margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px dashed #e2e8f0; page-break-inside: avoid;">
                    <p style="font-weight: bold; margin-bottom: 4px; color: #1e293b;">Q${idx + 1}: ${pair.question}</p>
                    <p style="color: #475569; padding-left: 10px; border-left: 3px solid #3b82f6; margin: 0;">Answer: ${pair.answer}</p>
                </div>`;
        });
    } else {
        qaHtml = '<p>No transcript details available.</p>';
    }

    const feedbackHtml = (item.evaluation || 'No feedback details available.').replace(/\n/g, '<br>');
    // 3. Ek temporary virtual element banayenge PDF generation ke liye
    const container = document.createElement('div');
    container.style.padding = '40px';
    container.style.fontFamily = 'Helvetica, Arial, sans-serif';
    container.style.color = '#334155';
    container.style.lineHeight = '1.6';

    container.innerHTML = `
        <!-- Report Header -->
        <div style="text-align: center; border-bottom: 2px solid #3b82f6; padding-bottom: 20px; margin-bottom: 25px;">
            <h1 style="color: #1e3a8a; margin: 0 0 10px 0; font-size: 24px;">PLACEMENT INTERVIEW REPORT</h1>

                        <p style="color: #64748b; margin: 0; font-size: 14px;">Mock Interview Performance & Evaluation Profile</p>
        </div>

        <!-- 1. Summary details table -->
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 30px;">
            <h3 style="color: #1e3a8a; margin-top: 0; margin-bottom: 15px; font-size: 16px; border-bottom: 1px solid #cbd5e1; padding-bottom: 6px;">1. Summary Details</h3>
            <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                <tr>
                    <td style="padding: 6px 0; font-weight: bold; color: #475569; width: 35%;">Topic / Domain:</td>
                    <td style="padding: 6px 0; color: #1e293b;">${item.domain}</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0; font-weight: bold; color: #475569;">Difficulty Level:</td>
                    <td style="padding: 6px 0; color: #1e293b;">${item.difficulty}</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0; font-weight: bold; color: #475569;">Date & Time:</td>
                    <td style="padding: 6px 0; color: #1e293b;">${new Date(item.timestamp).toLocaleString()}</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0; font-weight: bold; color: #475569;">Evaluation Score:</td>
                    <td style="padding: 6px 0; color: #1e293b; font-size: 16px; font-weight: bold;">${item.score !== null ? item.score : 'N/A'}/50</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0; font-weight: bold; color: #475569;">Placement Status:</td>
                    <td style="padding: 6px 0;">
                        <span style="display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; 
                            background-color: ${item.status === 'Selected' ? '#d1fae5' : item.status === 'Next Round' ? '#dbeafe' : '#fee2e2'};
                            color: ${item.status === 'Selected' ? '#065f46' : item.status === 'Next Round' ? '#1e40af' : '#991b1b'};">
                            ${item.status || 'Needs Practice'}
                        </span>
                    </td>
                </tr>
            </table>
        </div>
        <!-- 2. AI Performance Evaluation -->
        <div style="margin-bottom: 30px; page-break-inside: avoid;">
            <h3 style="color: #1e3a8a; margin-top: 0; margin-bottom: 12px; font-size: 16px; border-bottom: 1px solid #3b82f6; padding-bottom: 6px;">2. AI Performance Evaluation</h3>
            <div style="font-size: 13px; color: #334155; text-align: justify; line-height: 1.7; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                ${feedbackHtml}
            </div>
        </div>

        <!-- 3. Full Transcript -->
        <div style="page-break-before: auto;">
            <h3 style="color: #1e3a8a; margin-top: 0; margin-bottom: 15px; font-size: 16px; border-bottom: 1px solid #3b82f6; padding-bottom: 6px;">3. Interview Question & Answer Transcript</h3>
            <div style="font-size: 13px;">
                ${qaHtml}
            </div>
        </div>

        <!-- Document Footer -->
        <div style="margin-top: 50px; text-align: center; border-top: 1px solid #e2e8f0; padding-top: 15px; font-size: 11px; color: #94a3b8; page-break-inside: avoid;">
            Report generated automatically by Mock Placement System. All rights reserved.
        </div>
    `;

    // 5. PDF generation configuration aur specifications set karna
    const opt = {
        margin: 15,
        filename: `interview-report-${item.domain.replace(/\s+/g, '-').toLowerCase()}-${item.id}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    // 6. html2pdf library ko invoke karke PDF download start karna
    html2pdf().set(opt).from(container).save();
}

