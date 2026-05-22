import customtkinter as ctk
from tkinter import ttk  # Importación obligatoria para la tabla
from database import GestorBaseDatos


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AuditGradesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = GestorBaseDatos()
        self.profesor_actual = "PROF_001" 

        self.title("Audit-Grades Pro - UNEXCA")
        self.geometry("700x600")

        self.crear_interfaz_completa()

    def crear_interfaz_completa(self):
        # Título Principal
        self.lbl_titulo = ctk.CTkLabel(self, text="Sistema de Gestión y Auditoría de Notas", font=("Arial", 22, "bold"))
        self.lbl_titulo.pack(pady=15)

        # Sistema de Pestañas (Módulos)
        self.tabview = ctk.CTkTabview(self, width=650, height=450)
        self.tabview.pack(padx=20, pady=10)

        self.tabview.add("Registrar Nota (Create)")
        self.tabview.add("Modificar Nota (Update)")
        self.tabview.add("Log de Auditoría (Read)")

        self.construir_modulo_registro()
        self.construir_modulo_modificacion()
        self.construir_modulo_auditoria()

    # --- Módulo 1: Registro ---
    def construir_modulo_registro(self):
        tab = self.tabview.tab("Registrar Nota (Create)")
        
        self.reg_estudiante = ctk.CTkEntry(tab, placeholder_text="ID Estudiante (Ej: V-1234)", width=300)
        self.reg_estudiante.pack(pady=15)

        self.reg_materia = ctk.CTkEntry(tab, placeholder_text="Código de Materia", width=300)
        self.reg_materia.pack(pady=15)

        self.reg_nota = ctk.CTkEntry(tab, placeholder_text="Nota (0-20)", width=300)
        self.reg_nota.pack(pady=15)

        btn_guardar = ctk.CTkButton(tab, text="Registrar Calificación", command=self.accion_registrar)
        btn_guardar.pack(pady=20)

        self.lbl_msg_registro = ctk.CTkLabel(tab, text="", font=("Arial", 14))
        self.lbl_msg_registro.pack()

