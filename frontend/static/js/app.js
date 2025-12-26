// Basic State
const state = {
    token: localStorage.getItem('token'),
    user: localStorage.getItem('user_name')
};

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    updateUI();
    setInterval(updateClock, 1000);
    if (state.token) {
        fetchProfile();
        fetchHealthLogs();
    }
});

function updateUI() {
    const navLinks = document.getElementById('nav-links');
    const authLinks = document.getElementById('auth-links');
    const dashboard = document.getElementById('dashboard-content');
    const landing = document.getElementById('landing-content');
    const userNameDisplay = document.getElementById('user-display-name');

    if (state.token) {
        navLinks.classList.remove('hidden');
        authLinks.classList.add('hidden');
        dashboard.classList.remove('hidden');
        landing.classList.add('hidden');
        if (state.user) userNameDisplay.textContent = state.user;
    } else {
        navLinks.classList.add('hidden');
        authLinks.classList.remove('hidden');
        dashboard.classList.add('hidden');
        landing.classList.remove('hidden');
    }
}

function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { hour12: false });
    const dateString = now.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'short', day: 'numeric' });
    
    const clockEl = document.getElementById('digital-clock');
    const dateEl = document.getElementById('current-date');
    
    if (clockEl) clockEl.textContent = timeString;
    if (dateEl) dateEl.textContent = dateString;
}

function logout() {
    localStorage.clear();
    window.location.href = '/';
}

// Navigation
window.showSection = function(sectionName) {
    document.querySelectorAll('.section-block').forEach(el => el.classList.add('hidden'));
    const target = document.getElementById(`section-${sectionName}`);
    if (target) {
        target.classList.remove('hidden');
        target.scrollIntoView({ behavior: 'smooth' });
    }
}

// Profile Logic
const profileForm = document.getElementById('profile-form');
if (profileForm) {
    profileForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(profileForm);
        const data = Object.fromEntries(formData.entries());
        
        if (!confirm('Are you sure you want to update your profile?')) return;

        try {
            const res = await fetch('/api/profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${state.token}`
                },
                body: JSON.stringify(data)
            });
            const resData = await res.json();
            alert(resData.msg);
            if (resData.recommendations) displayRecommendations(resData.recommendations);
        } catch (err) {
            console.error(err);
        }
    });
}

function displayRecommendations(recs) {
    const container = document.getElementById('exercise-recommendations');
    const list = document.getElementById('rec-list');
    list.innerHTML = '';
    recs.forEach(r => {
        const li = document.createElement('li');
        li.textContent = r;
        list.appendChild(li);
    });
    container.classList.remove('hidden');
}

async function fetchProfile() {
    try {
        const res = await fetch('/api/profile', {
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
        const data = await res.json();
        if (data.age) {
            document.getElementById('p-age').value = data.age;
            document.getElementById('p-gender').value = data.gender;
            document.getElementById('p-height').value = data.height;
            document.getElementById('p-weight').value = data.weight;
            document.getElementById('p-activity').value = data.activity_level;
            if (data.recommended_exercises) displayRecommendations(data.recommended_exercises);
        }
    } catch (err) {
        console.error("Failed to fetch profile");
    }
}

// Health Logs & Charts Logic
let hrChart, bpChart;
const healthForm = document.getElementById('health-log-form');

if (healthForm) {
    healthForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            heart_rate: document.getElementById('h-hr').value,
            bp_systolic: document.getElementById('h-sys').value,
            bp_diastolic: document.getElementById('h-dia').value,
            blood_sugar: document.getElementById('h-sugar').value
        };

        try {
            const res = await fetch('/api/health/log', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${state.token}`
                },
                body: JSON.stringify(data)
            });
            const resData = await res.json();
            alert('Logged!');
            if(resData.alerts && resData.alerts.length > 0) {
                alert('WARNING: ' + resData.alerts.join(', '));
            }
            healthForm.reset();
            fetchHealthLogs(); // Refresh charts
        } catch (err) {
            console.error(err);
        }
    });
}

async function fetchHealthLogs() {
    try {
        const res = await fetch('/api/health/logs', {
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
        const data = await res.json();
        updateCharts(data);
        if (data.length > 0) {
            document.getElementById('display-hr').textContent = data[0].heart_rate + " bpm";
            document.getElementById('display-bp').textContent = `${data[0].bp_systolic}/${data[0].bp_diastolic}`;
        }
    } catch (err) {
        console.error(err);
    }
}

function updateCharts(data) {
    // Reverse data to show oldest to newest left to right
    const reversedData = [...data].reverse();
    const labels = reversedData.map(d => new Date(d.timestamp).toLocaleDateString());
    
    // HR Chart
    const ctxHr = document.getElementById('chart-hr');
    if (ctxHr) {
        if (hrChart) hrChart.destroy();
        hrChart = new Chart(ctxHr, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Heart Rate',
                    data: reversedData.map(d => d.heart_rate),
                    borderColor: '#ef4444',
                    tension: 0.4
                }]
            },
            options: { responsive: true, plugins: { legend: { labels: { color: 'white' } } }, scales: { x: { ticks: { color: 'gray' } }, y: { ticks: { color: 'gray' } } } }
        });
    }

    // BP Chart
    const ctxBp = document.getElementById('chart-bp');
    if (ctxBp) {
        if (bpChart) bpChart.destroy();
        bpChart = new Chart(ctxBp, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Systolic',
                        data: reversedData.map(d => d.bp_systolic),
                        borderColor: '#3b82f6',
                        tension: 0.4
                    },
                    {
                        label: 'Diastolic',
                        data: reversedData.map(d => d.bp_diastolic),
                        borderColor: '#60a5fa',
                        tension: 0.4
                    }
                ]
            },
            options: { responsive: true, plugins: { legend: { labels: { color: 'white' } } }, scales: { x: { ticks: { color: 'gray' } }, y: { ticks: { color: 'gray' } } } }
        });
    }
}

// Medication Logic
const medForm = document.getElementById('medication-form');
if (medForm) {
    medForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            name: document.getElementById('m-name').value,
            dosage: document.getElementById('m-dosage').value,
            frequency: document.getElementById('m-frequency').value,
            time: document.getElementById('m-time').value
        };
        
        try {
            const res = await fetch('/api/medication', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${state.token}`
                },
                body: JSON.stringify(data)
            });
            if (res.ok) {
                alert('Medication added!');
                medForm.reset();
                fetchMedications();
            } else {
                alert('Error adding medication');
            }
        } catch (err) { console.error(err); }
    });
}

