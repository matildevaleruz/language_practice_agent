document.addEventListener('DOMContentLoaded', () => {
	// Elements
	const settingsForm = document.getElementById('settings-form');
	const startBtn = document.getElementById('start-btn');
	const conversationPane = document.getElementById('conversation-pane');
	const emptyState = document.getElementById('empty-state');
	const userInput = document.getElementById('user-input');
	const sendButton = document.getElementById('send-button');
	const finishButton = document.getElementById('finish-button');
	const sessionList = document.getElementById('session-list');
	const langDisplay = document.getElementById('current-language-display');
	const levelDisplay = document.getElementById('current-level-display');

	let currentSessionId = null;
	let isSessionActive = false;

	// --- Event Listeners ---

	settingsForm.addEventListener('submit', async(e) => {
		e.preventDefault();
		const formData = new FormData(settingsForm);
		const settings = Object.fromEntries(formData.entries());

		// UI Feedback: Loading
		startBtn.textContent = 'Starting...';
		startBtn.disabled = true;

		try {
			const response = await fetch('/start-session', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(settings)
			});

			if (!response.ok)
				throw new Error('Failed to start session');

			const data = await response.json();
			currentSessionId = data.session_id;

			// UI Updates
			startSessionUI(data.assistant_message, settings.language, settings.level);

			// Add to Sidebar List
			addSessionToSidebar(currentSessionId, settings.language, settings.level);

		} catch (error) {
			console.error(error);
			alert("Could not start session. Please check console.");
			startBtn.textContent = 'Start Session';
			startBtn.disabled = false;
		}
	});

	sendButton.addEventListener('click', sendMessage);

	finishButton.addEventListener('click', async() => {
		if (!currentSessionId)
			return;

		// UI Feedback
		finishButton.textContent = 'Finishing...';
		finishButton.disabled = true;
		userInput.disabled = true;

		try {
			const response = await fetch('/finish-session', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					session_id: currentSessionId
				})
			});

			const data = await response.json();
			displayFeedback(data.feedback);
			endSessionUI();

		} catch (error) {
			console.error(error);
			finishButton.textContent = 'Finish Session';
			finishButton.disabled = false;
		}
	});

	// Enter Key Support
	userInput.addEventListener('keydown', (e) => {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault(); // Prevent new line
			sendMessage();
		}
	});

	// --- Functions ---

	async function sendMessage() {
		const text = userInput.value.trim();
		if (!text || !currentSessionId)
			return;

		// Add User Message
		addMessage('user', text);
		userInput.value = '';

		// UI Loading state
		userInput.disabled = true;
		sendButton.disabled = true;

		try {
			const response = await fetch('/chat', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					session_id: currentSessionId,
					text: text
				})
			});

			const data = await response.json();
			addMessage('assistant', data.assistant_message);

		} catch (error) {
			console.error(error);
			addMessage('assistant', "Sorry, I'm having trouble connecting.");
		} finally {
			if (isSessionActive) {
				userInput.disabled = false;
				sendButton.disabled = false;
				userInput.focus();
			}
		}
	}

	function startSessionUI(initialMessage, lang, level) {
		isSessionActive = true;
		emptyState.style.display = 'none';

		// Update Header
		const langMap = {
			es: 'Spanish',
			fr: 'French',
			de: 'German',
			it: 'Italian',
			pt: 'Portuguese'
		};
		langDisplay.textContent = `${langMap[lang] || lang} Practice`;
		levelDisplay.textContent = `Level ${level}`;
		levelDisplay.classList.add('active');

		// Enable Chat
		userInput.disabled = false;
		sendButton.disabled = false;
		finishButton.disabled = false;
		finishButton.textContent = 'Finish Session';
		startBtn.textContent = 'Restart Session'; // Allow restarting with new settings
		startBtn.disabled = false;

		// Add Initial Bot Message
		addMessage('assistant', initialMessage);
		userInput.focus();
	}

	function endSessionUI() {
		isSessionActive = false;
		currentSessionId = null;

		// Disable Inputs
		userInput.disabled = true;
		sendButton.disabled = true;
		finishButton.disabled = true;

		// Reset Header
		levelDisplay.classList.remove('active');
	}

	function addMessage(sender, message) {
		const messageWrapper = document.createElement('div');
		messageWrapper.classList.add('message', `${sender}-message`);

		const senderName = document.createElement('div');
		senderName.classList.add('sender-name');
		senderName.textContent = sender === 'user' ? 'You' : 'Tutor';

		const bubble = document.createElement('div');
		bubble.classList.add('bubble');
		bubble.textContent = message; // textContent prevents HTML injection attacks

		messageWrapper.appendChild(senderName);
		messageWrapper.appendChild(bubble);
		conversationPane.appendChild(messageWrapper);

		scrollToBottom();
	}

	function displayFeedback(feedback) {
		const feedbackWrapper = document.createElement('div');
		feedbackWrapper.classList.add('feedback-card');

		// Construct the feedback HTML safely (using template literals but known data structure)
		// Note: In a production app with real backend, ensure the backend escapes user input
		// or use a sanitizer library. Here we assume the backend returns safe HTML strings.

		let correctionsHtml = '';
		if (feedback.corrections && feedback.corrections.length > 0) {
			correctionsHtml = feedback.corrections.map(c => `
		<table class="correction-item">
			<tr><td><b>Your text:</b></td><td>${escapeHtml(c.user_text)}</td></tr>
			<tr><td><b>Corrected:</b></td><td>${escapeHtml(c.corrected_text)}</td></tr>
			<tr><td><b>Explanation:</b></td><td>${escapeHtml(c.explanation)}</td></tr>
		</table>
	    `).join('');
		} else {
			correctionsHtml = '<li>No major corrections. Great job!</li>';
		}

		let strengthsHtml = feedback.strengths ? feedback.strengths.map(s => `<li>${escapeHtml(s)}</li>`).join('') : '';
		let weaknessesHtml = feedback.weaknesses ? feedback.weaknesses.map(w => `<li>${escapeHtml(w)}</li>`).join('') : '';
		let recommendationsHtml = feedback.recommendations ? feedback.recommendations.map(r => `<li>${escapeHtml(r)}</li>`).join('') : '';

		feedbackWrapper.innerHTML = `
	    <h3>Session Feedback</h3>
	    <h4>Corrections</h4>
	    <div class="corrections-list">${correctionsHtml}</div>

	    <h4>Strengths</h4>
	    <ul>${strengthsHtml}</ul>

	    <h4>Areas to Improve</h4>
	    <ul>${weaknessesHtml}</ul>

	    <h4>Recommendations</h4>
	    <ul>${recommendationsHtml}</ul>
	`;

		conversationPane.appendChild(feedbackWrapper);
		scrollToBottom();
	}

	function addSessionToSidebar(id, lang, level) {
		const li = document.createElement('li');
		li.classList.add('session-item');
		// Simple SVG icon
		li.innerHTML = `
	    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
	    <span>${lang.toUpperCase()} - ${level} <small>(${new Date().toLocaleTimeString([], {
				hour: '2-digit',
				minute: '2-digit'
			})})</small></span>
	`;
		sessionList.prepend(li);
	}

	function scrollToBottom() {
		conversationPane.scrollTop = conversationPane.scrollHeight;
	}

	// Basic HTML escape function for safety
	function escapeHtml(text) {
		if (!text)
			return '';
		return text
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;")
		.replace(/"/g, "&quot;")
		.replace(/'/g, "&#039;");
	}
});