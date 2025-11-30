let motors = [];
const motorsPerPage = 10;
let currentPage = 1;
let updateTimeout;

function getStatus(temp) {
  if (temp == null) return { label: "N/A", color: "bg-gray-100", text_color: "text-gray-600", arc: "#9CA3AF" };
  if (temp < 36) return { label: "SAFE", color: "bg-green-100", text_color:"text-green-600", arc: "#10B981" };
  if (temp < 41) return { label: "WARNING", color: "bg-orange-100", text_color:"text-orange-600", arc: "#F59E0B" };
  return { label: "DANGER", color: "bg-red-100", text_color:"text-red-600", arc: "#EF4444" };
}

function renderCounts() {
  const counts = { SAFE: 0, WARNING: 0, DANGER: 0 };
  motors.forEach(m => {
    const status = getStatus(m.temp_value);
    if (status.label in counts) counts[status.label]++;
  });
  document.getElementById("statusCounts").innerHTML = `
    <li class="flex items-center gap-x-2 text-sm text-gray-500 dark:text-gray-300">
      <p class="p-2 bg-green-600 rounded-full"></p> ${counts.SAFE} Safe
    </li>
    <li class="flex items-center gap-x-2 text-sm text-gray-500 dark:text-gray-300">
      <p class="p-2 bg-orange-600 rounded-full"></p> ${counts.WARNING} Warning
    </li>
    <li class="flex items-center gap-x-2 text-sm text-gray-500 dark:text-gray-300">
      <p class="p-2 bg-red-600 rounded-full"></p> ${counts.DANGER} Danger
    </li>
  `;
}

function renderMotors() {
  const start = (currentPage - 1) * motorsPerPage;
  const end = start + motorsPerPage;
  const pageMotors = motors.slice(start, end);

  document.getElementById("motorsContainer").innerHTML = pageMotors.map(m => {
    const temp = m.temp_value;
    const status = getStatus(temp);
    const percent = Math.min((temp ?? 0) / 120, 1);
    const dasharray = 188;
    const offset = dasharray - dasharray * percent;

    // change div → a
    return `
      <a href="/detail/${m.id}/page"
         class="motor-card dark:bg-gray-800 bg-gray-200 rounded-xl shadow-md p-5 w-80 block hover:shadow-lg transition-shadow duration-200">
        <div class="flex justify-between items-start">
          <div>
            <h2 class="text-lg font-bold text-black dark:text-white">${m.name}</h2>
            <p class="dark:text-gray-400 text-gray-500 text-sm">${m.zone}</p>
          </div>
          <span class="status text-xs px-2 py-1 rounded ${status.color} ${status.text_color}">${status.label}</span>
        </div>

        <div class="flex flex-col items-center my-6">
          <svg width="160" height="100" viewBox="0 0 160 100">
            <path d="M20 80 A60 60 0 0 1 140 80"
              stroke="#374151" stroke-width="12" fill="none" stroke-linecap="round"/>
            <path d="M20 80 A60 60 0 0 1 140 80"
              stroke="${status.arc}" stroke-width="12" fill="none" stroke-linecap="round"
              stroke-dasharray="${dasharray}" stroke-dashoffset="${offset}"/>
          </svg>
          <div class="text-center -mt-6">
            <p class="temp text-2xl font-bold text-black dark:text-white">${temp ?? 'N/A'}°C</p>
            <p class="label dark:text-gray-400 text-gray-500 text-sm">${status.label}</p>
          </div>
        </div>

        <div class="flex flex-col gap-1 text-xs dark:text-gray-400 text-gray-500">
          <div><strong>Vibration:</strong> ${m.vibration_value ?? 'N/A'} (at ${m.vibration_time})</div>
          <div><strong>Humidity:</strong> ${m.humidity_value ?? 'N/A'} (at ${m.humidity_time})</div>
          <div class="flex justify-between mt-1">
            <span class="dark:bg-gray-700 bg-gray-300 px-2 py-1 rounded text-sm">${m.id}</span>
            <span>${m.temp_time}</span>
          </div>
        </div>
      </a>
    `;
  }).join("");
}

function renderPagination() {
  const totalPages = Math.ceil(motors.length / motorsPerPage);
  let buttons = "";
  for (let i = 1; i <= totalPages; i++) {
    buttons += `
      <button onclick="goToPage(${i})"
        class="px-3 py-1 rounded ${i === currentPage ? 'bg-blue-600 text-white' : 'bg-gray-300 dark:bg-gray-700 text-black dark:text-white'} transition-colors duration-150">
        ${i}
      </button>
    `;
  }
  document.getElementById("pagination").innerHTML = buttons;
}

function goToPage(page) {
  currentPage = page;
  renderMotors();
  renderPagination();
}

// Optimized render with RequestAnimationFrame for smooth updates
function scheduleRender() {
  clearTimeout(updateTimeout);
  updateTimeout = setTimeout(() => {
    requestAnimationFrame(() => {
      renderCounts();
      renderMotors();
      renderPagination();
    });
  }, 100); // Debounce rapid updates
}

let lastPayload = "";

document.addEventListener("DOMContentLoaded", () => {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const ws = new WebSocket(`${protocol}://${window.location.host}/ws/motors`);
  console.log("WebSocket connecting...");
  
  ws.onopen = () => {
    console.log("WebSocket connected - ready for real-time updates");
  };

  ws.onmessage = (event) => {
    const newMotors = JSON.parse(event.data);
    motors = newMotors;
    scheduleRender();
  };

  ws.onerror = (error) => {
    console.error("WebSocket error:", error);
  };

  ws.onclose = () => {
    console.log("WebSocket closed - attempting to reconnect in 3 seconds");
    setTimeout(() => {
      location.reload(); // Reload to reconnect
    }, 3000);
  };
});