async function fetchMedications() {
    try {
        const res = await fetch('/api/medication', {
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
        const data = await res.json();
        renderMedications(data);
    } catch (err) { console.error(err); }
}

function renderMedications(meds) {
    const list = document.getElementById('medication-list');
    list.innerHTML = '';
    
    if (meds.length === 0) {
        list.innerHTML = '<p class="text-gray-500 text-center">No medications scheduled.</p>';
        return;
    }
    
    meds.forEach(med => {
        const el = document.createElement('div');
        el.className = 'bg-gray-800 p-4 rounded-lg flex justify-between items-center border border-gray-700';
        el.innerHTML = `
            <div>
                <h4 class="font-bold text-white">${med.name} <span class="text-xs text-gray-400 ml-2">(${med.dosage})</span></h4>
                <p class="text-sm text-secondary"><i class="fa-solid fa-clock mr-1"></i> ${med.time} • ${med.frequency}</p>
            </div>
            <button onclick="deleteMed('${med._id}')" class="text-gray-500 hover:text-red-400 transition"><i class="fa-solid fa-trash"></i></button>
        `;
        list.appendChild(el);
    });
}

window.deleteMed = async (id) => {
    if(!confirm('Remove this medication?')) return;
    try {
        await fetch(`/api/medication/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
        fetchMedications();
    } catch (err) { console.error(err); }
};

// Risk Logic
window.calculateRisk = async () => {
    try {
        const res = await fetch('/api/health/risk', {
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
        const data = await res.json();
        
        // Update UI
        const scoreEl = document.getElementById('risk-score-value');
        const levelEl = document.getElementById('risk-level-text');
        const circle = document.getElementById('risk-circle');
        const factorsContainer = document.getElementById('risk-factors-container');
        const factorsList = document.getElementById('risk-factors-list');
        
        // Animate Score
        if (scoreEl) scoreEl.textContent = data.score;
        
        // Update Circle (Circumference ~ 552)
        const offset = 552 - (552 * data.score / 100);
        if (circle) circle.style.strokeDashoffset = offset;
        
        // Update Colors/Text
        let color = 'text-green-500';
        let stroke = '#10B981';
        if (data.score > 30) { color = 'text-yellow-500'; stroke = '#EAB308'; }
        if (data.score > 60) { color = 'text-red-500'; stroke = '#EF4444'; }
        
        if (levelEl) {
            levelEl.className = `text-3xl font-bold ${color} mb-4`;
            levelEl.textContent = data.level + " Risk";
        }
        if (circle) circle.style.color = stroke;
        
        // Factors
        if (data.factors && data.factors.length > 0) {
            factorsContainer.classList.remove('hidden');
            factorsList.innerHTML = '';
            data.factors.forEach(f => {
                const li = document.createElement('li');
                li.textContent = f;
                factorsList.appendChild(li);
            });
        } else {
            factorsContainer.classList.add('hidden');
        }
        
    } catch (err) { console.error(err); }
};

// Load risk score for dashboard
async function loadDashboardRisk() {
    try {
        const res = await fetch('/api/health/risk', {
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
        const data = await res.json();
        
        const riskDisplay = document.getElementById('risk-score-display');
        if (riskDisplay) {
            riskDisplay.textContent = data.level || '--';
            riskDisplay.className = 'text-3xl font-bold mt-2 ' + 
                (data.score > 60 ? 'text-red-500' : (data.score > 30 ? 'text-yellow-500' : 'text-green-500'));
        }
    } catch (err) {
        console.error('Failed to load risk score:', err);
    }
}

document.addEventListener('DOMContentLoaded', () => {
   if (state.token) {
       fetchMedications();
       fetchHealthLogs();
       loadDashboardRisk();
       // Pre-calc risk if user visits
       if (document.getElementById('risk-score-value')) {
           calculateRisk();
       }
   }
});
