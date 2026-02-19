
    // ===============================
    // DFA DEFINITION
    // ===============================
    const CoffeeDFA = {
        // States Q
        Q: {
            q0: { name: 'IDLE', color: '#95A5A6' },
            q1: { name: 'SELECTING', color: '#3498DB' },
            q2: { name: 'BREWING', color: '#E74C3C' },
            q3: { name: 'READY', color: '#2ECC71' },
            q4: { name: 'CLEAN', color: '#9B59B6' }
        },
        
        // Alphabet Σ
        Sigma: {
            START: 'START',
            SELECT: 'SELECT',
            BREW: 'BREW',
            COLLECT: 'COLLECT',
            MAINTENANCE: 'MAINTENANCE'
        },
        
        // Transition function δ: Q × Σ → Q
        delta: {
            q0: { START: 'q1' },
            q1: { SELECT: 'q2' },
            q2: { BREW: 'q3', MAINTENANCE: 'q4' },
            q3: { COLLECT: 'q0', MAINTENANCE: 'q4' },
            q4: { COLLECT: 'q0' }
        },
        
        // Start state
        q0: 'q0',
        
        // Accept states F
        F: ['q3'],
        
        // State descriptions
        descriptions: {
            q0: 'Ready to start coffee selection',
            q1: 'Choose your coffee type',
            q2: 'Brewing in progress...',
            q3: 'Coffee is ready! Accepting state',
            q4: 'Maintenance mode active'
        }
    };

    // ===============================
    // GLOBAL STATE
    // ===============================
    let currentState = CoffeeDFA.q0;
    let selectedCoffee = null;
    let transitionHistory = [];
    let database = JSON.parse(localStorage.getItem('coffeeDFA_db') || '[]');
    let totalTransitions = 0;
    let coffeesMade = 0;
    
    // Coffee types
    const coffeeTypes = {
        espresso: { name: 'Espresso', color: '#2C1810' },
        latte: { name: 'Café Latte', color: '#E6D3B9' },
        cappuccino: { name: 'Cappuccino', color: '#C8AD7F' },
        mocha: { name: 'Mocha', color: '#5C3A21' }
    };

    // ===============================
    // INITIALIZATION
    // ===============================
    function init() {
        showLoading();
        setupCoffeeSelection();
        setupDFATable();
        loadFromStorage();
        
        // Calculate stats
        totalTransitions = database.length;
        coffeesMade = database.filter(entry => entry.toState === 'q3').length;
        
        // Initial log
        logToDatabase('SYSTEM', 'INIT', currentState);
        updateDisplay();
        
        // Update statistics
        updateStatistics();
        
        setTimeout(() => {
            hideLoading();
        }, 1000);
    }

    function showLoading() {
        document.getElementById('loading').style.display = 'block';
    }

    function hideLoading() {
        document.getElementById('loading').style.display = 'none';
    }

    // ===============================
    // ANIMATIONS
    // ===============================
    function animateTransition(fromState, toState, input) {
        // Animate DFA table cell
        highlightTableTransition(fromState, input);
        
        // Animate machine display
        animateMachineDisplay(input);
        
        // Special animations for specific states
        if (toState === 'q2') {
            animateBrewing();
        } else if (toState === 'q3') {
            animateReady();
        } else if (toState === 'q4') {
            animateMaintenance();
        }
    }

    function highlightTableTransition(fromState, input) {
        // Remove active class from all table cells
        document.querySelectorAll('.transition-cell').forEach(cell => {
            cell.classList.remove('active');
        });
        
        // Find and highlight the active transition cell
        const activeCell = document.querySelector(
            `.transition-cell[data-from="${fromState}"][data-input="${input}"]`
        );
        
        if (activeCell) {
            activeCell.classList.add('active');
            
            // Remove active class after animation
            setTimeout(() => {
                activeCell.classList.remove('active');
            }, 1000);
        }
    }

    function animateMachineDisplay(input) {
        const display = document.querySelector('.machine-display');
        const inputColors = {
            START: '#2ECC71',
            SELECT: '#3498DB',
            BREW: '#E74C3C',
            COLLECT: '#F39C12',
            MAINTENANCE: '#9B59B6'
        };
        
        display.style.boxShadow = `
            inset 0 0 25px rgba(212, 184, 150, 0.4),
            0 0 50px ${inputColors[input]}
        `;
        
        setTimeout(() => {
            display.style.boxShadow = `
                inset 0 0 25px rgba(212, 184, 150, 0.4),
                0 0 40px rgba(212, 184, 150, 0.3)
            `;
        }, 800);
    }

    function animateBrewing() {
        const liquid = document.getElementById('coffeeLiquid');
        const steam = document.getElementById('steamEffect');
        const coffeeColor = coffeeTypes[selectedCoffee]?.color || '#2C1810';
        
        // Set coffee color
        liquid.style.background = `linear-gradient(to top, ${coffeeColor}, ${coffeeTypes[selectedCoffee]?.color || '#6F4E37'})`;
        
        // Animate filling
        liquid.style.height = '0%';
        setTimeout(() => {
            liquid.style.height = '100%';
            liquid.style.transition = 'height 2s cubic-bezier(0.34, 1.56, 0.64, 1)';
        }, 100);
        
        // Create steam particles
        steam.innerHTML = '';
        for (let i = 0; i < 5; i++) {
            const particle = document.createElement('div');
            particle.className = 'steam-particle';
            particle.style.left = `${i * 20}px`;
            particle.style.animationDelay = `${i * 0.3}s`;
            steam.appendChild(particle);
        }
        
        steam.style.opacity = '1';
        setTimeout(() => {
            steam.style.opacity = '0';
        }, 3000);
        
        // Machine vibration
        const machine = document.querySelector('.coffee-machine');
        machine.style.animation = 'none';
        setTimeout(() => {
            machine.style.animation = 'machinePulse 0.1s 30';
            setTimeout(() => {
                machine.style.animation = '';
            }, 3000);
        }, 100);
    }

    function animateReady() {
        const liquid = document.getElementById('coffeeLiquid');
        liquid.style.height = '100%';
        
        // Pulse animation for ready state
        const readyCell = document.querySelector('.accept-state');
        readyCell.style.animation = 'checkmarkPulse 0.5s ease 3';
    }

    function animateMaintenance() {
        const machine = document.querySelector('.coffee-machine');
        const originalBackground = machine.style.background;
        
        machine.style.background = 'linear-gradient(145deg, #9B59B6, #8E44AD)';
        
        setTimeout(() => {
            machine.style.background = originalBackground;
        }, 3000);
    }

    // ===============================
    // DFA TRANSITIONS
    // ===============================
    function transition(input) {
        const fromState = currentState;
        
        // Check if transition is valid
        if (!CoffeeDFA.delta[fromState] || !CoffeeDFA.delta[fromState][input]) {
            showError(`Invalid transition: δ(${fromState}, ${input})`);
            return false;
        }
        
        // Apply transition
        const toState = CoffeeDFA.delta[fromState][input];
        
        // Update state
        currentState = toState;
        totalTransitions++;
        
        // Log transition
        logToDatabase(fromState, input, toState);
        
        // Update display and animate
        updateDisplay();
        animateTransition(fromState, toState, input);
        
        // Update button states
        updateButtonStates();
        
        // Update statistics
        updateStatistics();
        
        return true;
    }

    // ===============================
    // USER ACTIONS
    // ===============================
    function startProcess() {
        if (transition(CoffeeDFA.Sigma.START)) {
            showMessage('Select your coffee type');
            animateButton('startBtn');
        }
    }

    function selectCoffee() {
        if (!selectedCoffee) {
            showError('Please select a coffee type first!');
            return;
        }
        
        if (transition(CoffeeDFA.Sigma.SELECT)) {
            showMessage(`Selected: ${coffeeTypes[selectedCoffee].name}`);
            animateButton('selectBtn');
        }
    }

    function startBrewing() {
        if (transition(CoffeeDFA.Sigma.BREW)) {
            showMessage(`Brewing ${selectedCoffee ? coffeeTypes[selectedCoffee].name : 'coffee'}...`);
            animateButton('brewBtn');
        }
    }

    function collectCoffee() {
        if (transition(CoffeeDFA.Sigma.COLLECT)) {
            showMessage('Coffee collected. Enjoy! ☕');
            animateButton('doneBtn');
            coffeesMade++;
            selectedCoffee = null;
            resetCoffeeSelection();
        }
    }

    function maintenanceMode() {
        if (transition(CoffeeDFA.Sigma.MAINTENANCE)) {
            showMessage('Maintenance mode activated');
            animateButton('cleanBtn');
        }
    }

    function resetMachine() {
        currentState = CoffeeDFA.q0;
        selectedCoffee = null;
        
        // Reset visual elements
        document.getElementById('coffeeLiquid').style.height = '0%';
        resetCoffeeSelection();
        
        // Update buttons
        updateButtonStates();
        
        // Log reset
        logToDatabase('SYSTEM', 'RESET', currentState);
        
        showMessage('Machine reset to initial state');
        updateDisplay();
        updateStatistics();
    }

    function animateButton(btnId) {
        const btn = document.getElementById(btnId);
        btn.style.transform = 'scale(1.2)';
        btn.style.boxShadow = '0 0 30px rgba(255, 255, 255, 0.8)';
        
        setTimeout(() => {
            btn.style.transform = '';
            btn.style.boxShadow = '';
        }, 500);
    }

    // ===============================
    // UI SETUP
    // ===============================
    function setupCoffeeSelection() {
        const options = document.querySelectorAll('.coffee-option');
        options.forEach(option => {
            option.addEventListener('click', function() {
                if (currentState !== 'q1') return;
                
                // Remove previous selection
                options.forEach(opt => opt.classList.remove('selected'));
                
                // Set new selection
                this.classList.add('selected');
                selectedCoffee = this.dataset.type;
                
                // Enable select button
                document.getElementById('selectBtn').disabled = false;
                
                // Animate selection
                this.style.animation = 'selectedBounce 0.6s ease';
            });
        });
    }

    function setupDFATable() {
        const cells = document.querySelectorAll('.transition-cell');
        cells.forEach(cell => {
            cell.addEventListener('click', function() {
                const fromState = this.dataset.from;
                const input = this.dataset.input;
                
                if (this.textContent !== '—' && currentState === fromState) {
                    // Trigger the transition
                    if (input === 'START') startProcess();
                    else if (input === 'SELECT') selectCoffee();
                    else if (input === 'BREW') startBrewing();
                    else if (input === 'COLLECT') collectCoffee();
                    else if (input === 'MAINTENANCE') maintenanceMode();
                }
            });
        });
    }

    function updateDisplay() {
        // Update state display
        document.getElementById('currentState').textContent = CoffeeDFA.Q[currentState].name;
        document.getElementById('stateMessage').textContent = CoffeeDFA.descriptions[currentState];
        document.getElementById('currentStateCode').textContent = currentState;
    }

    function updateButtonStates() {
        // Enable/disable buttons based on current state
        const selectBtn = document.getElementById('selectBtn');
        const brewBtn = document.getElementById('brewBtn');
        const doneBtn = document.getElementById('doneBtn');
        const startBtn = document.getElementById('startBtn');
        
        startBtn.disabled = (currentState !== 'q0');
        selectBtn.disabled = (currentState !== 'q1');
        brewBtn.disabled = (currentState !== 'q2');
        doneBtn.disabled = (currentState !== 'q3');
    }

    function resetCoffeeSelection() {
        document.querySelectorAll('.coffee-option').forEach(opt => {
            opt.classList.remove('selected');
            opt.style.animation = '';
        });
        document.getElementById('selectBtn').disabled = true;
    }

    function updateStatistics() {
        document.getElementById('totalTransitions').textContent = totalTransitions;
        document.getElementById('coffeesMade').textContent = coffeesMade;
        document.getElementById('currentStateCode').textContent = currentState;
    }

    // ===============================
    // DATABASE LOGGING
    // ===============================
    function logToDatabase(fromState, input, toState) {
        const logEntry = {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            time: new Date().toLocaleTimeString(),
            date: new Date().toLocaleDateString(),
            fromState: fromState,
            input: input,
            toState: toState,
            fromStateName: CoffeeDFA.Q[fromState]?.name || fromState,
            toStateName: CoffeeDFA.Q[toState]?.name || toState,
            selectedCoffee: selectedCoffee,
            isAcceptState: CoffeeDFA.F.includes(toState)
        };
        
        // Add to history
        transitionHistory.unshift(logEntry);
        
        // Add to database
        database.push(logEntry);
        
        // Keep database manageable
        if (database.length > 100) {
            database = database.slice(-100);
        }
        
        // Save to localStorage
        saveToStorage();
        
        // Update history display
        updateHistoryLog();
    }

    function saveToStorage() {
        try {
            localStorage.setItem('coffeeDFA_db', JSON.stringify(database));
            localStorage.setItem('coffeeDFA_log', JSON.stringify(transitionHistory));
        } catch (e) {
            console.error('Failed to save to storage:', e);
        }
    }

    function loadFromStorage() {
        try {
            const storedDB = localStorage.getItem('coffeeDFA_db');
            const storedLog = localStorage.getItem('coffeeDFA_log');
            
            if (storedDB) database = JSON.parse(storedDB);
            if (storedLog) transitionHistory = JSON.parse(storedLog);
            
            // Keep only last 20 entries in memory
            if (transitionHistory.length > 20) {
                transitionHistory = transitionHistory.slice(0, 20);
            }
        } catch (e) {
            console.error('Failed to load from storage:', e);
        }
    }

    function updateHistoryLog() {
        const logContainer = document.getElementById('historyLog');
        logContainer.innerHTML = '';
        
        // Show latest 10 entries
        const recentLogs = transitionHistory.slice(0, 10);
        
        if (recentLogs.length === 0) {
            logContainer.innerHTML = `
                <div class="log-entry">
                    <div class="log-transition">
                        <i class="fas fa-info-circle" style="color: var(--coffee-cream);"></i>
                        <span>No transitions logged yet</span>
                    </div>
                </div>
            `;
            return;
        }
        
        recentLogs.forEach(log => {
            const coffeeInfo = log.selectedCoffee ? 
                `<span style="color: ${coffeeTypes[log.selectedCoffee]?.color || '#6F4E37'}">
                    [${coffeeTypes[log.selectedCoffee]?.name}]
                </span>` : '';
            
            const acceptMark = log.isAcceptState ? 
                '<i class="fas fa-check-circle" style="color: var(--green);"></i>' : '';
            
            const inputIcon = getInputIcon(log.input);
            
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            logEntry.innerHTML = `
                <div class="log-transition">
                    ${inputIcon}
                    <span>δ(${log.fromState}, ${log.input}) → ${log.toState}</span>
                    ${acceptMark}
                    ${coffeeInfo}
                </div>
                <div class="log-time">
                    <i class="far fa-clock"></i> ${log.time}
                </div>
            `;
            logContainer.appendChild(logEntry);
        });
    }

    function getInputIcon(input) {
        const icons = {
            START: '<i class="fas fa-play-circle" style="color: var(--green);"></i>',
            SELECT: '<i class="fas fa-check-circle" style="color: var(--blue);"></i>',
            BREW: '<i class="fas fa-fire" style="color: var(--red);"></i>',
            COLLECT: '<i class="fas fa-mug-hot" style="color: #F39C12;"></i>',
            MAINTENANCE: '<i class="fas fa-tools" style="color: var(--purple);"></i>',
            RESET: '<i class="fas fa-redo" style="color: var(--coffee-light);"></i>',
            INIT: '<i class="fas fa-power-off" style="color: var(--green);"></i>'
        };
        return icons[input] || '<i class="fas fa-arrow-right"></i>';
    }

    // ===============================
    // DATABASE FUNCTIONS
    // ===============================
    function exportToTextFile() {
        let textContent = `COFFEE MACHINE DFA TRANSITION LOG\n`;
        textContent += `==================================\n\n`;
        textContent += `Generated: ${new Date().toLocaleString()}\n`;
        textContent += `Total Transitions: ${database.length}\n`;
        textContent += `Coffees Made: ${coffeesMade}\n`;
        textContent += `Current State: ${currentState} (${CoffeeDFA.Q[currentState].name})\n\n`;
        
        textContent += `DFA SPECIFICATION:\n`;
        textContent += `------------------\n`;
        textContent += `States Q: {${Object.entries(CoffeeDFA.Q).map(([k,v]) => `${k}=${v.name}`).join(', ')}}\n`;
        textContent += `Alphabet Σ: {${Object.values(CoffeeDFA.Sigma).join(', ')}}\n`;
        textContent += `Start State: ${CoffeeDFA.q0}\n`;
        textContent += `Accept States F: {${CoffeeDFA.F.join(', ')}}\n\n`;
        
        textContent += `TRANSITION HISTORY:\n`;
        textContent += `------------------\n\n`;
        
        database.forEach((entry, index) => {
            const coffee = entry.selectedCoffee ? coffeeTypes[entry.selectedCoffee]?.name : 'None';
            textContent += `${index + 1}. ${entry.date} ${entry.time}\n`;
            textContent += `   From: ${entry.fromState} (${entry.fromStateName})\n`;
            textContent += `   Input: ${entry.input}\n`;
            textContent += `   To: ${entry.toState} (${entry.toStateName})\n`;
            textContent += `   Coffee: ${coffee}\n`;
            textContent += `   Accept State: ${entry.isAcceptState ? 'Yes ✓' : 'No'}\n`;
            textContent += `   ----------------------------\n`;
        });
        
        // Create and download
        const blob = new Blob([textContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `coffee-dfa-log-${new Date().toISOString().slice(0,10)}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showMessage('Log exported as text file');
    }

    function exportToJSON() {
        const exportData = {
            metadata: {
                exportDate: new Date().toISOString(),
                project: "Coffee Machine DFA Simulator",
                description: "Automata Theory Implementation"
            },
            dfa: CoffeeDFA,
            currentState: {
                code: currentState,
                name: CoffeeDFA.Q[currentState].name
            },
            statistics: {
                totalTransitions: totalTransitions,
                coffeesMade: coffeesMade,
                databaseSize: database.length
            },
            recentTransitions: transitionHistory.slice(0, 10)
        };
        
        const jsonContent = JSON.stringify(exportData, null, 2);
        const blob = new Blob([jsonContent], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `coffee-dfa-${new Date().toISOString().slice(0,10)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showMessage('Database exported as JSON');
    }

    function viewDatabase() {
        const stats = `
            📊 DATABASE STATISTICS
            =====================
            Total Entries: ${database.length}
            Current State: ${currentState} (${CoffeeDFA.Q[currentState].name})
            Coffees Made: ${coffeesMade}
            Total Transitions: ${totalTransitions}
            
            💾 Storage: ${(JSON.stringify(database).length / 1024).toFixed(2)} KB
        `;
        
        alert(stats);
    }

    function clearDatabase() {
        if (confirm('Clear all database entries? This will delete all logged transitions.')) {
            database = [];
            transitionHistory = [];
            totalTransitions = 0;
            coffeesMade = 0;
            localStorage.removeItem('coffeeDFA_db');
            localStorage.removeItem('coffeeDFA_log');
            updateHistoryLog();
            updateStatistics();
            showMessage('Database cleared successfully');
        }
    }

    function runAutoDemo() {
        if (confirm('Run automated demonstration of the DFA?')) {
            resetMachine();
            
            const steps = [
                { action: startProcess, delay: 1000 },
                { action: () => {
                    selectedCoffee = 'latte';
                    document.querySelector('.coffee-option[data-type="latte"]').classList.add('selected');
                    document.getElementById('selectBtn').disabled = false;
                }, delay: 1500 },
                { action: selectCoffee, delay: 2000 },
                { action: startBrewing, delay: 2500 },
                { action: collectCoffee, delay: 5000 }
            ];
            
            let stepIndex = 0;
            function executeStep() {
                if (stepIndex < steps.length) {
                    setTimeout(() => {
                        steps[stepIndex].action();
                        stepIndex++;
                        executeStep();
                    }, steps[stepIndex].delay);
                }
            }
            
            executeStep();
        }
    }

    function showDFADetails() {
        const details = `
            🎯 DFA FORMAL DEFINITION
            =======================
            
            M = (Q, Σ, δ, q₀, F)
            
            Q = {${Object.entries(CoffeeDFA.Q).map(([k,v]) => `${k} (${v.name})`).join(', ')}}
            
            Σ = {${Object.values(CoffeeDFA.Sigma).join(', ')}}
            
            q₀ = ${CoffeeDFA.q0} (${CoffeeDFA.Q[CoffeeDFA.q0].name})
            
            F = {${CoffeeDFA.F.map(f => `${f} (${CoffeeDFA.Q[f].name})`).join(', ')}}
            
            δ: Q × Σ → Q
            ${Object.entries(CoffeeDFA.delta).map(([from, trans]) => 
                Object.entries(trans).map(([input, to]) => 
                    `δ(${from}, ${input}) = ${to}`
                ).join('\n')
            ).join('\n')}
            
            💡 This DFA models a coffee machine:
            q₀ → q₁: Start the machine
            q₁ → q₂: Select coffee type
            q₂ → q₃: Brew coffee
            q₃ → q₀: Collect coffee
            Any state → q₄: Maintenance mode
        `;
        
        alert(details);
    }

    // ===============================
    // HELPER FUNCTIONS
    // ===============================
    function showMessage(message) {
        document.getElementById('stateMessage').textContent = message;
    }

    function showError(error) {
        const messageEl = document.getElementById('stateMessage');
        const original = messageEl.textContent;
        const originalColor = messageEl.style.color;
        
        messageEl.textContent = `⚠️ ${error}`;
        messageEl.style.color = '#E74C3C';
        
        setTimeout(() => {
            messageEl.textContent = original;
            messageEl.style.color = originalColor;
        }, 3000);
    }

    // ===============================
    // INITIALIZE
    // ===============================
    window.onload = init;
