// Global data storage (simulating persistence)
let foodEntries = [
    {"date": "2025-01-15", "time": "08:30", "food_items": ["Oatmeal", "Banana", "Almond milk"], "calories": 320, "protein": 12, "carbs": 58, "fat": 8, "meal_type": "Breakfast"},
    {"date": "2025-01-15", "time": "12:45", "food_items": ["Grilled chicken salad", "Olive oil dressing"], "calories": 450, "protein": 35, "carbs": 15, "fat": 28, "meal_type": "Lunch"},
    {"date": "2025-01-14", "time": "19:00", "food_items": ["Salmon", "Quinoa", "Broccoli"], "calories": 520, "protein": 40, "carbs": 42, "fat": 18, "meal_type": "Dinner"}
];

let weightEntries = [
    {"date": "2025-01-15", "time": "07:00", "weight": 75.2, "context": "Wake up", "notes": ""},
    {"date": "2025-01-15", "time": "20:30", "weight": 76.1, "context": "Before sleep", "notes": "After dinner"},
    {"date": "2025-01-14", "time": "07:15", "weight": 75.5, "context": "Wake up", "notes": ""},
    {"date": "2025-01-13", "time": "07:00", "weight": 75.8, "context": "Wake up", "notes": ""}
];

let sleepEntries = [
    {"date": "2025-01-14", "sleep_time": "23:30", "wake_time": "07:00", "duration": 7.5, "quality": 8, "notes": "Good sleep"},
    {"date": "2025-01-13", "sleep_time": "00:15", "wake_time": "07:15", "duration": 7.0, "quality": 6, "notes": "Woke up once"},
    {"date": "2025-01-12", "sleep_time": "23:45", "wake_time": "07:00", "duration": 7.25, "quality": 9, "notes": "Excellent sleep"}
];

const foodRecognitionFoods = [
    "Apple", "Banana", "Chicken breast", "Salmon", "Broccoli", "Rice", "Pasta", "Salad", "Pizza", "Burger", 
    "Oatmeal", "Eggs", "Yogurt", "Avocado", "Bread", "Quinoa", "Sweet potato", "Almonds", "Greek yogurt", "Spinach"
];

let charts = {};

// Navigation function - make it globally accessible
function showTab(tabId) {
    console.log('Switching to tab:', tabId);
    
    // Hide all content sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    // Remove active class from all nav buttons
    const buttons = document.querySelectorAll('.nav-btn');
    buttons.forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    const targetSection = document.getElementById(tabId);
    const targetButton = document.querySelector(`[data-tab="${tabId}"]`);
    
    if (targetSection) {
        targetSection.classList.add('active');
        console.log('Activated section:', tabId);
    }
    
    if (targetButton) {
        targetButton.classList.add('active');
        console.log('Activated button for:', tabId);
    }

    // Refresh charts when analytics tab is shown
    if (tabId === 'analytics' && charts.weightChart) {
        setTimeout(() => {
            updateCharts();
        }, 200);
    }
}

// Make navigation globally accessible
window.showTab = showTab;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded - Initializing app...');
    
    // Set up navigation immediately
    setupNavigation();
    
    // Initialize other components
    setDefaultDates();
    setupOtherEventListeners();
    updateAllDisplays();
    
    // Initialize charts after DOM is ready
    setTimeout(() => {
        initializeCharts();
    }, 500);
});

function setupNavigation() {
    console.log('Setting up navigation...');
    
    // Get all navigation buttons
    const navButtons = document.querySelectorAll('.nav-btn');
    console.log('Found navigation buttons:', navButtons.length);
    
    // Add click listeners to each button
    navButtons.forEach((button, index) => {
        const tabId = button.getAttribute('data-tab');
        console.log(`Setting up button ${index + 1}: ${tabId}`);
        
        // Remove any existing listeners
        button.removeEventListener('click', handleNavClick);
        
        // Add new listener
        button.addEventListener('click', handleNavClick);
        
        // Also add direct onclick attribute as backup
        button.onclick = function(e) {
            e.preventDefault();
            e.stopPropagation();
            showTab(tabId);
            return false;
        };
    });
    
    // Show initial tab
    showTab('food-tracker');
    console.log('Navigation setup complete');
}