# --- Módulo 2: Modificación (Actualizado) ---
    def construir_modulo_modificacion(self):
        tab = self.tabview.tab("Modificar Nota (Update)")

        # Estilo para adaptar la tabla estándar al modo oscuro
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")

        # Zona de Búsqueda
        frame_busqueda = ctk.CTkFrame(tab, fg_color="transparent")
        frame_busqueda.pack(pady=5, fill="x", padx=20)
        
        self.entrada_busqueda = ctk.CTkEntry(frame_busqueda, placeholder_text="Buscar Estudiante o Materia...", width=400)
        self.entrada_busqueda.pack(side="left", padx=10)
        
        btn_buscar = ctk.CTkButton(frame_busqueda, text="Buscar", width=100, command=self.accion_buscar_notas)
        btn_buscar.pack(side="left")

        # Tabla de Datos (Treeview)
        columnas = ("id", "estudiante", "materia", "nota")
        self.tabla_notas = ttk.Treeview(tab, columns=columnas, show="headings", height=6)
        self.tabla_notas.heading("id", text="ID")
        self.tabla_notas.heading("estudiante", text="Estudiante")
        self.tabla_notas.heading("materia", text="Materia")
        self.tabla_notas.heading("nota", text="Nota Actual")
        
        self.tabla_notas.column("id", width=50, anchor="center")
        self.tabla_notas.column("estudiante", width=150, anchor="center")
        self.tabla_notas.column("materia", width=150, anchor="center")
        self.tabla_notas.column("nota", width=100, anchor="center")
        
        self.tabla_notas.pack(pady=10, padx=20, fill="x")
        
        # Evento: Al hacer clic en una fila, cargar datos
        self.tabla_notas.bind("<ButtonRelease-1>", self.seleccionar_fila)

        # Zona de Edición
        frame_edicion = ctk.CTkFrame(tab)
        frame_edicion.pack(pady=10, fill="x", padx=20)

        ctk.CTkLabel(frame_edicion, text="ID Seleccionado:").grid(row=0, column=0, padx=10, pady=10)
        self.mod_id_calificacion = ctk.CTkEntry(frame_edicion, state="disabled", width=100) # Solo lectura por seguridad
        self.mod_id_calificacion.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(frame_edicion, text="Nueva Nota:").grid(row=0, column=2, padx=10, pady=10)
        self.mod_nueva_nota = ctk.CTkEntry(frame_edicion, width=100)
        self.mod_nueva_nota.grid(row=0, column=3, padx=10, pady=10)

        btn_modificar = ctk.CTkButton(frame_edicion, text="Guardar Modificación", fg_color="darkred", hover_color="red", command=self.accion_modificar_tabla)
        btn_modificar.grid(row=0, column=4, padx=10, pady=10)

        self.lbl_msg_modificacion = ctk.CTkLabel(tab, text="", font=("Arial", 14))
        self.lbl_msg_modificacion.pack()

        # Cargar todos los datos al iniciar la pestaña
        self.accion_buscar_notas()

    # --- Nueva Lógica de Interacción para la Tabla ---

    def accion_buscar_notas(self):
        """ Llena la tabla con los registros de la base de datos. """
        criterio = self.entrada_busqueda.get()
        resultados = self.db.buscar_calificaciones(criterio)
        
        # Limpiar tabla actual
        for fila in self.tabla_notas.get_children():
            self.tabla_notas.delete(fila)
            
        # Insertar nuevos resultados
        for registro in resultados:
            self.tabla_notas.insert("", "end", values=registro)

    def seleccionar_fila(self, event):
        """ Captura los datos de la fila seleccionada y los pasa a los campos de edición. """
        item_seleccionado = self.tabla_notas.focus()
        if item_seleccionado:
            valores = self.tabla_notas.item(item_seleccionado, 'values')
            
            # Habilitar el campo ID temporalmente para escribir, luego volver a bloquearlo
            self.mod_id_calificacion.configure(state="normal")
            self.mod_id_calificacion.delete(0, 'end')
            self.mod_id_calificacion.insert(0, valores[0])
            self.mod_id_calificacion.configure(state="disabled")
            
            self.mod_nueva_nota.delete(0, 'end')
            self.mod_nueva_nota.insert(0, valores[3])

    def accion_modificar_tabla(self):
        """ Ejecuta la modificación usando el ID seleccionado. """
        # Leer el campo bloqueado
        self.mod_id_calificacion.configure(state="normal")
        id_calificacion = self.mod_id_calificacion.get()
        self.mod_id_calificacion.configure(state="disabled")
        
        nueva_nota = self.mod_nueva_nota.get()

        if not id_calificacion:
            self.lbl_msg_modificacion.configure(text="Error: Seleccione un registro de la tabla.", text_color="red")
            return

        exito, mensaje = self.db.modificar_nota(int(id_calificacion), nueva_nota, self.profesor_actual)
        
        color = "green" if exito else "red"
        self.lbl_msg_modificacion.configure(text=mensaje, text_color=color)
        
        if exito:
            self.mod_nueva_nota.delete(0, 'end')
            self.accion_buscar_notas() # Refrescar la tabla para mostrar el cambio

    # --- Módulo 3: Auditoría (US3.3) ---
    def construir_modulo_auditoria(self):
        tab = self.tabview.tab("Log de Auditoría (Read)")

        btn_actualizar = ctk.CTkButton(tab, text="Actualizar Datos de Auditoría", command=self.accion_cargar_auditoria)
        btn_actualizar.pack(pady=10)

        # Consola visual para mostrar los logs
        self.txt_auditoria = ctk.CTkTextbox(tab, width=600, height=350, state="disabled")
        self.txt_auditoria.pack(pady=10)

    # --- Lógica de Interacción ---

    def accion_registrar(self):
        estudiante = self.reg_estudiante.get()
        materia = self.reg_materia.get()
        nota = self.reg_nota.get()

        exito, mensaje = self.db.registrar_nota(estudiante, materia, nota, self.profesor_actual)
        
        color = "green" if exito else "red"
        self.lbl_msg_registro.configure(text=mensaje, text_color=color)
        
        if exito:
            self.reg_estudiante.delete(0, 'end')
            self.reg_materia.delete(0, 'end')
            self.reg_nota.delete(0, 'end')

    def accion_modificar(self):
        id_calificacion = self.mod_id_calificacion.get()
        nueva_nota = self.mod_nueva_nota.get()

        if not id_calificacion.isdigit():
            self.lbl_msg_modificacion.configure(text="Error: El ID de calificación debe ser un número entero.", text_color="red")
            return

        exito, mensaje = self.db.modificar_nota(int(id_calificacion), nueva_nota, self.profesor_actual)
        
        color = "green" if exito else "red"
        self.lbl_msg_modificacion.configure(text=mensaje, text_color=color)
        
        if exito:
            self.mod_id_calificacion.delete(0, 'end')
            self.mod_nueva_nota.delete(0, 'end')

    def accion_cargar_auditoria(self):
        registros = self.db.consultar_auditoria()
        
        self.txt_auditoria.configure(state="normal")
        self.txt_auditoria.delete("1.0", "end") # Limpiar pantalla
        
        if not registros:
            self.txt_auditoria.insert("end", "El log de auditoría está vacío. No se han detectado modificaciones.\n")
        else:
            encabezado = f"{'OP':<8} | {'ID_NOTA':<8} | {'PROFESOR':<10} | {'ANT':<5} | {'NVA':<5} | {'FECHA_HORA'}\n"
            self.txt_auditoria.insert("end", encabezado)
            self.txt_auditoria.insert("end", "-" * 70 + "\n")
            
            for reg in registros:
                linea = f"{reg[1]:<8} | {reg[2]:<8} | {reg[3]:<10} | {reg[4]:<5.1f} | {reg[5]:<5.1f} | {reg[6]}\n"
                self.txt_auditoria.insert("end", linea)
                
        self.txt_auditoria.configure(state="disabled")

if __name__ == "__main__":
    app = AuditGradesApp()
    app.mainloop()