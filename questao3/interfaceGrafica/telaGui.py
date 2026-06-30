import customtkinter as ctk
from .eventoGui import EventoView 

class TelaGui(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ctk.CTkLabel(self, text="Menu Principal", font=("Arial", 24))
        label.pack(pady=20, padx=10)

        # Botões que substituem as opções do menu de texto
        botao_gerir_eventos = ctk.CTkButton(
            self,
            text="Gerir Eventos",
            command=lambda: controller.show_frame(EventoView)

        )
        botao_gerir_eventos.pack(pady=10)

        botao_gerir_participante = ctk.CTkButton( self, text="Gerir participantes",command = lambda: controller.show_frame(EventoView)) 
        botao_gerir_participante.pack(pady=10)

        botao_gerir_fornecedor = ctk.CTkButton(self,text = "Gerir fornecedores", command= lambda: controller.show_frame(FornecedorView) )
        botao_gerir_fornecedor.pack(pady=10)

        botao_gerir_financa = ctk.CTkButton(self, text= "Gerir finanças",command=lambda: controller.show_frame(FinancasView))
        botao_gerir_financa.pack(pady=10)

        botao_gerir_local = ctk.CTkButton(self, text= "Gerir locais", command= lambda: controller.show_frame(LocalView))
        botao_gerir_local.pack(pady=10)
       