function handleNavClick(event) {
    event.preventDefault();
    event.stopPropagation();
    
    const tabId = this.getAttribute('data-tab');
    console.log('Navigation clicked:', tabId);
    showTab(tabId);
    
    return false;
}

function setupOtherEventListeners() {
    console.log('Setting up other event listeners...');
    
    // Food photo upload
    setupFileUpload();
    
    // Sleep quality slider
    const sleepQualitySlider = document.getElementById('sleepQuality');
    if (sleepQualitySlider) {
        sleepQualitySlider.addEventListener('input', function() {
            document.getElementById('qualityValue').textContent = this.value;
        });
    }

    // Set current time for weight logging
    const weightTimeInput = document.getElementById('weightTime');
    if (weightTimeInput) {
        const now = new Date();
        weightTimeInput.value = now.toTimeString().slice(0, 5);
    }
    
    console.log('Other event listeners setup complete');
}

function setupFileUpload() {
    console.log('Setting up file upload...');
    
    const foodPhotoInput = document.getElementById('foodPhoto');
    const uploadLabel = document.querySelector('.upload-label');
    
    if (foodPhotoInput && uploadLabel) {
        // File input change event
        foodPhotoInput.addEventListener('change', handleFoodPhotoUpload);
        
        // Upload label click event
        uploadLabel.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Upload area clicked, triggering file input...');
            foodPhotoInput.click();
            return false;
        });
        
        // Also add onclick as backup
        uploadLabel.onclick = function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Upload area onclick triggered');
            foodPhotoInput.click();
            return false;
        };
        
        console.log('File upload setup complete');
    } else {
        console.error('File upload elements not found');
    }
}

function setDefaultDates() {
    const today = new Date().toISOString().split('T')[0];
    const dateInputs = ['foodDate', 'sleepDate'];
    
    dateInputs.forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.value = today;
        }
    });

    // Set current time for food logging
    const foodTimeInput = document.getElementById('foodTime');
    if (foodTimeInput) {
        const now = new Date();
        foodTimeInput.value = now.toTimeString().slice(0, 5);
    }
}

function handleFoodPhotoUpload(event) {
    console.log('Food photo upload triggered');
    const file = event.target.files[0];
    if (!file) {
        console.log('No file selected');
        return;
    }

    console.log('File selected:', file.name);
    const imagePreview = document.getElementById('imagePreview');
    const nutritionAnalysis = document.getElementById('nutritionAnalysis');

    // Show image preview
    const reader = new FileReader();
    reader.onload = function(e) {
        imagePreview.innerHTML = `<img src="${e.target.result}" alt="Food preview">`;
        imagePreview.classList.remove('hidden');
        
        // Simulate nutrition analysis
        setTimeout(() => {
            performMockFoodAnalysis();
            nutritionAnalysis.classList.remove('hidden');
        }, 1500);
    };
    
    reader.readAsDataURL(file);
}

function performMockFoodAnalysis() {
    // Mock food recognition
    const randomFoods = getRandomFoods(2, 4);
    const mockNutrition = generateMockNutrition(randomFoods);
    
    document.getElementById('detectedFoodsList').textContent = randomFoods.join(', ');
    document.getElementById('calories').textContent = mockNutrition.calories;
    document.getElementById('protein').textContent = mockNutrition.protein;
    document.getElementById('carbs').textContent = mockNutrition.carbs;
    document.getElementById('fat').textContent = mockNutrition.fat;
}

function getRandomFoods(min, max) {
    const count = Math.floor(Math.random() * (max - min + 1)) + min;
    const shuffled = [...foodRecognitionFoods].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, count);
}

function generateMockNutrition(foods) {
    const baseCalories = foods.length * (120 + Math.random() * 180);
    return {
        calories: Math.round(baseCalories),
        protein: Math.round(baseCalories * 0.15 / 4),
        carbs: Math.round(baseCalories * 0.45 / 4),
        fat: Math.round(baseCalories * 0.35 / 9)
    };
}

