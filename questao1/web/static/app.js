// Global State
let currentSessionId = null;
let kbInfo = null;
let activeTab = "tab-consultation";
let activeExplanationTab = "natural";
let currentQuestionAttr = null;

// Selectors
const selectKb = document.getElementById("kb-select");
const btnLoadKb = document.getElementById("btn-load-kb");
const inputKbUpload = document.getElementById("kb-upload-input");
const btnDownloadKb = document.getElementById("btn-download-kb");
const btnNewKb = document.getElementById("btn-new-kb");

const metaDomain = document.getElementById("meta-domain");
const metaDesc = document.getElementById("meta-desc");
const hypothesesList = document.getElementById("hypotheses-list");
const rulesCount = document.getElementById("rules-count");
const rulesListContainer = document.getElementById("rules-list-container");
const inputNewHypothesis = document.getElementById("input-new-hypothesis");
const btnAddHypothesis = document.getElementById("btn-add-hypothesis");

const tabBtns = document.querySelectorAll(".tab-btn");
const tabPanes = document.querySelectorAll(".tab-pane");

// Consultation Elements
const selectInferenceMode = document.getElementById("inference-mode");
const selectTargetGoal = document.getElementById("target-goal");
const targetGoalWrapper = document.getElementById("target-goal-wrapper");
const btnStartSession = document.getElementById("btn-start-session");
const initialFactsSetup = document.getElementById("initial-facts-setup");
const initialFactsFields = document.getElementById("initial-facts-fields");

const consultationSetup = document.querySelector(".consultation-setup");
const consultationActive = document.querySelector(".consultation-active");
const consultationResults = document.querySelector(".consultation-results");

const questionText = document.getElementById("question-text");
const inputContainer = document.getElementById("input-container");
const validationError = document.getElementById("validation-error");
const btnSubmitAnswer = document.getElementById("btn-submit-answer");
const btnWhy = document.getElementById("btn-why");
const btnResetSession = document.getElementById("btn-reset-session");

const factsTableBody = document.getElementById("facts-table-body");
const noFactsMsg = document.getElementById("no-facts-msg");

const explanationBox = document.getElementById("explanation-box");
const btnCloseExplanation = document.getElementById("btn-close-explanation");
const expTabBtns = document.querySelectorAll(".exp-tab-btn");
const expPanes = document.querySelectorAll(".exp-pane");
const expNatural = document.getElementById("explanation-natural");
const expStructured = document.getElementById("explanation-structured");

const resultsContainer = document.getElementById("results-container");
const howExplanationContent = document.getElementById("how-explanation-content");
const btnRestartFromResults = document.getElementById("btn-restart-from-results");

// Rule Manager Elements
const formRule = document.getElementById("form-rule");
const btnAddCondition = document.getElementById("btn-add-condition");
const ruleConditionsList = document.getElementById("rule-conditions-list");

// Question Manager Elements
const formQuestion = document.getElementById("form-question");

// IA Assistant Elements
const selectIaTargetMode = document.getElementById("ia-target-mode");
const textIaInput = document.getElementById("ia-input-text");
const btnIaGenerate = document.getElementById("btn-ia-generate");
const iaPreviewBox = document.getElementById("ia-preview-box");
const preIaPreviewContent = document.getElementById("ia-preview-content");
const btnIaConfirm = document.getElementById("btn-ia-confirm");
const btnIaDiscard = document.getElementById("btn-ia-discard");
let iaParsedData = null;

// TOAST Notification helper
function showToast(message, type = "success") {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.style.display = "block";
    toast.style.borderLeftColor = type === "success" ? "var(--success)" : "var(--danger)";
    setTimeout(() => {
        toast.style.display = "none";
    }, 4000);
}

// APP INITIALIZATION
document.addEventListener("DOMContentLoaded", () => {
    loadKbList();
    loadActiveKbInfo();
    setupEventListeners();
});

