import os
import sys
import threading
import uuid
import json
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# Adjust path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.knowledge_base import KnowledgeBase, validate_free_input, Fact, Rule, Condition, Conclusion
from core.inference_engine import InferenceEngine
from core.explanation import ExplanationEngine
from core.llm_client import GroqClient

app = FastAPI(title="K-RuleShell Web API", description="Generic Expert System Shell API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
DEMOS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demos")
active_kb: Optional[KnowledgeBase] = None
active_kb_filename: Optional[str] = None
llm_client = GroqClient()

class SessionState:
    def __init__(self, kb: KnowledgeBase):
        # Clone the KB to avoid cross-talk between concurrent sessions
        self.kb = KnowledgeBase.from_dict(kb.to_dict())
        self.engine = InferenceEngine(self.kb, ask_user_callback=self._ask_user_callback)
        self.explanation = ExplanationEngine(self.kb, self.engine)
        self.thread: Optional[threading.Thread] = None
        self.question_event = threading.Event()
        self.answer_event = threading.Event()
        
        self.current_attribute: Optional[str] = None
        self.current_question: Optional[str] = None
        self.current_options: Optional[List[str]] = None
        self.current_answer: Optional[str] = None
        self.current_cf: float = 1.0
        self.is_finished = False
        self.results: Dict[str, List[str]] = {}
        self.error_msg: Optional[str] = None
        self.thread: Optional[threading.Thread] = None

    def start(self, mode: str = "hybrid", target_hyp: Optional[str] = None):
        self.thread = threading.Thread(target=self._run_inference, args=(mode, target_hyp))
        self.thread.daemon = True
        self.thread.start()

    def _run_inference(self, mode: str, target_hyp: Optional[str]):
        try:
            if mode == "forward":
                self.engine.forward_chain()
                res = {}
                for hyp in self.kb.hypotheses:
                    val = self.kb.get_fact_value(hyp)
                    res[hyp] = [str(val)] if val is not None else []
                self.results = res
            elif mode == "backward":
                target = target_hyp or (self.kb.hypotheses[0] if self.kb.hypotheses else "")
                if not target:
                    raise ValueError("Nenhuma hipótese/meta alvo definida para encadeamento para trás.")
                self.engine.backward_chain(target)
                val = self.kb.get_fact_value(target)
                self.results = {target: [str(val)] if val is not None else []}
            else:  # hybrid
                self.results = self.engine.hybrid_chain(self.kb.hypotheses)
        except Exception as e:
            self.error_msg = str(e)
        finally:
            self.is_finished = True
            self.current_question = None
            self.current_attribute = None
            self.current_options = []
            # Make sure waiting API threads release
            self.question_event.set()
            self.answer_event.set()

    def _ask_user_callback(self, attr: str, question: str, options: list) -> Optional[str]:
        self.current_attribute = attr
        self.current_question = question
        self.current_options = options
        self.current_answer = None
        self.current_cf = 1.0
        
        self.question_event.set()
        self.answer_event.wait()
        self.answer_event.clear()
        
        # When user answers, inject the fact with CF
        if self.current_answer is not None:
            self.kb.assert_fact(attr, self.current_answer, source="user", cf=self.current_cf)
            return self.current_answer
        return None

    def submit_answer(self, answer: str, cf: float = 1.0) -> tuple[bool, str]:
        val_normalized, is_valid, err_msg = validate_free_input(self.kb, self.current_attribute, answer)
        if not is_valid:
            return False, err_msg
            
        self.current_answer = val_normalized
        self.current_cf = cf
        self.question_event.clear()
        
        # Release inference loop
        self.answer_event.set()
        
        # Wait a short timeout for the inference thread to set the next question or finish
        self.question_event.wait(timeout=0.2)
        return True, ""

# Active sessions storage
sessions: Dict[str, SessionState] = {}

# Pydantic schemas
class AnswerRequest(BaseModel):
    answer: str
    cf: float = 1.0

class StartSessionRequest(BaseModel):
    mode: str = "hybrid"  # "hybrid" | "forward" | "backward"
    target: Optional[str] = None
    initial_facts: Optional[Dict[str, str]] = None
    initial_cfs: Optional[Dict[str, float]] = None

class SaveRuleRequest(BaseModel):
    id: str
    name: str
    priority: int = 0
    description: str = ""
    conditions: List[dict]  # [{"attribute":..., "operator":..., "value":...}]
    conclusion: dict        # {"attribute":..., "value":...}
    condition_operator: str = "AND"
    cf: float = 1.0

class SaveQuestionRequest(BaseModel):
    attribute: str
    question: str
    options: Optional[List[str]] = None
    range: Optional[List[Optional[float]]] = None

# Helper to automatically load initial KB if available
def get_initial_kb():
    global active_kb, active_kb_filename
    if active_kb is not None:
        return active_kb
        
    # Try loading triagem_upa_kb.json by default if it exists
    default_path = os.path.join(DEMOS_DIR, "triagem_upa_kb.json")
    if os.path.exists(default_path):
        try:
            active_kb = KnowledgeBase.load(default_path)
            active_kb_filename = "triagem_upa_kb.json"
        except Exception:
            pass
    if active_kb is None:
        active_kb = KnowledgeBase(domain="generico")
        active_kb_filename = "generico"
    return active_kb

@app.get("/api/kb/export")
def export_kb():
    kb = get_initial_kb()
    return kb.to_dict()

# API Endpoints
@app.get("/api/kb/list")
def list_kbs():
    os.makedirs(DEMOS_DIR, exist_ok=True)
    files = [f for f in os.listdir(DEMOS_DIR) if f.endswith(".json")]
    return {"kbs": files}

@app.post("/api/kb/load")
def load_kb(filename: str):
    global active_kb, active_kb_filename
    path = os.path.join(DEMOS_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    try:
        active_kb = KnowledgeBase.load(path)
        active_kb_filename = filename
        return {"success": True, "domain": active_kb.domain}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar KB: {e}")

@app.post("/api/kb/new")
def new_kb(domain: str = "generico", description: str = ""):
    global active_kb, active_kb_filename
    active_kb = KnowledgeBase(domain=domain, description=description)
    active_kb_filename = f"{domain}.json"
    return {"success": True, "domain": active_kb.domain}

@app.post("/api/kb/upload")
async def upload_kb(file: UploadFile = File(...)):
    global active_kb, active_kb_filename
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Apenas arquivos .json são permitidos.")
    os.makedirs(DEMOS_DIR, exist_ok=True)
    path = os.path.join(DEMOS_DIR, file.filename)
    try:
        content = await file.read()
        data = json.loads(content.decode("utf-8"))
        # Validate format
        temp_kb = KnowledgeBase.from_dict(data)
        # Save file
        with open(path, "wb") as f:
            f.write(content)
        active_kb = temp_kb
        active_kb_filename = file.filename
        return {"success": True, "domain": active_kb.domain, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Arquivo JSON inválido ou mal-formatado: {e}")

@app.get("/api/kb/info")
def get_kb_info():
    kb = get_initial_kb()
    rules_summary = []
    for r in kb.rules.values():
        rules_summary.append({
            "id": r.id,
            "name": r.name,
            "priority": r.priority,
            "description": r.description,
            "conditions": [{"attribute": c.attribute, "operator": c.operator, "value": c.value} for c in r.conditions],
            "conclusion": {"attribute": r.conclusion.attribute, "value": r.conclusion.value}
        })
    
    return {
        "domain": kb.domain,
        "description": kb.description,
        "hypotheses": kb.hypotheses,
        "rules_count": len(kb.rules),
        "rules": rules_summary,
        "questions": kb.questions,
        "answer_options": kb.answer_options,
        "attribute_ranges": kb.attribute_ranges,
        "filename": active_kb_filename
    }

@app.post("/api/session/start")
def start_session(req: StartSessionRequest):
    kb = get_initial_kb()
    session_id = str(uuid.uuid4())
    state = SessionState(kb)
    
    # Assert any initial facts from frontend (especially for Forward Chaining)
    if req.initial_facts:
        for attr, val in req.initial_facts.items():
            if val is not None and str(val).strip() != "":
                val_normalized, is_valid, err_msg = validate_free_input(state.kb, attr, str(val))
                if is_valid:
                    cf_val = req.initial_cfs.get(attr, 1.0) if req.initial_cfs else 1.0
                    state.kb.add_initial_fact(attr, val_normalized, cf=cf_val)
                    
    sessions[session_id] = state
    state.start(req.mode, req.target)
    
    # Wait briefly for thread to initialize and trigger first question if any
    state.question_event.wait(timeout=0.1)
    
    return {"session_id": session_id}

@app.get("/api/session/status")
def get_session_status(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    s = sessions[session_id]
    
    # Wait for a question or finish
    if not s.is_finished and s.current_question is None:
        s.question_event.wait(timeout=0.05)
        
    return {
        "is_done": s.is_finished,
        "question": s.current_question,
        "attribute": s.current_attribute,
        "options": s.current_options,
        "results": s.results,
        "error": s.error_msg,
        "has_llm": llm_client.is_available()
    }

@app.post("/api/session/answer")
def session_answer(session_id: str = Query(...), req: AnswerRequest = None):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    state = sessions[session_id]
    if state.is_finished:
        raise HTTPException(status_code=400, detail="Sessão já finalizada.")
    if not state.question_event.is_set():
        raise HTTPException(status_code=400, detail="Nenhuma pergunta aguardando resposta.")
        
    cf_val = req.cf if req else 1.0
    success, err = state.submit_answer(req.answer, cf=cf_val)
    if not success:
        return {"success": False, "error": err}
    return {"success": True}

@app.get("/api/session/facts")
def get_session_facts(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    s = sessions[session_id]
    facts_list = []
    for attr, f in s.kb.working_memory.items():
        facts_list.append({
            "attribute": attr,
            "value": f.value,
            "cf": f.cf,
            "source": f.source,
            "rule_id": f.rule_id
        })
    return {"facts": facts_list}

@app.get("/api/session/why")
def get_why_explanation(session_id: str, attribute: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    s = sessions[session_id]
    explanation = s.explanation.why(attribute)
    
    natural_explanation = None
    if llm_client.is_available():
        natural_explanation = llm_client.explain_natural_language(explanation)
        
    return {
        "structured": explanation,
        "natural": natural_explanation
    }

@app.get("/api/session/how")
def get_how_explanation(session_id: str, attribute: str, value: Optional[str] = None):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    s = sessions[session_id]
    explanation = s.explanation.how(attribute, value)
    
    natural_explanation = None
    if llm_client.is_available():
        natural_explanation = llm_client.explain_natural_language(explanation)
        
    return {
        "structured": explanation,
        "natural": natural_explanation
    }

# Interactive editing APIs (Generic Editor functionality)
@app.post("/api/kb/edit/rule")
def edit_rule(req: SaveRuleRequest):
    kb = get_initial_kb()
    try:
        conditions = [Condition(c["attribute"], c["operator"], c["value"]) for c in req.conditions]
        conc_data = req.conclusion
        conclusion = Conclusion(conc_data["attribute"], conc_data["value"], cf=conc_data.get("cf", 1.0))
        rule = Rule(
            id=req.id,
            name=req.name,
            conditions=conditions,
            conclusion=conclusion,
            priority=req.priority,
            description=req.description,
            condition_operator=req.condition_operator,
            cf=req.cf
        )
        kb.add_rule(rule)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao salvar regra: {e}")

@app.post("/api/kb/delete/rule")
def delete_rule(rule_id: str):
    kb = get_initial_kb()
    success = kb.remove_rule(rule_id)
    return {"success": success}

@app.post("/api/kb/edit/question")
def edit_question(req: SaveQuestionRequest):
    kb = get_initial_kb()
    kb.register_question(req.attribute, req.question, req.options)
    if req.range and len(req.range) == 2:
        kb.register_attribute_range(req.attribute, req.range[0], req.range[1])
    return {"success": True}

@app.post("/api/kb/delete/question")
def delete_question(attribute: str):
    kb = get_initial_kb()
    success = kb.remove_question(attribute)
    return {"success": success}

@app.post("/api/kb/edit/hypothesis")
def edit_hypothesis(attribute: str):
    kb = get_initial_kb()
    kb.register_hypothesis(attribute)
    return {"success": True}

@app.post("/api/kb/delete/hypothesis")
def delete_hypothesis(attribute: str):
    kb = get_initial_kb()
    if attribute in kb.hypotheses:
        kb.hypotheses.remove(attribute)
        return {"success": True}
    return {"success": False}

@app.post("/api/kb/save-to-disk")
def save_to_disk(filename: Optional[str] = None):
    global active_kb_filename
    kb = get_initial_kb()
    target_name = filename or active_kb_filename or "knowledge_base.json"
    if not target_name.endswith(".json"):
        target_name += ".json"
    path = os.path.join(DEMOS_DIR, target_name)
    try:
        kb.save(path)
        active_kb_filename = target_name
        return {"success": True, "path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo no disco: {e}")

class IAParseRequest(BaseModel):
    text: str
    type: str  # "rules" | "questions"

@app.post("/api/ia/parse")
def parse_ia(req: IAParseRequest):
    if not llm_client.is_available():
        raise HTTPException(status_code=503, detail="Serviço de IA indisponível. Verifique as chaves de API.")
    
    kb = get_initial_kb()
    kb_rules = []
    for r in kb.rules.values():
        kb_rules.append(f"- [{r.id}] {r.name}: SE {r.conditions} ENTÃO {r.conclusion}")
        
    if req.type == "rules":
        current_kb_info = f"""
Domínio: {kb.domain}
Descrição: {kb.description}
Perguntas/Opções registradas: {kb.answer_options}
Hipóteses: {kb.hypotheses}
Regras cadastradas atualmente:
{chr(10).join(kb_rules)}
"""
        parsed = llm_client.parse_rules_from_natural_language(req.text, current_kb_info)
    else:
        current_kb_info = f"""
Domínio: {kb.domain}
Descrição: {kb.description}
Perguntas/Opções registradas atualmente: {kb.answer_options}
Limites numéricos atuais: {kb.attribute_ranges}
Hipóteses: {kb.hypotheses}
"""
        parsed = llm_client.parse_questions_from_natural_language(req.text, current_kb_info)
        
    if parsed is None:
        raise HTTPException(status_code=400, detail="Não foi possível estruturar os dados a partir do texto.")
        
    return {"data": parsed}

# Serve frontend files
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