function saveFoodEntry() {
    const detectedFoods = document.getElementById('detectedFoodsList').textContent;
    if (!detectedFoods) {
        showMessage('Please upload a food photo first', 'error');
        return;
    }

    const entry = {
        date: document.getElementById('foodDate').value,
        time: document.getElementById('foodTime').value,
        food_items: detectedFoods.split(', '),
        calories: parseInt(document.getElementById('calories').textContent),
        protein: parseInt(document.getElementById('protein').textContent),
        carbs: parseInt(document.getElementById('carbs').textContent),
        fat: parseInt(document.getElementById('fat').textContent),
        meal_type: document.getElementById('mealType').value
    };

    foodEntries.unshift(entry);
    showMessage('Food entry saved successfully!', 'success');
    
    // Reset form
    document.getElementById('foodPhoto').value = '';
    document.getElementById('imagePreview').classList.add('hidden');
    document.getElementById('nutritionAnalysis').classList.add('hidden');
    
    updateAllDisplays();
}

function saveWeightEntry() {
    const weightValue = document.getElementById('weightValue').value;
    if (!weightValue) {
        showMessage('Please enter a weight value', 'error');
        return;
    }

    const entry = {
        date: new Date().toISOString().split('T')[0],
        time: document.getElementById('weightTime').value,
        weight: parseFloat(weightValue),
        context: document.getElementById('weightContext').value,
        notes: document.getElementById('weightNotes').value
    };

    weightEntries.unshift(entry);
    showMessage('Weight entry saved successfully!', 'success');
    
    // Reset form
    document.getElementById('weightValue').value = '';
    document.getElementById('weightNotes').value = '';
    
    updateAllDisplays();
}

function saveSleepEntry() {
    const sleepTime = document.getElementById('sleepTime').value;
    const wakeTime = document.getElementById('wakeTime').value;
    
    if (!sleepTime || !wakeTime) {
        showMessage('Please enter both sleep and wake times', 'error');
        return;
    }

    const duration = calculateSleepDuration(sleepTime, wakeTime);
    
    const entry = {
        date: document.getElementById('sleepDate').value,
        sleep_time: sleepTime,
        wake_time: wakeTime,
        duration: duration,
        quality: parseInt(document.getElementById('sleepQuality').value),
        notes: document.getElementById('sleepNotes').value
    };

    sleepEntries.unshift(entry);
    showMessage('Sleep entry saved successfully!', 'success');
    
    // Reset form
    document.getElementById('sleepNotes').value = '';
    
    updateAllDisplays();
}

function calculateSleepDuration(sleepTime, wakeTime) {
    const sleep = new Date(`2000-01-01 ${sleepTime}`);
    let wake = new Date(`2000-01-01 ${wakeTime}`);
    
    // If wake time is earlier than sleep time, assume it's the next day
    if (wake < sleep) {
        wake.setDate(wake.getDate() + 1);
    }
    
    const duration = (wake - sleep) / (1000 * 60 * 60); // Convert to hours
    return Math.round(duration * 100) / 100; // Round to 2 decimal places
}

function importAppleHealth() {
    showMessage('Apple Health integration would be implemented here. Mock data imported!', 'success');
    
    // Add mock sleep entry
    const mockEntry = {
        date: new Date().toISOString().split('T')[0],
        sleep_time: "23:15",
        wake_time: "07:30",
        duration: 8.25,
        quality: 8,
        notes: "Imported from Apple Health"
    };
    
    sleepEntries.unshift(mockEntry);
    updateAllDisplays();
}

function updateAllDisplays() {
    updateRecentFoodsTable();
    updateTodaysWeightsTable();
    updateWeightStats();
    updateRecentSleepTable();
    updateSummaryStats();
    
    if (charts.weightChart) {
        updateCharts();
    }
}

function updateRecentFoodsTable() {
    const container = document.getElementById('recentFoodsTable');
    const recentEntries = foodEntries.slice(0, 5);
    
    if (recentEntries.length === 0) {
        container.innerHTML = '<div class="empty-state"><span>🍽️</span><p>No food entries yet</p></div>';
        return;
    }
    
    const table = `
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Food Items</th>
                    <th>Calories</th>
                    <th>Meal Type</th>
                </tr>
            </thead>
            <tbody>
                ${recentEntries.map(entry => `
                    <tr>
                        <td>${entry.date}</td>
                        <td>${entry.time}</td>
                        <td>${entry.food_items.join(', ')}</td>
                        <td>${entry.calories} kcal</td>
                        <td>${entry.meal_type}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = table;
}