// EVENT LISTENERS SETUP
function setupEventListeners() {
    // Tabs Navigation
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            tabPanes.forEach(p => p.classList.remove("active"));
            
            btn.classList.add("active");
            activeTab = btn.getAttribute("data-tab");
            document.getElementById(activeTab).classList.add("active");
        });
    });

    // Add Hypothesis
    btnAddHypothesis.addEventListener("click", () => {
        const attr = inputNewHypothesis.value.trim();
        if (!attr) return;
        fetch(`/api/kb/edit/hypothesis?attribute=${encodeURIComponent(attr)}`, { method: "POST" })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showToast(`Hipótese '${attr}' registrada.`);
                    inputNewHypothesis.value = "";
                    loadActiveKbInfo();
                } else {
                    showToast("Erro ao registrar hipótese.", "error");
                }
            });
    });

    // KB Selection & Loading
    btnLoadKb.addEventListener("click", () => {
        const filename = selectKb.value;
        if (!filename) return;
        fetch(`/api/kb/load?filename=${encodeURIComponent(filename)}`, { method: "POST" })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showToast(`Base de conhecimento '${data.domain}' carregada.`);
                    loadActiveKbInfo();
                } else {
                    showToast(data.detail || "Erro ao carregar base.", "error");
                }
            });
    });

    // KB Upload
    inputKbUpload.addEventListener("change", () => {
        const file = inputKbUpload.files[0];
        if (!file) return;
        const formData = new FormData();
        formData.append("file", file);
        
        fetch("/api/kb/upload", {
            method: "POST",
            body: formData
        })
        .then(res => {
            if (!res.ok) throw new Error("Falha no upload");
            return res.json();
        })
        .then(data => {
            if (data.success) {
                showToast(`Base de conhecimento '${data.domain}' importada e carregada.`);
                loadKbList(data.filename);
                loadActiveKbInfo();
            }
        })
        .catch(err => showToast("Erro ao importar base de conhecimento (certifique-se de que é um JSON válido).", "error"));
    });



    // Download/Save current KB JSON
    btnDownloadKb.addEventListener("click", () => {
        fetch("/api/kb/export")
            .then(res => res.json())
            .then(data => {
                // Determine clean filename
                let suggestedFilename = "base_conhecimento.json";
                if (kbInfo) {
                    if (kbInfo.filename && kbInfo.filename !== "generico") {
                        suggestedFilename = kbInfo.filename;
                        if (!suggestedFilename.endsWith(".json")) {
                            suggestedFilename += ".json";
                        }
                    } else if (kbInfo.domain) {
                        suggestedFilename = kbInfo.domain + ".json";
                    }
                }
                
                // Try modern Save File Picker first (allows user to select folder and name)
                if (window.showSaveFilePicker) {
                    const options = {
                        suggestedName: suggestedFilename,
                        types: [{
                            description: 'JSON Knowledge Base',
                            accept: { 'application/json': ['.json'] }
                        }],
                    };
                    window.showSaveFilePicker(options)
                        .then(handle => handle.createWritable())
                        .then(writable => {
                            return writable.write(JSON.stringify(data, null, 4))
                                .then(() => writable.close());
                        })
                        .then(() => {
                            showToast("Base de conhecimento salva com sucesso!");
                        })
                        .catch(err => {
                            if (err.name !== 'AbortError') {
                                console.error(err);
                                showToast("Erro ao salvar arquivo.", "error");
                            }
                        });
                } else {
                    // Fallback standard download
                    const blob = new Blob([JSON.stringify(data, null, 4)], { type: "application/json" });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = suggestedFilename;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                    showToast("Base de conhecimento baixada com sucesso!");
                }
            })
            .catch(err => {
                console.error(err);
                showToast("Erro ao exportar base de conhecimento.", "error");
            });
    });

    // Selectors for Modal New KB
    const modalNewKb = document.getElementById("modal-new-kb");
    const btnCloseNewKbModal = document.getElementById("btn-close-new-kb-modal");
    const btnCancelNewKb = document.getElementById("btn-cancel-new-kb");
    const btnConfirmNewKb = document.getElementById("btn-confirm-new-kb");
    const inputNewKbDomain = document.getElementById("new-kb-domain");
    const inputNewKbDesc = document.getElementById("new-kb-desc");

    // Open Modal
    btnNewKb.addEventListener("click", () => {
        inputNewKbDomain.value = "";
        inputNewKbDesc.value = "";
        modalNewKb.style.display = "flex";
    });

    // Close Modal helpers
    const closeModal = () => {
        modalNewKb.style.display = "none";
    };
    btnCloseNewKbModal.addEventListener("click", closeModal);
    btnCancelNewKb.addEventListener("click", closeModal);
    
    // Close on click outside card
    modalNewKb.addEventListener("click", (e) => {
        if (e.target === modalNewKb) {
            closeModal();
        }
    });

    // Confirm Create Base
    btnConfirmNewKb.addEventListener("click", () => {
        const domain = inputNewKbDomain.value.trim();
        const description = inputNewKbDesc.value.trim();
        
        if (!domain) {
            showToast("O nome do domínio é obrigatório.", "error");
            return;
        }
        
        // Remove spaces or special characters to keep it filename safe
        const cleanDomain = domain.toLowerCase().replace(/[^a-z0-9_]/g, "");
        if (cleanDomain !== domain) {
            showToast("O domínio deve conter apenas letras minúsculas, números e sublinhados.", "error");
            return;
        }
        
        fetch(`/api/kb/new?domain=${encodeURIComponent(cleanDomain)}&description=${encodeURIComponent(description)}`, { method: "POST" })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showToast(`Nova base de conhecimento '${cleanDomain}' criada!`);
                    closeModal();
                    loadKbList(cleanDomain + ".json");
                    loadActiveKbInfo();
                } else {
                    showToast("Erro ao criar nova base.", "error");
                }
            })
            .catch(() => {
                showToast("Erro de comunicação com o servidor ao criar nova base.", "error");
            });
    });

    // Toggle backward target option
    selectInferenceMode.addEventListener("change", () => {
        if (selectInferenceMode.value === "backward") {
            targetGoalWrapper.style.display = "flex";
        } else {
            targetGoalWrapper.style.display = "none";
        }
    });

    // Start Session
    btnStartSession.addEventListener("click", () => {
        const mode = selectInferenceMode.value;
        const target = mode === "backward" ? selectTargetGoal.value : null;
        
        const initialFacts = {};
        const initialCfs = {};
        document.querySelectorAll(".initial-fact-input").forEach(el => {
            const attr = el.getAttribute("data-attribute");
            const val = el.value.trim();
            if (val !== "") {
                initialFacts[attr] = val;
                
                // Get corresponding CF selector
                const cfEl = document.querySelector(`.initial-fact-cf[data-cf-attribute="${attr}"]`);
                if (cfEl) {
                    initialCfs[attr] = parseFloat(cfEl.value) || 1.0;
                }
            }
        });
        
        fetch("/api/session/start", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mode, target, initial_facts: initialFacts, initial_cfs: initialCfs })
        })
        .then(res => res.json())
        .then(data => {
            currentSessionId = data.session_id;
            consultationSetup.style.display = "none";
            consultationResults.style.display = "none";
            consultationActive.style.display = "block";
            explanationBox.style.display = "none";
            refreshSessionStatus();
        });
    });

    // Reset/Cancel Consultation
    btnResetSession.addEventListener("click", () => {
        currentSessionId = null;
        consultationActive.style.display = "none";
        consultationSetup.style.display = "block";
        explanationBox.style.display = "none";
    });

    // Submit Answer
    btnSubmitAnswer.addEventListener("click", submitAnswer);

    // Why this question?
    btnWhy.addEventListener("click", () => {
        if (!currentSessionId || !currentQuestionAttr) return;
        
        explanationBox.style.display = "block";
        expNatural.innerHTML = "<p>Consultando a inteligência artificial...</p>";
        expStructured.innerHTML = "Consultando motor especialista...";
        
        fetch(`/api/session/why?session_id=${currentSessionId}&attribute=${currentQuestionAttr}`)
            .then(res => res.json())
            .then(data => {
                expStructured.textContent = data.structured;
                expNatural.innerHTML = data.natural ? `<p>${data.natural.replace(/\n/g, "<br>")}</p>` : "<p>Explicação da IA indisponível. Veja a lógica estruturada.</p>";
            });
    });

    // Close explanation box
    btnCloseExplanation.addEventListener("click", () => {
        explanationBox.style.display = "none";
    });

    // Explanation tabs
    expTabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            expTabBtns.forEach(b => b.classList.remove("active"));
            expPanes.forEach(p => p.classList.remove("active"));
            
            btn.classList.add("active");
            activeExplanationTab = btn.getAttribute("data-exp-type");
            document.getElementById(`explanation-${activeExplanationTab}`).classList.add("active");
        });
    });

    // Restart consultation from results screen
    btnRestartFromResults.addEventListener("click", () => {
        consultationResults.style.display = "none";
        consultationSetup.style.display = "block";
    });

    // Add Condition Row in Rule Manager
    btnAddCondition.addEventListener("click", () => {
        addConditionRow();
    });

    // Save Rule Form submit
    formRule.addEventListener("submit", (e) => {
        e.preventDefault();
        saveRuleFromForm();
    });

    // Save Question Form submit
    formQuestion.addEventListener("submit", (e) => {
        e.preventDefault();
        saveQuestionFromForm();
    });

    // IA Assistant Generate
    btnIaGenerate.addEventListener("click", () => {
        const text = textIaInput.value.trim();
        const type = selectIaTargetMode.value;
        if (!text) return;
        
        btnIaGenerate.disabled = true;
        btnIaGenerate.textContent = "Processando com IA...";
        iaPreviewBox.style.display = "none";
        
        fetch("/api/ia/parse", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, type })
        })
        .then(res => {
            if (!res.ok) return res.json().then(d => { throw new Error(d.detail || "Erro na IA") });
            return res.json();
        })
        .then(data => {
            iaParsedData = data.data;
            preIaPreviewContent.textContent = JSON.stringify(iaParsedData, null, 2);
            iaPreviewBox.style.display = "block";
        })
        .catch(err => {
            showToast(err.message, "error");
        })
        .finally(() => {
            btnIaGenerate.disabled = false;
            btnIaGenerate.textContent = "Processar com IA";
        });
    });

    // IA Assistant Confirm
    btnIaConfirm.addEventListener("click", () => {
        if (!iaParsedData) return;
        const type = selectIaTargetMode.value;
        
        const promises = [];
        if (type === "rules") {
            iaParsedData.forEach(r => {
                promises.push(
                    fetch("/api/kb/edit/rule", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(r)
                    })
                );
            });
        } else {
            iaParsedData.forEach(q => {
                promises.push(
                    fetch("/api/kb/edit/question", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            attribute: q.attribute,
                            question: q.question,
                            options: q.options,
                            range: q.range
                        })
                    })
                );
            });
        }

        Promise.all(promises)
            .then(() => {
                showToast(`Metadados de ${type === "rules" ? "regras" : "perguntas"} cadastrados com sucesso via IA!`);
                iaPreviewBox.style.display = "none";
                textIaInput.value = "";
                iaParsedData = null;
                loadActiveKbInfo();
            })
            .catch(() => showToast("Ocorreu um erro ao salvar os metadados gerados pela IA.", "error"));
    });

    // IA Assistant Discard
    btnIaDiscard.addEventListener("click", () => {
        iaPreviewBox.style.display = "none";
        iaParsedData = null;
    });
}

