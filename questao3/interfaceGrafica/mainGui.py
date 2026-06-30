import customtkinter as ctk
from estruturais.facade import SistemaFacade
from .telaGui import TelaView


class App(ctk.CTk):
    def __init__(self, facade: SistemaFacade):
        super().__init__()
        self.facade = facade

        self.title("Sistema de Gestão de Eventos")
        self.geometry("800x600")

        # Configura o tema
        ctk.set_appearance_mode("System")  # "Dark", "Light"
        ctk.set_default_color_theme("blue")

        # Container principal para as "telas" (Frames)
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Inicia com a primeira tela (o menu principal)
        self.show_frame(TelaView)

    def show_frame(self, FrameClasse):
        # Limpa o frame antigo e mostra o novo
        for widget in self.container.winfo_children():
            widget.destroy()
        
        frame = FrameClasse(parent=self.container, controller=self)
        frame.grid(row=0, column=0, sticky="nsew")