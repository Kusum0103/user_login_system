// Har 20 seconds mein API ko ping bhejega
setInterval(() => {
    fetch('/api/ping', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            // Agar session invalid ho chuka hai (401 response)
            if (response.status === 401) {
                // To login page par redirect kar do
                window.location.href = '/';
            }
        })
        .catch(err => console.error("Heartbeat ping error:", err));
}, 20000);