// LOAD LIST OF KNOWLEDGE BASES
function loadKbList(selectedFilename = null) {
    fetch("/api/kb/list")
        .then(res => res.json())
        .then(data => {
            selectKb.innerHTML = "";
            data.kbs.forEach(file => {
                const opt = document.createElement("option");
                opt.value = file;
                opt.textContent = file;
                if (selectedFilename && file === selectedFilename) {
                    opt.selected = true;
                }
                selectKb.appendChild(opt);
            });
        });
}

// LOAD ACTIVE KB METADATA
function loadActiveKbInfo() {
    fetch("/api/kb/info")
        .then(res => res.json())
        .then(data => {
            kbInfo = data;
            
            // Update sidebar header info
            metaDomain.textContent = data.domain;
            metaDesc.textContent = data.description || "Sem descrição";
            rulesCount.textContent = data.rules_count;
            
            // Render Hypotheses list
            hypothesesList.innerHTML = "";
            if (data.hypotheses && data.hypotheses.length > 0) {
                data.hypotheses.forEach(hyp => {
                    const li = document.createElement("li");
                    li.style.display = "flex";
                    li.style.alignItems = "center";
                    li.style.gap = "6px";
                    li.innerHTML = `
                        <span>${hyp}</span>
                        <span style="cursor:pointer; font-weight:bold; color:var(--danger); margin-left: 2px;" onclick="deleteHypothesis('${hyp}')">&times;</span>
                    `;
                    hypothesesList.appendChild(li);
                });
                
                // Populate backward goal selection
                selectTargetGoal.innerHTML = "";
                data.hypotheses.forEach(hyp => {
                    const opt = document.createElement("option");
                    opt.value = hyp;
                    opt.textContent = hyp;
                    selectTargetGoal.appendChild(opt);
                });
            } else {
                const li = document.createElement("li");
                li.textContent = "Nenhuma hipótese cadastrada";
                hypothesesList.appendChild(li);
            }

            // Render Rules list accordion
            rulesListContainer.innerHTML = "";
            if (data.rules && data.rules.length > 0) {
                data.rules.forEach(r => {
                    const ruleDiv = document.createElement("div");
                    ruleDiv.className = "rule-accordion";
                    
                    const opWord = r.condition_operator === "OR" ? "\nOU\n" : "\nE\n";
                    const conditionsStr = r.conditions.map(c => `  ${c.attribute} ${c.operator} ${c.value}`).join(opWord);
                    const conclusionStr = `  ${r.conclusion.attribute} = ${r.conclusion.value}`;
                    
                    ruleDiv.innerHTML = `
                        <div class="rule-acc-header" onclick="this.nextElementSibling.classList.toggle('active')">
                            <span class="rule-acc-title">[${r.id}] ${r.name}</span>
                            <div style="display:flex; gap: 12px; align-items:center;">
                                <span class="rule-acc-priority" style="margin-right: 4px;">Prio: ${r.priority}</span>
                                <button class="btn btn-secondary btn-small" style="padding: 4px 6px;" onclick="event.stopPropagation(); loadRuleToForm('${r.id}')" title="Editar Regra">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display: block;"><path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path></svg>
                                </button>
                                <button class="btn btn-danger-outline btn-small" onclick="event.stopPropagation(); deleteRule('${r.id}')">Excluir</button>
                            </div>
                        </div>
                        <div class="rule-acc-content">
                            ${r.description ? `<div class="rule-desc-text">${r.description}</div>` : ""}
                            <div class="rule-logic-block">
                                <div>SE</div>
                                <div style="white-space: pre-wrap;">${conditionsStr}</div>
                                <div>ENTÃO</div>
                                <div>${conclusionStr}</div>
                            </div>
                        </div>
                    `;
                    rulesListContainer.appendChild(ruleDiv);
                });
            } else {
                rulesListContainer.innerHTML = "<p style='color: var(--text-muted); font-size:12px;'>Nenhuma regra cadastrada na base de conhecimento.</p>";
            }
            // Render Questions list
            const questionsContainer = document.getElementById("questions-list-container");
            if (questionsContainer) {
                questionsContainer.innerHTML = "";
                if (data.questions && Object.keys(data.questions).length > 0) {
                    Object.entries(data.questions).forEach(([attr, text]) => {
                        const qDiv = document.createElement("div");
                        qDiv.className = "form-list-item";
                        qDiv.style.display = "flex";
                        qDiv.style.justifyContent = "space-between";
                        qDiv.style.alignItems = "center";
                        qDiv.style.padding = "8px 10px";
                        qDiv.style.background = "var(--bg-dark)";
                        qDiv.style.borderRadius = "var(--radius-sm)";
                        qDiv.style.border = "1px solid var(--border-color)";
                        qDiv.style.marginBottom = "8px";
                        
                        const opts = data.answer_options[attr];
                        const limits = data.attribute_ranges[attr];
                        
                        qDiv.innerHTML = `
                            <div style="display: flex; flex-direction: column; gap: 2px; flex: 1; min-width: 0; padding-right: 10px;">
                                <div style="display: flex; gap: 6px; align-items: center; flex-wrap: wrap;">
                                    <span style="font-size: 11px; font-weight: 700; color: var(--accent); font-family: monospace;">${attr}</span>
                                    ${limits ? `<span style="font-size: 9px; color: var(--text-muted); background: var(--bg-card); padding: 1px 4px; border-radius: 2px;">Limites: [${limits[0] !== null ? limits[0] : '-'}, ${limits[1] !== null ? limits[1] : '-'}]</span>` : ""}
                                </div>
                                <span style="font-size: 12px; color: var(--text-main); font-weight: 500; word-break: break-word;">${text}</span>
                                ${opts && opts.length > 0 ? `<div style="font-size: 10px; color: var(--text-muted); text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">Opções: <span style="color: var(--accent);">${opts.join(", ")}</span></div>` : ""}
                            </div>
                            <button type="button" class="btn btn-danger-outline btn-small" onclick="deleteQuestion('${attr}')">Excluir</button>
                        `;
                        questionsContainer.appendChild(qDiv);
                    });
                } else {
                    questionsContainer.innerHTML = "<p style='color: var(--text-muted); font-size:12px;'>Nenhuma pergunta cadastrada nesta base.</p>";
                }
            }
            
            populateInitialFactsForm();
        });
}