function updateTodaysWeightsTable() {
    const container = document.getElementById('todaysWeightsTable');
    const today = new Date().toISOString().split('T')[0];
    const todaysEntries = weightEntries.filter(entry => entry.date === today);
    
    if (todaysEntries.length === 0) {
        container.innerHTML = '<div class="empty-state"><span>⚖️</span><p>No weight entries for today</p></div>';
        return;
    }
    
    const table = `
        <table>
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Weight</th>
                    <th>Context</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
                ${todaysEntries.map(entry => `
                    <tr>
                        <td>${entry.time}</td>
                        <td>${entry.weight} kg</td>
                        <td>${entry.context}</td>
                        <td>${entry.notes || '-'}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = table;
}

function updateWeightStats() {
    const latestWeightElement = document.getElementById('latestWeight');
    const weightChangeElement = document.getElementById('weightChange');
    
    if (weightEntries.length === 0) {
        latestWeightElement.textContent = '-- kg';
        weightChangeElement.textContent = '-- kg';
        return;
    }
    
    // Sort by date and time to get latest
    const sortedEntries = [...weightEntries].sort((a, b) => {
        const dateA = new Date(`${a.date} ${a.time}`);
        const dateB = new Date(`${b.date} ${b.time}`);
        return dateB - dateA;
    });
    
    const latest = sortedEntries[0];
    latestWeightElement.textContent = `${latest.weight} kg`;
    
    // Calculate change from yesterday
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const yesterdayStr = yesterday.toISOString().split('T')[0];
    
    const yesterdayEntry = weightEntries.find(entry => entry.date === yesterdayStr);
    if (yesterdayEntry) {
        const change = latest.weight - yesterdayEntry.weight;
        const changeStr = change >= 0 ? `+${change.toFixed(1)}` : change.toFixed(1);
        weightChangeElement.textContent = `${changeStr} kg`;
        weightChangeElement.className = `stat-value ${change >= 0 ? 'text-warning' : 'text-success'}`;
    } else {
        weightChangeElement.textContent = '-- kg';
        weightChangeElement.className = 'stat-value';
    }
}

function updateRecentSleepTable() {
    const container = document.getElementById('recentSleepTable');
    const recentEntries = sleepEntries.slice(0, 5);
    
    if (recentEntries.length === 0) {
        container.innerHTML = '<div class="empty-state"><span>😴</span><p>No sleep entries yet</p></div>';
        return;
    }
    
    const table = `
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Sleep Time</th>
                    <th>Wake Time</th>
                    <th>Duration</th>
                    <th>Quality</th>
                </tr>
            </thead>
            <tbody>
                ${recentEntries.map(entry => `
                    <tr>
                        <td>${entry.date}</td>
                        <td>${entry.sleep_time}</td>
                        <td>${entry.wake_time}</td>
                        <td>${entry.duration}h</td>
                        <td>${entry.quality}/10</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = table;
}

function updateSummaryStats() {
    // Average weight
    const avgWeightElement = document.getElementById('avgWeight');
    if (weightEntries.length > 0) {
        const avgWeight = weightEntries.reduce((sum, entry) => sum + entry.weight, 0) / weightEntries.length;
        avgWeightElement.textContent = `${avgWeight.toFixed(1)} kg`;
    }
    
    // Average sleep
    const avgSleepElement = document.getElementById('avgSleep');
    if (sleepEntries.length > 0) {
        const avgSleep = sleepEntries.reduce((sum, entry) => sum + entry.duration, 0) / sleepEntries.length;
        avgSleepElement.textContent = `${avgSleep.toFixed(1)} hrs`;
    }
    
    // Average calories
    const avgCaloriesElement = document.getElementById('avgCalories');
    if (foodEntries.length > 0) {
        const dailyCalories = {};
        foodEntries.forEach(entry => {
            if (!dailyCalories[entry.date]) {
                dailyCalories[entry.date] = 0;
            }
            dailyCalories[entry.date] += entry.calories;
        });
        const avgCalories = Object.values(dailyCalories).reduce((sum, cal) => sum + cal, 0) / Object.keys(dailyCalories).length;
        avgCaloriesElement.textContent = `${Math.round(avgCalories)} kcal`;
    }
}

