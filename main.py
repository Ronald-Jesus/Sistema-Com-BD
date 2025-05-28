import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

def inicializar_banco():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pedidos (
        id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
        id_cliente INTEGER,
        produto TEXT,
        quantidade INTEGER,
        data TEXT,
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
    )
    ''')
    conn.commit()
    conn.close()

def inserir_cliente():
    nome = entry_nome.get()
    email = entry_email.get()
    if nome == "":
        messagebox.showerror("Erro", "Nome não pode estar vazio!")
        return
    try:
        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clientes (nome, email) VALUES (?, ?)", (nome, email))
        conn.commit()
        conn.close()
        listar_clientes()
        entry_nome.delete(0, tk.END)
        entry_email.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def editar_cliente():
    cliente_selecionado = tree_clientes.selection()
    if not cliente_selecionado:
        messagebox.showwarning("Aviso", "Selecione um cliente para editar.")
        return
    id_cliente = tree_clientes.item(cliente_selecionado)['values'][0]
    nome_novo = entry_nome.get()
    email_novo = entry_email.get()
    if nome_novo == "":
        messagebox.showerror("Erro", "Nome não pode estar vazio.")
        return
    try:
        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE clientes SET nome = ?, email = ? WHERE id_cliente = ?", (nome_novo, email_novo, id_cliente))
        conn.commit()
        conn.close()
        listar_clientes()
        entry_nome.delete(0, tk.END)
        entry_email.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def excluir_cliente():
    cliente_selecionado = tree_clientes.selection()
    if not cliente_selecionado:
        messagebox.showwarning("Aviso", "Selecione um cliente para excluir.")
        return
    id_cliente = tree_clientes.item(cliente_selecionado)['values'][0]
    confirm = messagebox.askyesno("Confirmação", "Deseja realmente excluir o cliente e seus pedidos?")
    if not confirm:
        return
    try:
        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pedidos WHERE id_cliente = ?", (id_cliente,))
        cursor.execute("DELETE FROM clientes WHERE id_cliente = ?", (id_cliente,))
        conn.commit()
        conn.close()
        listar_clientes()
        tree_pedidos.delete(*tree_pedidos.get_children())
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def listar_clientes():
    for item in tree_clientes.get_children():
        tree_clientes.delete(item)
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id_cliente, nome, email FROM clientes")
    for row in cursor.fetchall():
        tree_clientes.insert('', tk.END, values=row)
    conn.close()

def inserir_pedido():
    produto = entry_produto.get()
    quantidade = entry_quantidade.get()
    data = entry_data.get()
    try:
        cliente_selecionado = tree_clientes.selection()
        if not cliente_selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente primeiro.")
            return
        id_cliente = tree_clientes.item(cliente_selecionado)['values'][0]
        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO pedidos (id_cliente, produto, quantidade, data) VALUES (?, ?, ?, ?)",
                       (id_cliente, produto, int(quantidade), data))
        conn.commit()
        conn.close()
        entry_produto.delete(0, tk.END)
        entry_quantidade.delete(0, tk.END)
        entry_data.delete(0, tk.END)
        listar_pedidos_por_cliente(id_cliente)
    except ValueError:
        messagebox.showerror("Erro", "Quantidade deve ser um número inteiro.")
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def excluir_pedido():
    pedido_selecionado = tree_pedidos.selection()
    if not pedido_selecionado:
        messagebox.showwarning("Aviso", "Selecione um pedido para excluir.")
        return
    id_pedido = tree_pedidos.item(pedido_selecionado)['values'][0]
    confirm = messagebox.askyesno("Confirmação", "Deseja realmente excluir este pedido?")
    if not confirm:
        return
    try:
        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pedidos WHERE id_pedido = ?", (id_pedido,))
        conn.commit()
        conn.close()
        listar_pedidos_por_cliente()
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def listar_pedidos_por_cliente(id_cliente=None):
    for item in tree_pedidos.get_children():
        tree_pedidos.delete(item)
    if not id_cliente:
        cliente_selecionado = tree_clientes.selection()
        if not cliente_selecionado:
            return
        id_cliente = tree_clientes.item(cliente_selecionado)['values'][0]
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id_pedido, produto, quantidade, data FROM pedidos WHERE id_cliente = ?", (id_cliente,))
    for row in cursor.fetchall():
        tree_pedidos.insert('', tk.END, values=row)
    conn.close()

inicializar_banco()
root = tk.Tk()
root.title("Sistema de Clientes e Pedidos")
root.geometry("800x600")

frame_cliente = tk.LabelFrame(root, text="Cadastro de Cliente", padx=10, pady=10)
frame_cliente.pack(padx=10, pady=10, fill="x")

tk.Label(frame_cliente, text="Nome:").grid(row=0, column=0)
entry_nome = tk.Entry(frame_cliente)
entry_nome.grid(row=0, column=1)

tk.Label(frame_cliente, text="Email:").grid(row=1, column=0)
entry_email = tk.Entry(frame_cliente)
entry_email.grid(row=1, column=1)

btn_adicionar = tk.Button(frame_cliente, text="Adicionar", command=inserir_cliente)
btn_adicionar.grid(row=0, column=2, padx=5)
btn_editar = tk.Button(frame_cliente, text="Editar", command=editar_cliente)
btn_editar.grid(row=0, column=3, padx=5)
btn_excluir = tk.Button(frame_cliente, text="Excluir", command=excluir_cliente)
btn_excluir.grid(row=1, column=2, columnspan=2, padx=5)

frame_lista = tk.LabelFrame(root, text="Clientes", padx=10, pady=10)
frame_lista.pack(padx=10, pady=10, fill="both")

colunas = ("ID", "Nome", "Email")
tree_clientes = ttk.Treeview(frame_lista, columns=colunas, show="headings")
for col in colunas:
    tree_clientes.heading(col, text=col)
    tree_clientes.column(col, anchor="center")
tree_clientes.pack(fill="x")

frame_pedido = tk.LabelFrame(root, text="Cadastrar Pedido", padx=10, pady=10)
frame_pedido.pack(padx=10, pady=10, fill="x")

tk.Label(frame_pedido, text="Produto:").grid(row=0, column=0)
entry_produto = tk.Entry(frame_pedido)
entry_produto.grid(row=0, column=1)

tk.Label(frame_pedido, text="Quantidade:").grid(row=0, column=2)
entry_quantidade = tk.Entry(frame_pedido)
entry_quantidade.grid(row=0, column=3)

tk.Label(frame_pedido, text="Data:").grid(row=0, column=4)
entry_data = tk.Entry(frame_pedido)
entry_data.grid(row=0, column=5)

btn_pedido = tk.Button(frame_pedido, text="Adicionar Pedido", command=inserir_pedido)
btn_pedido.grid(row=0, column=6, padx=5)
btn_excluir_pedido = tk.Button(frame_pedido, text="Excluir Pedido", command=excluir_pedido)
btn_excluir_pedido.grid(row=0, column=7, padx=5)

frame_lista_pedidos = tk.LabelFrame(root, text="Pedidos do Cliente", padx=10, pady=10)
frame_lista_pedidos.pack(padx=10, pady=10, fill="both", expand=True)

colunas_pedidos = ("ID", "Produto", "Quantidade", "Data")
tree_pedidos = ttk.Treeview(frame_lista_pedidos, columns=colunas_pedidos, show="headings")
for col in colunas_pedidos:
    tree_pedidos.heading(col, text=col)
    tree_pedidos.column(col, anchor="center")
tree_pedidos.pack(fill="x")

def on_cliente_select(event):
    listar_pedidos_por_cliente()

tree_clientes.bind("<<TreeviewSelect>>", on_cliente_select)
    
listar_clientes()
root.mainloop()