// DELETE RULE
function deleteRule(ruleId) {
    if (!confirm(`Deseja realmente excluir a regra ${ruleId}?`)) return;
    fetch(`/api/kb/delete/rule?rule_id=${encodeURIComponent(ruleId)}`, { method: "POST" })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast(`Regra '${ruleId}' excluída.`);
                loadActiveKbInfo();
            } else {
                showToast("Erro ao excluir regra.", "error");
            }
        });
}

// REFRESH SESSION STATUS
function refreshSessionStatus() {
    if (!currentSessionId) return;
    
    fetch(`/api/session/status?session_id=${currentSessionId}`)
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                showToast(`Erro na inferência: ${data.error}`, "error");
                btnResetSession.click();
                return;
            }
            
            // Update Facts Table
            refreshFactsList();
            
            if (data.is_done) {
                // Show results
                displayResults(data.results);
            } else {
                // Show next question
                currentQuestionAttr = data.attribute;
                questionText.textContent = data.question || `Qual o valor de '${data.attribute}'?`;
                renderQuestionInputs(data.attribute, data.options);
                validationError.style.display = "none";
            }
        });
}

// RENDER QUESTION INPUTS
function renderQuestionInputs(attribute, options) {
    inputContainer.innerHTML = "";
    
    if (options && options.length > 0) {
        // Option buttons
        const grid = document.createElement("div");
        grid.className = "options-grid";
        
        options.forEach(opt => {
            const btn = document.createElement("div");
            btn.className = "btn-option";
            btn.textContent = opt;
            btn.setAttribute("data-value", opt);
            btn.addEventListener("click", () => {
                document.querySelectorAll(".btn-option").forEach(b => b.classList.remove("selected"));
                btn.classList.add("selected");
            });
            grid.appendChild(btn);
        });
        inputContainer.appendChild(grid);
    } else {
        // Free text input
        const wrapper = document.createElement("div");
        wrapper.className = "free-input-wrapper";
        
        const input = document.createElement("input");
        input.type = "text";
        input.id = "free-answer-input";
        input.placeholder = "Digite sua resposta...";
        
        // Handle enter key submit
        input.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                submitAnswer();
            }
        });
        
        wrapper.appendChild(input);
        
        // Show range tip if registered in KB
        if (kbInfo && kbInfo.attribute_ranges && kbInfo.attribute_ranges[attribute]) {
            const range = kbInfo.attribute_ranges[attribute];
            if (range && (range[0] !== null || range[1] !== null)) {
                const tip = document.createElement("span");
                tip.className = "input-range-tip";
                
                if (range[0] !== null && range[1] !== null) {
                    tip.textContent = `Limites válidos: entre ${range[0]} e ${range[1]}`;
                } else if (range[0] !== null) {
                    tip.textContent = `Limites válidos: maior ou igual a ${range[0]}`;
                } else if (range[1] !== null) {
                    tip.textContent = `Limites válidos: menor ou igual a ${range[1]}`;
                }
                wrapper.appendChild(tip);
            }
        }
        
        inputContainer.appendChild(wrapper);
        // Focus input
        setTimeout(() => input.focus(), 50);
    }

    // Append CF slider for answer confidence
    const cfWrapper = document.createElement("div");
    cfWrapper.className = "answer-cf-wrapper";
    cfWrapper.style.marginTop = "15px";
    cfWrapper.style.paddingTop = "15px";
    cfWrapper.style.borderTop = "1px solid var(--border-color)";
    
    cfWrapper.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; font-size: 13px; color: var(--text-muted);">
            <span>Grau de certeza desta resposta:</span>
            <span id="answer-cf-val" style="font-weight: 600; color: var(--accent);">100%</span>
        </div>
        <input type="range" id="answer-cf-range" min="0" max="100" value="100" style="width: 100%; cursor: pointer;" oninput="document.getElementById('answer-cf-val').textContent = this.value + '%'">
    `;
    inputContainer.appendChild(cfWrapper);
}

// SUBMIT ANSWER
function submitAnswer() {
    if (!currentSessionId || !currentQuestionAttr) return;
    
    let answer = "";
    const selectedBtn = document.querySelector(".btn-option.selected");
    if (selectedBtn) {
        answer = selectedBtn.getAttribute("data-value");
    } else {
        const textInput = document.getElementById("free-answer-input");
        if (textInput) {
            answer = textInput.value.trim();
        }
    }
    
    if (!answer) {
        validationError.textContent = "Por favor, selecione uma opção ou digite uma resposta.";
        validationError.style.display = "block";
        return;
    }
    
    const cfValEl = document.getElementById("answer-cf-range");
    const cf = cfValEl ? parseFloat(cfValEl.value) / 100.0 : 1.0;
    
    btnSubmitAnswer.disabled = true;
    
    fetch(`/api/session/answer?session_id=${currentSessionId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answer, cf })
    })
    .then(res => res.json())
    .then(data => {
        btnSubmitAnswer.disabled = false;
        if (data.success) {
            validationError.style.display = "none";
            explanationBox.style.display = "none";
            refreshSessionStatus();
        } else {
            validationError.textContent = `Aviso: ${data.error}`;
            validationError.style.display = "block";
        }
    })
    .catch(() => {
        btnSubmitAnswer.disabled = false;
    });
}