function initializeCharts() {
    console.log('Initializing charts...');
    const chartColors = ['#1FB8CD', '#FFC185', '#B4413C', '#ECEBD5', '#5D878F', '#DB4545', '#D2BA4C', '#964325', '#944454', '#13343B'];
    
    // Weight Chart
    const weightCtx = document.getElementById('weightChart');
    if (weightCtx) {
        charts.weightChart = new Chart(weightCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Weight (kg)',
                    data: [],
                    borderColor: chartColors[0],
                    backgroundColor: chartColors[0] + '20',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false
                    }
                }
            }
        });
        console.log('Weight chart initialized');
    }
    
    // Calories Chart
    const caloriesCtx = document.getElementById('caloriesChart');
    if (caloriesCtx) {
        charts.caloriesChart = new Chart(caloriesCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Calories',
                    data: [],
                    backgroundColor: chartColors[1]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
        console.log('Calories chart initialized');
    }
    
    // Macro Chart
    const macroCtx = document.getElementById('macroChart');
    if (macroCtx) {
        charts.macroChart = new Chart(macroCtx, {
            type: 'doughnut',
            data: {
                labels: ['Protein', 'Carbs', 'Fat'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: [chartColors[2], chartColors[3], chartColors[4]]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
        console.log('Macro chart initialized');
    }
    
    // Sleep Chart
    const sleepCtx = document.getElementById('sleepChart');
    if (sleepCtx) {
        charts.sleepChart = new Chart(sleepCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Sleep Duration (hours)',
                    data: [],
                    borderColor: chartColors[5],
                    backgroundColor: chartColors[5] + '20',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 12
                    }
                }
            }
        });
        console.log('Sleep chart initialized');
    }
    
    updateCharts();
}

function updateCharts() {
    console.log('Updating charts...');
    updateWeightChart();
    updateCaloriesChart();
    updateMacroChart();
    updateSleepChart();
}

function updateWeightChart() {
    if (!charts.weightChart) return;
    
    const last7Days = weightEntries.slice(0, 7).reverse();
    const labels = last7Days.map(entry => entry.date);
    const data = last7Days.map(entry => entry.weight);
    
    charts.weightChart.data.labels = labels;
    charts.weightChart.data.datasets[0].data = data;
    charts.weightChart.update();
}

function updateCaloriesChart() {
    if (!charts.caloriesChart) return;
    
    const dailyCalories = {};
    foodEntries.forEach(entry => {
        if (!dailyCalories[entry.date]) {
            dailyCalories[entry.date] = 0;
        }
        dailyCalories[entry.date] += entry.calories;
    });
    
    const last7Days = Object.entries(dailyCalories).slice(0, 7).reverse();
    const labels = last7Days.map(([date]) => date);
    const data = last7Days.map(([, calories]) => calories);
    
    charts.caloriesChart.data.labels = labels;
    charts.caloriesChart.data.datasets[0].data = data;
    charts.caloriesChart.update();
}

function updateMacroChart() {
    if (!charts.macroChart) return;
    
    const totals = foodEntries.reduce((acc, entry) => {
        acc.protein += entry.protein;
        acc.carbs += entry.carbs;
        acc.fat += entry.fat;
        return acc;
    }, { protein: 0, carbs: 0, fat: 0 });
    
    charts.macroChart.data.datasets[0].data = [totals.protein, totals.carbs, totals.fat];
    charts.macroChart.update();
}

function updateSleepChart() {
    if (!charts.sleepChart) return;
    
    const last7Days = sleepEntries.slice(0, 7).reverse();
    const labels = last7Days.map(entry => entry.date);
    const data = last7Days.map(entry => entry.duration);
    
    charts.sleepChart.data.labels = labels;
    charts.sleepChart.data.datasets[0].data = data;
    charts.sleepChart.update();
}

function showMessage(message, type) {
    const container = document.getElementById('messageContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.innerHTML = `
        <span>${type === 'success' ? '✅' : '❌'}</span>
        ${message}
    `;
    
    container.appendChild(messageDiv);
    
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

// Make functions globally available for onclick handlers
window.saveFoodEntry = saveFoodEntry;
window.saveWeightEntry = saveWeightEntry;
window.saveSleepEntry = saveSleepEntry;
window.importAppleHealth = importAppleHealth;