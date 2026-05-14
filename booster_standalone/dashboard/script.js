document.addEventListener('DOMContentLoaded', () => {
    const boostBtn = document.getElementById('boost-btn');
    const logsContainer = document.getElementById('logs');
    const inviteInput = document.getElementById('invite');
    const tokensInput = document.getElementById('tokens');
    const watermarkInput = document.getElementById('watermark');
    const tokenPoolDisplay = document.getElementById('token-pool');
    const successDisplay = document.getElementById('total-success');
    
    const redeemNav = document.getElementById('redeem-nav');
    const modal = document.getElementById('license-modal');
    const cancelModal = document.getElementById('cancel-modal');
    const redeemBtn = document.getElementById('redeem-btn');
    const licenseKeyInput = document.getElementById('license-key');

    let totalSuccess = 0;

    function addLog(message, type = '') {
        const entry = document.createElement('div');
        entry.className = `log-line ${type}`;
        const time = new Date().toLocaleTimeString();
        entry.innerText = `[${time}] ${message}`;
        logsContainer.appendChild(entry);
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }

    // Modal logic
    redeemNav.onclick = () => modal.style.display = 'flex';
    cancelModal.onclick = () => modal.style.display = 'none';
    window.onclick = (e) => { if (e.target == modal) modal.style.display = 'none'; }

    tokensInput.addEventListener('input', () => {
        const tokens = tokensInput.value.split('\n').filter(t => t.trim().length > 0);
        tokenPoolDisplay.innerText = tokens.length;
    });

    redeemBtn.onclick = async () => {
        const key = licenseKeyInput.value.trim();
        if (!key) return;

        addLog(`Verifying license key: ${key.substring(0, 8)}...`, 'system');
        const response = await fetch('/api/redeem', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key, user_id: 'WEB_USER' })
        });

        const data = await response.json();
        if (data.success) {
            addLog(data.message, 'success');
            modal.style.display = 'none';
        } else {
            addLog(data.message, 'error');
        }
    };

    boostBtn.addEventListener('click', async () => {
        const invite = inviteInput.value.trim();
        const tokens = tokensInput.value.split('\n').filter(t => t.trim().length > 0);
        const watermark = watermarkInput.value.trim();

        if (!invite || tokens.length === 0) {
            addLog('Missing initialization parameters.', 'error');
            return;
        }

        boostBtn.disabled = true;
        boostBtn.innerText = 'ACCELERATING...';
        addLog(`Injected loadout of ${tokens.length} tokens. Target: ${invite}`, 'system');

        for (const token of tokens) {
            try {
                const response = await fetch('/api/boost', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ token, invite, watermark })
                });

                const data = await response.json();
                if (data.success) {
                    totalSuccess++;
                    successDisplay.innerText = totalSuccess;
                    addLog(data.message, 'success');
                } else {
                    addLog(data.message, 'error');
                }
            } catch (err) {
                addLog('Critical connection error.', 'error');
            }
        }

        addLog('Mission completed. All threads joined.', 'system');
        boostBtn.disabled = false;
        boostBtn.innerText = 'START ACCELERATION';
    });
});