// REFRESH FACTS LIST
function refreshFactsList() {
    if (!currentSessionId) return;
    
    fetch(`/api/session/facts?session_id=${currentSessionId}`)
        .then(res => res.json())
        .then(data => {
            factsTableBody.innerHTML = "";
            if (data.facts && data.facts.length > 0) {
                noFactsMsg.style.display = "none";
                data.facts.forEach(f => {
                    const tr = document.createElement("tr");
                    
                    let badgeClass = "source-initial";
                    if (f.source === "user") badgeClass = "source-user";
                    if (f.source === "inferred") badgeClass = "source-inferred";
                    
                    tr.innerHTML = `
                        <td style="font-weight: 500;">${f.attribute}</td>
                        <td>${f.value} <span style="color: var(--accent); font-size:11px;">(CF: ${f.cf !== undefined ? f.cf.toFixed(2) : '1.00'})</span></td>
                        <td><span class="fact-source-badge ${badgeClass}">${f.source}</span></td>
                    `;
                    factsTableBody.appendChild(tr);
                });
            } else {
                noFactsMsg.style.display = "block";
            }
        });
}

// DISPLAY RESULTS
function displayResults(results) {
    consultationActive.style.display = "none";
    consultationResults.style.display = "block";
    explanationBox.style.display = "none";
    
    resultsContainer.innerHTML = "";
    howExplanationContent.innerHTML = "<p style='color: var(--text-muted); font-style: italic;'>Selecione um card de conclusão acima para ver as regras associadas.</p>";
    
    let hasResults = false;
    for (const [hyp, vals] of Object.entries(results)) {
        if (vals && vals.length > 0) {
            hasResults = true;
            vals.forEach(val => {
                const card = document.createElement("div");
                card.className = "result-card";
                card.innerHTML = `
                    <div class="result-header">
                        <span class="result-attr-name">${hyp.replace(/_/g, " ")}</span>
                    </div>
                    <div class="result-value-badge">${val}</div>
                `;
                
                card.addEventListener("click", () => {
                    document.querySelectorAll(".result-card").forEach(c => c.classList.remove("active"));
                    card.classList.add("active");
                    showHowExplanation(hyp, val);
                });
                
                resultsContainer.appendChild(card);
            });
        }
    }
    
    if (!hasResults) {
        resultsContainer.innerHTML = `
            <div class="card" style="grid-column: 1 / -1; text-align: center; padding: 40px;">
                <p style="color: var(--text-muted);">Não foi possível chegar a nenhum diagnóstico/hipótese com as respostas fornecidas.</p>
            </div>
        `;
    }
}

