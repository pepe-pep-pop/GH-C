document.addEventListener('DOMContentLoaded', async () => {
  await loadActivities();
  setupForm();
});

async function loadActivities() {
  try {
    const response = await fetch('/activities');
    const activities = await response.json();
    displayActivities(activities);
    populateActivityDropdown(activities);
  } catch (error) {
    console.error('Error loading activities:', error);
    document.getElementById('activities-list').innerHTML = '<p>Error loading activities</p>';
  }
}

function displayActivities(activities) {
  const container = document.getElementById('activities-list');
  container.innerHTML = '';

  Object.entries(activities).forEach(([name, activity]) => {
    const card = document.createElement('div');
    card.className = 'activity-card';
    
    const participantsList = activity.participants.length > 0
      ? `<ul>${activity.participants.map(p => `<li>${p}</li>`).join('')}</ul>`
      : '<p class="participants-empty">No participants yet</p>';

    card.innerHTML = `
      <h4>${name}</h4>
      <p>${activity.description}</p>
      <p><strong>Schedule:</strong> ${activity.schedule}</p>
      <p><strong>Capacity:</strong> ${activity.participants.length}/${activity.max_participants}</p>
      <div class="participants">
        <h5>Participants:</h5>
        ${participantsList}
      </div>
    `;
    container.appendChild(card);
  });
}

function populateActivityDropdown(activities) {
  const select = document.getElementById('activity');
  Object.keys(activities).forEach(name => {
    const option = document.createElement('option');
    option.value = name;
    option.textContent = name;
    select.appendChild(option);
  });
}

function setupForm() {
  document.getElementById('signup-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const activity = document.getElementById('activity').value;
    const messageDiv = document.getElementById('message');

    try {
      const response = await fetch(`/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`, {
        method: 'POST'
      });

      if (response.ok) {
        messageDiv.className = 'message success';
        messageDiv.textContent = '✓ Successfully signed up!';
        messageDiv.classList.remove('hidden');
        await loadActivities();
        document.getElementById('signup-form').reset();
      } else {
        const error = await response.json();
        messageDiv.className = 'message error';
        messageDiv.textContent = '✗ ' + error.detail;
        messageDiv.classList.remove('hidden');
      }
    } catch (error) {
      messageDiv.className = 'message error';
      messageDiv.textContent = '✗ An error occurred';
      messageDiv.classList.remove('hidden');
    }
  });
}
