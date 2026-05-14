document.addEventListener('DOMContentLoaded', () => {
    const boostBtn = document.getElementById('boost-btn');
    const logsContainer = document.getElementById('logs');
    const inviteInput = document.getElementById('invite');
    const tokensInput = document.getElementById('tokens');
    const tokenCountDisplay = document.getElementById('token-count');
    const activeTokensDisplay = document.getElementById('active-tokens');
    const successRateDisplay = document.getElementById('success-rate');
    const totalBoostsDisplay = document.getElementById('total-boosts');
    const clearLogsBtn = document.getElementById('clear-logs');

    let totalTokens = 0;
    let successfulBoosts = 0;
    let completedCount = 0;

    function addLog(message, type = '') {
        const entry = document.createElement('div');
        entry.className = `log-entry ${type}`;
        const time = new Date().toLocaleTimeString();
        entry.innerText = `[${time}] ${message}`;
        logsContainer.prepend(entry);
    }

    tokensInput.addEventListener('input', () => {
        const tokens = tokensInput.value.split('\n').filter(t => t.trim().length > 0);
        tokenCountDisplay.innerText = tokens.length;
        activeTokensDisplay.innerText = tokens.length;
    });

    clearLogsBtn.addEventListener('click', () => {
        logsContainer.innerHTML = '<div class="log-entry system">Logs cleared.</div>';
    });

    boostBtn.addEventListener('click', async () => {
        const invite = inviteInput.value.trim();
        const tokens = tokensInput.value.split('\n').filter(t => t.trim().length > 0);

        if (!invite) {
            addLog('Please provide a server invite link.', 'error');
            return;
        }

        if (tokens.length === 0) {
            addLog('Please provide at least one token.', 'error');
            return;
        }

        boostBtn.disabled = true;
        boostBtn.querySelector('.btn-text').style.opacity = '0';
        boostBtn.querySelector('.loader').style.display = 'block';

        addLog(`Starting initialization for ${tokens.length} tokens...`, 'system');

        completedCount = 0;
        successfulBoosts = 0;

        for (const token of tokens) {
            try {
                addLog(`Processing token: ${token.substring(0, 10)}...`, '');
                
                const response = await fetch('/api/boost', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ token, invite })
                });

                const data = await response.json();
                completedCount++;

                if (data.success) {
                    successfulBoosts++;
                    addLog(data.message, 'success');
                } else {
                    addLog(data.message, 'error');
                }

                // Update UI stats
                const rate = Math.round((successfulBoosts / completedCount) * 100);
                successRateDisplay.innerText = `${rate}%`;
                totalBoostsDisplay.innerText = successfulBoosts;

            } catch (err) {
                completedCount++;
                addLog(`Network error on token ${token.substring(0, 10)}...`, 'error');
            }
        }

        addLog('All operations completed.', 'system');
        boostBtn.disabled = false;
        boostBtn.querySelector('.btn-text').style.opacity = '1';
        boostBtn.querySelector('.loader').style.display = 'none';
    });
});