// SHOW HOW EXPLANATION
function showHowExplanation(attribute, value) {
    howExplanationContent.innerHTML = "<p>Consultando explicações lógica e IA...</p>";
    
    fetch(`/api/session/how?session_id=${currentSessionId}&attribute=${attribute}&value=${encodeURIComponent(value)}`)
        .then(res => res.json())
        .then(data => {
            howExplanationContent.innerHTML = `
                <div class="explanation-tabs" style="margin-bottom: 12px; display: flex; gap: 8px; border-bottom: 1px solid var(--border-color); padding-bottom: 8px;">
                    <button class="exp-tab-btn active" id="btn-how-tab-natural" style="background: none; border: none; color: var(--text-main); font-weight: 600; font-size: 13px; cursor: pointer; padding: 4px 8px; border-bottom: 2px solid var(--accent); outline: none;">Linguagem Natural (IA)</button>
                    <button class="exp-tab-btn" id="btn-how-tab-structured" style="background: none; border: none; color: var(--text-muted); font-weight: 500; font-size: 13px; cursor: pointer; padding: 4px 8px; outline: none;">Lógica Estruturada (Sistema)</button>
                </div>
                <div id="how-pane-natural" class="how-pane" style="font-size: 13px; line-height: 1.5; color: var(--text-muted); display: block;">
                    ${data.natural ? data.natural.replace(/\n/g, "<br>") : "Explicação por IA indisponível ou não gerada."}
                </div>
                <div id="how-pane-structured" class="how-pane structured-code" style="display: none; border-left: 2px solid var(--accent); padding-left: 10px;">
                    ${data.structured}
                </div>
            `;
            
            const tabNatural = document.getElementById("btn-how-tab-natural");
            const tabStructured = document.getElementById("btn-how-tab-structured");
            const paneNatural = document.getElementById("how-pane-natural");
            const paneStructured = document.getElementById("how-pane-structured");
            
            tabNatural.addEventListener("click", () => {
                tabNatural.classList.add("active");
                tabNatural.style.color = "var(--text-main)";
                tabNatural.style.fontWeight = "600";
                tabNatural.style.borderBottom = "2px solid var(--accent)";
                
                tabStructured.classList.remove("active");
                tabStructured.style.color = "var(--text-muted)";
                tabStructured.style.fontWeight = "500";
                tabStructured.style.borderBottom = "none";
                
                paneNatural.style.display = "block";
                paneStructured.style.display = "none";
            });
            
            tabStructured.addEventListener("click", () => {
                tabStructured.classList.add("active");
                tabStructured.style.color = "var(--text-main)";
                tabStructured.style.fontWeight = "600";
                tabStructured.style.borderBottom = "2px solid var(--accent)";
                
                tabNatural.classList.remove("active");
                tabNatural.style.color = "var(--text-muted)";
                tabNatural.style.fontWeight = "500";
                tabNatural.style.borderBottom = "none";
                
                paneNatural.style.display = "none";
                paneStructured.style.display = "block";
            });
        });
}

