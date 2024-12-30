document.getElementById('analyzeForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const postType = document.getElementById('postType').value;
    const response = await fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ post_type: postType })
    });
    const data = await response.json();
    const resultsDiv = document.getElementById('results');
    if (response.ok) {
        resultsDiv.innerHTML = `
            <h3>Analysis for: ${data.post_type}</h3>
            <p><strong>Average Likes:</strong> ${data.average_likes.toFixed(2)}</p>
            <p><strong>Average Shares:</strong> ${data.average_shares.toFixed(2)}</p>
            <p><strong>Average Comments:</strong> ${data.average_comments.toFixed(2)}</p>
            <p><strong>Insights:</strong> ${data.insights}</p>
        `;
    } else {
        resultsDiv.innerHTML = `<p style="color: red;">${data.error}</p>`;
    }
});
