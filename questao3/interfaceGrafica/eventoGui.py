import customtkinter as ctk
from .telaGui import TelaGui 

class EventView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller 
        self.facade = controller.facade

        # --- Layout Principal da Tela ---
        self.grid_columnconfigure((0, 1), weight=1) # Cria duas colunas de largura igual
        self.grid_rowconfigure(3, weight=1) # Permite que a área de texto se expanda

        # Botão para voltar ao menu principal
        btn_voltar = ctk.CTkButton(self, text="< Voltar ao Menu Principal", command=lambda: controller.show_frame(TelaGui))
        btn_voltar.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        
        # --- Frames para cada Secção ---
        self.criar_frame()
        self.cancelar_frame()
        self.listar_frame()
        self.pesquisa_frame()
        # Adicione aqui as chamadas para criar os outros frames...

        # --- Área de Saída de Texto ---
        self.output_textbox = ctk.CTkTextbox(self, font=("Arial", 14), wrap="word")
        self.output_textbox.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    # --- MÉTODOS PARA CONSTRUIR CADA FRAME ---

    def criar_frame(self):
        frame = ctk.CTkFrame(self, border_width=2)
        frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        frame.grid_columnconfigure(1, weight=1)

        label = ctk.CTkLabel(frame, text="Criar Evento", font=("Arial", 18))
        label.grid(row=0, column=0, columnspan=2, pady=10)

        ctk.CTkLabel(frame, text="Nome:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_nome_criar = ctk.CTkEntry(frame)
        self.entry_nome_criar.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(frame, text="Data:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_data_criar = ctk.CTkEntry(frame)
        self.entry_data_criar.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        btn = ctk.CTkButton(frame, text="Criar Evento", command=self.criar_evento) 
        btn.grid(row=3, column=1, padx=5, pady=10, sticky="w")

    def cancelar_frame(self):
        frame = ctk.CTkFrame(self, border_width=2)
        frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        frame.grid_columnconfigure(1, weight=1)

        label = ctk.CTkLabel(frame, text="Cancelar Evento", font=("Arial", 18))
        label.grid(row=0, column=0, columnspan=2, pady=10)

        ctk.CTkLabel(frame, text="Nome do Evento:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_nome_cancelar = ctk.CTkEntry(frame)
        self.entry_nome_cancelar.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        btn = ctk.CTkButton(frame, text="Cancelar Evento", command=self.cancelar_evento, fg_color="red") 
        btn.grid(row=2, column=1, padx=5, pady=10, sticky="w")

    def listar_frame(self):
        frame = ctk.CTkFrame(self, border_width=2)
        frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1) # Centralizar o botão

        label = ctk.CTkLabel(frame, text="Listar Eventos", font=("Arial", 18))
        label.pack(pady=10)
        
        btn = ctk.CTkButton(frame, text="Ver Todos os Eventos", command=self.listar_eventos)
        btn.pack(pady=10)

    def pesquisa_frame(self):
        frame = ctk.CTkFrame(self, border_width=2)
        frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        frame.grid_columnconfigure(1, weight=1)

        label = ctk.CTkLabel(frame, text="Criar Pesquisa", font=("Arial", 18))
        label.grid(row=0, column=0, columnspan=2, pady=10)

        ctk.CTkLabel(frame, text="Nome do Evento:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_evento_pesquisa = ctk.CTkEntry(frame)
        self.entry_evento_pesquisa.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(frame, text="Título da Pesquisa:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_titulo_pesquisa = ctk.CTkEntry(frame)
        self.entry_titulo_pesquisa.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        btn = ctk.CTkButton(frame, text="Criar Pesquisa", command=self.criar_pesquisa)
        btn.grid(row=3, column=1, padx=5, pady=10, sticky="w")

    # --- MÉTODOS DE LÓGICA (Callbacks dos Botões) ---

    def criar_evento(self):
        nome = self.entry_nome_criar.get()
        data = self.entry_data_criar.get()
        
        if not nome or not data:
            self.show_output("Erro: Nome e data são obrigatórios.")
            return

        try:
            # Lembre-se de refatorar facade.criar_evento() para aceitar argumentos
            # self.facade.criar_evento(nome, data) 
            self.show_output(f"Evento '{nome}' criado com sucesso!")
            self.entry_nome_criar.delete(0, 'end')
            self.entry_data_criar.delete(0, 'end')
        except Exception as e:
            self.show_output(f"Ocorreu um erro: {e}")
    
    def cancelar_evento(self):
        nome_evento = self.entry_nome_cancelar.get()
        if not nome_evento:
            self.show_output("Erro: É necessário o nome do evento para o cancelar.")
            return
        
        try:
            # Lembre-se de refatorar facade.cancelar_evento() para aceitar argumentos
            # self.facade.cancelar_evento(nome_evento)
            self.show_output(f"Evento '{nome_evento}' cancelado com sucesso!")
            self.entry_nome_cancelar.delete(0, 'end')
        except Exception as e:
            self.show_output(f"Ocorreu um erro: {e}")
    
    def listar_eventos(self):
        try:
            # Esta função na facade precisa de ser alterada para RETORNAR os dados,
            # em vez de os imprimir na consola.
            # lista_de_eventos = self.facade.listar_eventos()
            # self.show_output(lista_de_eventos)
            self.show_output("Simulação: Lista de eventos apareceria aqui.")
        except Exception as e:
            self.show_output(f"Ocorreu um erro: {e}")

    def criar_pesquisa(self):
        # Implemente a lógica aqui, similar a criar_evento
        self.show_output("Lógica para criar pesquisa ainda não implementada.")
    
    def show_output(self, message):
        """Função auxiliar para mostrar mensagens na caixa de texto."""
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.insert("1.0", message)

# Este bloco é importante para evitar erros de importação circular
EventView.__name__ = "EventView"