function updateLogicalConnectiveDisplays() {
    const rows = ruleConditionsList.querySelectorAll(".form-list-item");
    const currentOp = document.getElementById("rule-operator") ? document.getElementById("rule-operator").value : "AND";
    
    rows.forEach((row, index) => {
        const container = row.querySelector(".logical-op-container");
        if (!container) return;
        
        if (index === 0) {
            container.innerHTML = `
                <select class="cond-logical-op-first" disabled style="max-width: 70px; padding: 6px; border-radius: 4px; background: var(--bg-card); color: var(--text-muted); border: 1px solid var(--border-color); font-weight: 600; opacity: 0.8; width: 100%;">
                    <option>SE</option>
                </select>
            `;
        } else {
            container.innerHTML = `
                <select class="cond-logical-op" style="max-width: 70px; padding: 6px; border-radius: 4px; background: var(--bg-input); color: var(--accent); border: 1px solid var(--border-color); font-weight: 600; cursor: pointer; width: 100%;">
                    <option value="AND" ${currentOp === "AND" ? "selected" : ""}>E</option>
                    <option value="OR" ${currentOp === "OR" ? "selected" : ""}>OU</option>
                </select>
            `;
            
            const sel = container.querySelector(".cond-logical-op");
            sel.addEventListener("change", () => {
                const newOp = sel.value;
                document.getElementById("rule-operator").value = newOp;
                updateLogicalConnectiveDisplays();
            });
        }
    });
}

// MANAGER FORM: RULE CONDITIONS
function addConditionRow(attribute = "", operator = "=", value = "") {
    const row = document.createElement("div");
    row.className = "form-list-item";
    
    row.innerHTML = `
        <div class="logical-op-container" style="min-width: 70px;"></div>
        <input type="text" class="cond-attr flex-2" placeholder="Atributo" value="${attribute}" required>
        <select class="cond-op flex-1" style="min-width: 60px;">
            <option value="=" ${operator === "=" ? "selected" : ""}>=</option>
            <option value="!=" ${operator === "!=" ? "selected" : ""}>!=</option>
            <option value=">" ${operator === ">" ? "selected" : ""}>&gt;</option>
            <option value="<" ${operator === "<" ? "selected" : ""}>&lt;</option>
            <option value=">=" ${operator === ">=" ? "selected" : ""}>&gt;=</option>
            <option value="<=" ${operator === "<=" ? "selected" : ""}>&lt;=</option>
        </select>
        <input type="text" class="cond-val flex-2" placeholder="Valor" value="${value}" required>
        <button type="button" class="btn btn-danger btn-small btn-remove-cond">X</button>
    `;
    
    row.querySelector(".btn-remove-cond").addEventListener("click", () => {
        row.remove();
        updateLogicalConnectiveDisplays();
    });
    
    ruleConditionsList.appendChild(row);
    updateLogicalConnectiveDisplays();
}

// SAVE RULE FROM FORM
function saveRuleFromForm() {
    const id = document.getElementById("rule-id").value.trim();
    const name = document.getElementById("rule-name").value.trim();
    const desc = document.getElementById("rule-desc").value.trim();
    const priority = parseInt(document.getElementById("rule-priority").value) || 0;
    const cf = parseFloat(document.getElementById("rule-cf").value) || 1.0;
    
    const condRows = ruleConditionsList.querySelectorAll(".form-list-item");
    const conditions = [];
    condRows.forEach(row => {
        conditions.push({
            attribute: row.querySelector(".cond-attr").value.trim(),
            operator: row.querySelector(".cond-op").value,
            value: row.querySelector(".cond-val").value.trim()
        });
    });
    
    if (conditions.length === 0) {
        showToast("Por favor, adicione pelo menos uma condição para a regra.", "error");
        return;
    }
    
    const conclusion = {
        attribute: document.querySelector(".rule-conclusion-attr").value.trim(),
        value: document.querySelector(".rule-conclusion-val").value.trim()
    };
    
    const condition_operator = document.getElementById("rule-operator").value;
    
    const payload = { id, name, priority, description: desc, conditions, conclusion, condition_operator, cf };
    
    fetch("/api/kb/edit/rule", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showToast(`Regra '${id}' salva na base de conhecimento.`);
            // Reset form
            document.getElementById("rule-id").value = "";
            document.getElementById("rule-name").value = "";
            document.getElementById("rule-desc").value = "";
            document.getElementById("rule-priority").value = "0";
            document.getElementById("rule-cf").value = "1.0";
            ruleConditionsList.innerHTML = "";
            document.querySelector(".rule-conclusion-attr").value = "";
            document.querySelector(".rule-conclusion-val").value = "";
            // Reload metadata
            loadActiveKbInfo();
        } else {
            showToast("Erro ao salvar regra na base.", "error");
        }
    });
}

// SAVE QUESTION FROM FORM
function saveQuestionFromForm() {
    const attribute = document.getElementById("q-attribute").value.trim();
    const question = document.getElementById("q-text").value.trim();
    const optionsRaw = document.getElementById("q-options").value.trim();
    const minValStr = document.getElementById("q-min").value.trim();
    const maxValStr = document.getElementById("q-max").value.trim();
    
    const options = optionsRaw ? optionsRaw.split(",").map(o => o.trim()) : null;
    
    const min_val = minValStr ? parseFloat(minValStr) : null;
    const max_val = maxValStr ? parseFloat(maxValStr) : null;
    
    const payload = {
        attribute,
        question,
        options,
        range: (min_val !== null || max_val !== null) ? [min_val, max_val] : null
    };
    
    fetch("/api/kb/edit/question", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showToast(`Pergunta registrada com sucesso para o atributo '${attribute}'.`);
            // Reset form
            document.getElementById("q-attribute").value = "";
            document.getElementById("q-text").value = "";
            document.getElementById("q-options").value = "";
            document.getElementById("q-min").value = "";
            document.getElementById("q-max").value = "";
            // Reload metadata
            loadActiveKbInfo();
        } else {
            showToast("Erro ao salvar pergunta.", "error");
        }
    });
}

function deleteHypothesis(attr) {
    if (!confirm(`Deseja remover '${attr}' das hipóteses alvo?`)) return;
    fetch(`/api/kb/delete/hypothesis?attribute=${encodeURIComponent(attr)}`, { method: "POST" })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast(`Hipótese '${attr}' removida.`);
                loadActiveKbInfo();
            } else {
                showToast("Erro ao remover hipótese.", "error");
            }
        });
}
window.deleteHypothesis = deleteHypothesis;

function populateInitialFactsForm() {
    initialFactsFields.innerHTML = "";
    if (!kbInfo || !kbInfo.questions) {
        initialFactsSetup.style.display = "none";
        return;
    }
    
    const attributes = Object.keys(kbInfo.questions);
    if (attributes.length === 0) {
        initialFactsSetup.style.display = "none";
        return;
    }
    
    initialFactsSetup.style.display = "block";
    
    attributes.forEach(attr => {
        const grp = document.createElement("div");
        grp.className = "form-group";
        
        const label = document.createElement("label");
        label.textContent = kbInfo.questions[attr] || attr;
        grp.appendChild(label);
        
        const options = kbInfo.answer_options[attr];
        
        const wrapper = document.createElement("div");
        wrapper.style.display = "flex";
        wrapper.style.gap = "8px";
        wrapper.style.alignItems = "center";
        
        let control = null;
        if (options && options.length > 0) {
            const selectWrapper = document.createElement("div");
            selectWrapper.className = "select-wrapper";
            selectWrapper.style.flex = "2";
            selectWrapper.style.width = "100%";
            
            const sel = document.createElement("select");
            sel.className = "initial-fact-input";
            sel.setAttribute("data-attribute", attr);
            
            const emptyOpt = document.createElement("option");
            emptyOpt.value = "";
            emptyOpt.textContent = "(Não informado)";
            sel.appendChild(emptyOpt);
            
            options.forEach(opt => {
                const o = document.createElement("option");
                o.value = opt;
                o.textContent = opt;
                sel.appendChild(o);
            });
            selectWrapper.appendChild(sel);
            control = selectWrapper;
        } else {
            const inp = document.createElement("input");
            inp.type = "text";
            inp.className = "initial-fact-input";
            inp.style.flex = "2";
            inp.setAttribute("data-attribute", attr);
            inp.placeholder = "Deixe em branco se desconhecido";
            control = inp;
        }
        
        wrapper.appendChild(control);
        
        // Add CF selector
        const cfLabel = document.createElement("span");
        cfLabel.textContent = "CF:";
        cfLabel.style.fontSize = "11px";
        cfLabel.style.color = "var(--text-muted)";
        wrapper.appendChild(cfLabel);
        
        const cfInp = document.createElement("input");
        cfInp.type = "number";
        cfInp.className = "initial-fact-cf";
        cfInp.setAttribute("data-cf-attribute", attr);
        cfInp.style.flex = "1";
        cfInp.style.maxWidth = "80px";
        cfInp.style.padding = "4px 8px";
        cfInp.style.borderRadius = "4px";
        cfInp.style.background = "var(--bg-input)";
        cfInp.style.color = "var(--text-main)";
        cfInp.style.border = "1px solid var(--border-color)";
        cfInp.style.fontSize = "12px";
        cfInp.style.outline = "none";
        cfInp.min = "0";
        cfInp.max = "1";
        cfInp.step = "0.05";
        cfInp.value = "1.0";
        
        wrapper.appendChild(cfInp);
        
        grp.appendChild(wrapper);
        initialFactsFields.appendChild(grp);
    });
}

function loadRuleToForm(ruleId) {
    if (!kbInfo || !kbInfo.rules) return;
    const rule = kbInfo.rules.find(r => r.id === ruleId);
    if (!rule) return;

    // Switch tab to manager
    tabBtns.forEach(btn => {
        if (btn.getAttribute("data-tab") === "tab-manager") {
            btn.click();
        }
    });

    // Populate inputs
    document.getElementById("rule-id").value = rule.id;
    document.getElementById("rule-name").value = rule.name;
    document.getElementById("rule-desc").value = rule.description || "";
    document.getElementById("rule-priority").value = rule.priority;
    document.getElementById("rule-cf").value = rule.cf !== undefined ? rule.cf : 1.0;
    document.getElementById("rule-operator").value = rule.condition_operator || "AND";

    // Populate conditions
    ruleConditionsList.innerHTML = "";
    if (rule.conditions && rule.conditions.length > 0) {
        rule.conditions.forEach(cond => {
            addConditionRow(cond.attribute, cond.operator, cond.value);
        });
    }

    // Populate conclusion
    document.querySelector(".rule-conclusion-attr").value = rule.conclusion.attribute;
    document.querySelector(".rule-conclusion-val").value = rule.conclusion.value;

    showToast(`Regra '${ruleId}' carregada para edição.`);
}
window.loadRuleToForm = loadRuleToForm;

// DELETE QUESTION
function deleteQuestion(attr) {
    if (!confirm(`Deseja realmente excluir a pergunta do atributo '${attr}'?`)) return;
    fetch(`/api/kb/delete/question?attribute=${encodeURIComponent(attr)}`, { method: "POST" })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast(`Pergunta do atributo '${attr}' excluída.`);
                loadActiveKbInfo();
            } else {
                showToast("Erro ao excluir pergunta.", "error");
            }
        })
        .catch(() => {
            showToast("Erro ao comunicar com o servidor para excluir pergunta.", "error");
        });
}
window.deleteQuestion = deleteQuestion;
